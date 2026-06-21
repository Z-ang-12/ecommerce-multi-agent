# Multi-Agent 电商客服系统

## 项目简介
一个基于 LangChain + DeepSeek + ChromaDB 构建的 Multi-Agent 电商客服系统。三个 Agent 分工协作，实现意图分类、知识库检索、知识盲区自动检测与更新建议。配备 Gradio 网页聊天界面、SQLite 业务数据库和 SQLAlchemy ORM，支持 Docker 容器化部署和 GitHub Actions 自动构建推送。

## 技术栈
- **大模型**：DeepSeek-chat
- **Agent 框架**：LangChain（Multi-Agent 协作）
- **向量数据库**：ChromaDB（知识库语义检索）
- **业务数据库**：SQLite + SQLAlchemy ORM（聊天记录存储与统计分析）
- **前端界面**：Gradio（网页聊天界面，支持公网链接分享）
- **后端 API**：FastAPI + Uvicorn
- **容器化部署**：Docker + GitHub Actions + 阿里云容器镜像仓库
- **安全实践**：环境变量管理 API Key、参数化查询防 SQL 注入、.gitignore 防泄露

## 架构设计

系统由三个 Agent 分工协作：

| Agent | 职责 | 输入 → 输出 |
|:---|:---|:---|
| **Agent 1：意图分类师** | 判断用户问题类型，输出分类标签 | 用户消息 → 分类标签（问候/退货/物流/支付/发票/非业务） |
| **Agent 2：客服专员** | 基于意图分类结果，检索知识库并生成专业回复 | 用户消息 + 意图标签 → 客服回复 |
| **Agent 3：知识更新建议师** | 检测知识库盲区，自动生成 Q&A 更新条目 | 盲区问题 → Q&A 更新建议 |

用户提问
↓
Agent 1（意图分类师）判断问题类型
↓
Agent 2（客服专员）检索知识库 → 生成回复
↓
如果知识库未覆盖 → Agent 3（知识更新建议师）自动生成更新建议


## 核心功能
- **智能意图分类**：自动识别问候、退货、物流、支付、发票、非业务等6种问题类型
- **RAG 知识库检索**：基于退换货政策、物流规则、支付方式等FAQ进行语义检索
- **知识库自我进化**：检测到知识盲区时自动生成 Q&A 格式的更新建议，系统具备持续学习能力
- **Gradio 网页界面**：一键启动聊天窗口，支持公网链接分享给客户试用
- **对话记录持久化**：自动存入 SQLite 数据库，支持历史查询和统计分析
- **FastAPI 服务化**：将 Agent 包装为 RESTful API，可通过 HTTP 请求调用
- **Docker 一键部署**：支持本地构建、阿里云镜像仓库推送、GitHub Actions 自动构建

## 使用方法

## 方式一：Gradio 网页界面（推荐）
bash
 pip install -r requirements.txt
 python app_ui.py

浏览器访问 http://127.0.0.1:7860。如需公网链接，将最后一行改为 demo.launch(share=True)。

## 方式二：FastAPI 接口
 bash
 python api_server.py
 浏览器访问 http://localhost:8000/docs 查看 Swagger 文档并测试 API。

### 方式三：Docker 部署
bash
docker pull crpi-3xramxlts8n8u77t.cn-guangzhou.personal.cr.aliyuncs.com/ai-agent123/ecommerce-multi-agent:latest
docker run -p 8000:8000 --env-file .env crpi-3xramxlts8n8u77t.cn-guangzhou.personal.cr.aliyuncs.com/ai-agent123/ecommerce-multi-agent:latest

### 项目演进路径
本项目是 AI Agent 开发能力从 0 到 1 的完整演进记录：

V1：单工具天气 Agent（学习 API 调用）

V2：多工具生活助手（天气+美食+记忆）

V3：RAG 增强型助手（向量数据库语义检索）

V4：Agentic RAG 智能路由（自主判断是否需要检索）

V5：Multi-Agent 协作系统（三 Agent 分工）

V6：FastAPI 服务化 + Docker 容器化 + GitHub Actions 自动构建

V7：Gradio 前端界面 + SQLite 业务数据库 + SQLAlchemy ORM

### 作者
GitHub: [Z-ang-12]

