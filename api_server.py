import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from dotenv import load_dotenv
load_dotenv()
import requests
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from functools import lru_cache
from fastapi import FastAPI, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field
from middleware import add_request_logging
from dependencies import get_embeddings, get_current_user
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from auth import create_access_token
from starlette.websockets import WebSocketState

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
if not SILICONFLOW_API_KEY:
    raise ValueError("❌ 未找到 SILICONFLOW_API_KEY！请检查 .env 文件。")
llm = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY, temperature=0)

# ==================== 模型加载（依赖注入） ====================
@lru_cache()
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="C:\\Users\\asus\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
    )

# ==================== FastAPI 应用 ====================
app = FastAPI(title="AI客服API")
# 如果 static 目录不存在就创建
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
app.middleware("http")(add_request_logging)

class UserMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)

def create_knowledge_agent(embeddings):
    """每次请求时重新创建包含最新检索器的Agent"""
    vectorstore = Chroma(persist_directory="./ecommerce_db", embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    @tool
    def search_faq(query: str) -> str:
        """搜索电商客服知识库"""
        docs = retriever.invoke(query)
        if not docs:
            return "未找到相关信息。"
        return "\n\n".join([f"[来源{i+1}] {d.page_content}" for i, d in enumerate(docs)])

    return create_agent(
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

def log_chat_to_db(user_message: str, agent_reply: str):
    """后台任务：将聊天记录保存到数据库"""
    import sqlite3
    from datetime import datetime
    conn = sqlite3.connect("customer_service.db")
    conn.execute(
        "INSERT INTO chat_logs (user_question, agent_reply) VALUES (?, ?)",
        (user_message, agent_reply)
    )
    conn.commit()
    conn.close()
# ==================== 多模态接口 ====================

class ImageAnalysisRequest(BaseModel):
    image_url: str = Field(..., min_length=1, description="图片的URL地址")
    product_type: str = Field(default="商品", description="商品类型描述，如'陶瓷水杯'、'太阳镜'")

def analyze_product_image(image_url: str, product_type: str) -> str:
    """调用多模态模型分析商品图片"""
    prompt = f"""请仔细查看这张{product_type}的图片，从以下方面分析：

1. 商品/包装是否有明显的破损、裂纹、划痕？
2. 如果有瑕疵，具体在什么位置？严重程度如何？
3. 根据常见的电商退换货政策，这种情况是否应该允许退货？
4. 如果是客服，你会给客户什么建议？

请用中文回答，语气专业但友善。"""

    response = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "nex-agi/Nex-N2-Pro",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ],
            "temperature": 0
        }
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"多模态模型调用失败：{response.text}")
    
    return response.json()["choices"][0]["message"]["content"]


@app.post("/analyze-image")
def analyze_image(
    request: ImageAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """上传商品图片URL，让AI判断是否有瑕疵并给出客服建议"""
    try:
        result = analyze_product_image(request.image_url, request.product_type)
        return {"analysis": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败：{str(e)}")
    
@app.post("/token")
def login(username: str, password: str):
    """简单认证：用户名和密码均为 'admin' 时签发 Token"""
    if username == "admin" and password == "admin":
        token = create_access_token(username)
        return {"access_token": token, "token_type": "bearer"}
    return {"error": "用户名或密码错误"}

@app.post("/chat")
def chat(
    user_input: UserMessage,
    background_tasks: BackgroundTasks,
    embeddings=Depends(get_embeddings),
    current_user: str = Depends(get_current_user)
):
    try:
        agent = create_knowledge_agent(embeddings)
        result = agent.invoke({"messages": [{"role": "user", "content": user_input.message}]})
        reply = result["messages"][-1].content
        
        # 把保存操作扔到后台，不阻塞返回
        background_tasks.add_task(log_chat_to_db, user_input.message, reply)
        
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"服务暂时不可用，请稍后重试。错误信息：{str(e)}"}
    
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, embeddings=Depends(get_embeddings)):
    """WebSocket 端点：支持文字对话和图片分析"""
    await websocket.accept()
    agent = create_knowledge_agent(embeddings)
    
    try:
        while True:
            user_message = await websocket.receive_text()
            
            # 判断是否为图片分析请求（消息格式：ANALYZE_IMAGE:图片URL|商品类型）
            if user_message.startswith("ANALYZE_IMAGE:"):
                parts = user_message.replace("ANALYZE_IMAGE:", "").split("|")
                image_url = parts[0].strip()
                product_type = parts[1].strip() if len(parts) > 1 else "商品"
                
                try:
                    analysis_result = analyze_product_image(image_url, product_type)
                    await websocket.send_text(f"📊 **图片分析结果**：\n{analysis_result}")
                except Exception as e:
                    await websocket.send_text(f"❌ 图片分析失败：{str(e)}")
            
            else:
                # 普通文字对话
                result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
                reply = result["messages"][-1].content
                await websocket.send_text(reply)
    
    except WebSocketDisconnect:
        print("客户端断开了 WebSocket 连接")
        
@app.get("/health")
def health_check():
    return {"status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)