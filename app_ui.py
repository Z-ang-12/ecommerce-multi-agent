import gradio as gr
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from sqlalchemy import create_engine, Column, Integer, Text, DateTime, func
from sqlalchemy.orm import declarative_base, Session

# 初始化数据库引擎
engine = create_engine("sqlite:///customer_service.db", echo=False)
Base = declarative_base()

class ChatLog(Base):
    __tablename__ = "chat_logs"
    id = Column(Integer, primary_key=True)
    user_question = Column(Text, nullable=False)
    agent_reply = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# ==================== 初始化知识库和Agent ====================
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
5. 回答末尾可以适当引导用户继续提问。

用中文回答。""",
)
# ==================== 定义保存记录函数 ====================
def save_chat(user_question, agent_reply):
    """用ORM保存聊天记录到数据库"""
    session = Session(engine)
    log = ChatLog(user_question=user_question, agent_reply=agent_reply)
    session.add(log)
    session.commit()
    session.close()
# ==================== 定义Gradio聊天函数 ====================
def chat_with_agent(message, history):
    if not message.strip():
        return ""
    result = agent.invoke({"messages": [{"role": "user", "content": message}]})
    reply = result["messages"][-1].content
    save_chat(message, reply)  # ← 新增这行
    return reply

# ==================== 启动Gradio界面 ====================
demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="🤖 AI电商客服助手",
    description="我是您的专属AI客服，可以帮您解答退换货、物流、支付等问题。请在下方输入您的问题。",
    examples=["我想退货，怎么操作？", "物流好几天没更新了怎么办？", "你们支持哪些支付方式？", "收到的商品有损坏怎么办？"],
    
)

if __name__ == "__main__":
    demo.launch(share=True)