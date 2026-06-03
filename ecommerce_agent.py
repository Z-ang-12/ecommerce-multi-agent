import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
import logging

# 配置日志
logger = logging.getLogger('ecommerce_agent')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler('ecommerce_agent.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

from dotenv import load_dotenv
load_dotenv()

import json
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==================== 1. 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logger.error("❌ 未找到API Key！请检查 .env 文件。")
    raise ValueError("❌ 错误：未找到API Key！请检查 .env 文件。")

# ==================== 2. 初始化知识库 ====================
logger.info("📚 正在加载客服知识库...")

loader = TextLoader("ecommerce_faq.txt", encoding="utf-8")
documents = loader.load()
logger.info(f"✅ 加载完成，共 {len(documents)} 篇文档")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
logger.info(f"✅ 切分完成，共 {len(chunks)} 个文本块")

embeddings = HuggingFaceEmbeddings(
    model_name="C:\\Users\\asus\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./ecommerce_db"
)
logger.info(f"✅ 向量数据库已创建")

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ==================== 3. 客服知识库检索工具 ====================
@tool
def search_faq(query: str) -> str:
    """
    搜索电商客服知识库，获取退换货政策、物流查询、支付发票、常见问题等信息。
    当用户咨询售后政策、退款流程、物流状态等问题时使用此工具。
    输入应为用户的自然语言问题。
    """
    try:
        docs = retriever.invoke(query)
        if not docs:
            return "知识库中未找到相关信息。建议转接人工客服。"
        results = []
        for i, doc in enumerate(docs):
            results.append(f"[来源{i+1}] {doc.page_content}")
        return "\n\n".join(results)
    except Exception as e:
        logger.error(f"知识库搜索失败：{str(e)}")
        return f"知识库搜索失败，请稍后重试。"

# ==================== 4. 创建客服Agent ====================
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key=DEEPSEEK_API_KEY,
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=[search_faq],
    system_prompt="""你是一个专业的电商客服专员，负责回答用户的咨询。

工作方式：
1. 先判断用户问题是否与店铺业务相关（退换货、物流、支付、发票、订单等）。
2. 如果相关，使用 search_faq 工具搜索知识库，基于检索结果回答。
3. 如果用户只是问候（如"你好"），直接友好回应，不需要检索。
4. 如果知识库里没有相关内容，诚实告知并建议用户联系人工客服。
5. 回答要简洁、礼貌、专业，使用"您"来称呼用户。

用中文回答。""",
)

# ==================== 5. 主程序 ====================
logger.info("\n🎧 电商客服Agent已就绪！")
logger.info("输入 '退出' 结束对话。")
logger.info("您可以问：退货政策、物流查询、发票开具等问题。")

while True:
    user_input = input("\n👤 用户：")

    if user_input.lower() == "退出":
        logger.info("👋 客服对话结束。")
        break

    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    response = result["messages"][-1].content
    print(f"🤖 客服：{response}")