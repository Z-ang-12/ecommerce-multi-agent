# Multi-Agent 电商客服系统

## 项目简介
一个基于 LangChain + DeepSeek + ChromaDB 构建的 Multi-Agent 电商客服系统。
三个 Agent 分工协作，实现意图分类、知识库检索、知识盲区自动检测与更新建议。

## 技术栈
- 大模型：DeepSeek-chat
- 框架：LangChain Agent
- 向量数据库：ChromaDB
- Embedding：all-MiniLM-L6-v2
- 架构：Multi-Agent 协作（分类师 + 客服专员 + 知识更新建议师）

## 架构设计
- Agent 1（意图分类师）：判断用户问题类型，输出分类标签
- Agent 2（客服专员）：基于知识库检索结果，生成专业回复
- Agent 3（知识更新建议师）：检测知识库盲区，自动生成 Q&A 更新条目

## 核心功能
- 智能意图分类（问候/退货/物流/支付/发票/非业务）
- RAG 知识库检索（退换货政策、物流查询、支付发票等）
- 知识库盲区自动检测与更新建议
- 完整日志追踪，每次决策可追溯

## 技术亮点
- Multi-Agent 协作架构，各 Agent 职责分离，可独立维护
- 知识库自我进化闭环：检测盲区 → 生成建议 → 人工审核 → 更新知识库
- 多层兜底机制：Agent 判断 + 代码层校验，确保盲区不遗漏

## 使用方法
1. 克隆本仓库
2. 创建虚拟环境并安装依赖：`pip install -r requirements.txt`
3. 创建 `.env` 文件，填入 `DEEPSEEK_API_KEY=Key`
4. 运行：`python multi_agent_v2.py`

## 项目演进路径
- V1：单工具天气 Agent
- V2：多工具生活助手（天气+美食+记忆）
- V3：RAG 增强型助手
- V4：Agentic RAG 智能路由
- V5：Multi-Agent 协作系统（当前项目）

## 作者
GitHub: [Z-ang-12]