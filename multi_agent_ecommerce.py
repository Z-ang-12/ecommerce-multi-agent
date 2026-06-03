import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
import logging

# 配置日志
logger = logging.getLogger('multi_agent')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler('multi_agent.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

from dotenv import load_dotenv
load_dotenv()

from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ==================== 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("❌ 错误：未找到API Key！请检查 .env 文件。")

llm = ChatDeepSeek(model="deepseek-chat", api_key=DEEPSEEK_API_KEY, temperature=0)

# ==================== 初始化知识库（复用已有） ====================
embeddings = HuggingFaceEmbeddings(
    model_name="C:\\Users\\asus\\.cache\\huggingface\\hub\\models--sentence-transformers--all-MiniLM-L6-v2\\snapshots\\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)
vectorstore = Chroma(persist_directory="./ecommerce_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def search_faq(query: str) -> str:
    """搜索电商客服知识库，获取退换货政策、物流查询、支付发票等信息。"""
    docs = retriever.invoke(query)
    if not docs:
        return "未找到相关信息。"
    return "\n\n".join([f"[来源{i+1}] {d.page_content}" for i, d in enumerate(docs)])

# ==================== Agent 1: 意图分类师 ====================
classifier_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="""你是一个意图分类专家。阅读用户的消息，输出**一个**最准确的分类标签。

标签只能是以下之一：问候、退货、物流、支付、发票、非业务。

示例：
用户："你好啊" → 问候
用户："我要退货" → 退货
用户："物流怎么不更新" → 物流
用户："今天天气" → 非业务

只输出标签，不要解释。""",
)

# ==================== Agent 2: 客服专员 ====================
service_agent = create_agent(
    model=llm,
    tools=[search_faq],
    system_prompt="""你是一个专业的电商客服专员。

工作方式：
1. 阅读用户的原始消息和已经识别出的意图分类标签。
2. 如果意图是"问候"，直接友好回应。
3. 如果意图是"退货"、"物流"、"支付"、"发票"等业务相关，使用 search_faq 工具检索知识库，基于检索结果回答。
4. 如果意图是"非业务"，礼貌告知你只处理店铺业务，并引导用户询问购物相关问题。
5. 回答简洁、专业，使用"您"称呼用户。

用中文回答。""",
)

# ==================== 编排函数 ====================
def handle_message(user_input: str) -> str:
    # 第一步：意图分类
    result1 = classifier_agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    intent = result1["messages"][-1].content.strip()
    logger.info(f"意图分类结果：{intent}")

    # 第二步：客服专员基于意图生成回复
    combined_input = f"用户消息：{user_input}\n意图分类：{intent}"
    result2 = service_agent.invoke({"messages": [{"role": "user", "content": combined_input}]})
    return result2["messages"][-1].content

# ==================== 主程序 ====================
logger.info("🤖 Multi-Agent 电商客服已就绪！")
print("输入 '退出' 结束对话。")

while True:
    user_input = input("\n👤 用户：")
    if user_input.lower() == "退出":
        logger.info("对话结束。")
        break
    response = handle_message(user_input)
    print(f"🤖 客服：{response}")