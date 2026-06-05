from fastapi import FastAPI
from pydantic import BaseModel
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ==================== 初始化 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

llm = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY, temperature=0)

embeddings = HuggingFaceEmbeddings(
    model_name="C:\\Users\\asus\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)
vectorstore = Chroma(persist_directory="./ecommerce_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def search_faq(query: str) -> str:
    """搜索电商客服知识库"""
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join([f"[来源{i+1}] {d.page_content}" for i, d in enumerate(docs)])

agent = create_agent(
    model=llm,
    tools=[search_faq],
    system_prompt="""你是一个专业的电商客服专员。

工作方式：
1. 如果用户是问候，直接友好回应。
2. 如果是业务问题（退换货、物流、支付等），使用 search_faq 工具检索知识库回答。
3. 如果知识库没有覆盖，诚实告知。
4. 回答简洁、专业，使用"您"称呼用户。

用中文回答。""",
)

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI客服API")

# 定义请求体格式
from pydantic import BaseModel, Field

class UserMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

@app.post("/chat")
def chat(user_input: UserMessage):
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": user_input.message}]})
        reply = result["messages"][-1].content
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"服务暂时不可用，请稍后重试。错误信息：{str(e)}"}

@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "running"}

# ==================== 启动说明 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)