# Multi-Agent 电商客服系统

## 项目简介
一个基于 LangChain + DeepSeek + ChromaDB 构建的 Multi-Agent 电商客服系统。三个 Agent 分工协作，实现意图分类、知识库检索、知识盲区自动检测与更新建议。配备 Gradio 网页聊天界面、SQLite 业务数据库和 SQLAlchemy ORM，支持 Docker 容器化部署和 GitHub Actions 自动构建推送。

## 技术栈
- **大模型**：DeepSeek-chat
- **多模态模型**：硅基流动 Nex-N2-Pro
- **Agent 框架**：LangChain（Multi-Agent 协作）
- **向量数据库**：ChromaDB（知识库语义检索）
- **业务数据库**：SQLite + SQLAlchemy ORM（聊天记录存储与统计分析）
- **后端 API**：FastAPI + Uvicorn（HTTP + WebSocket）
- **认证**：JWT（python-jose）
- **前端界面**：原生 HTML/CSS/JS + WebSocket 实时聊天
- **容器化部署**：Docker + GitHub Actions + 阿里云容器镜像仓库 + 阿里云 ECS

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

## API 接口全览

| 接口 | 协议 | 认证 | 功能 |
|:---|:---|:---|:---|
| `POST /token` | HTTP | 无 | 获取 JWT Token |
| `POST /chat` | HTTP | JWT | 文字客服问答 |
| `POST /analyze-image` | HTTP | JWT | 商品瑕疵图片分析 |
| `WS /ws/chat` | WebSocket | 无 | 实时文字对话 + 图片分析 |
| `GET /health` | HTTP | 无 | 健康检查 |

## 核心功能
- **Multi-Agent 协作**：三个 Agent 分工明确，各司其职
- **智能意图分类**：自动识别问候、退货、物流、支付、发票、非业务等类型
- **RAG 知识库检索**：基于 ChromaDB 的语义检索，精准匹配 FAQ
- **知识库自我进化**：检测盲区时自动生成 Q&A 更新建议
- **FastAPI 全栈后端**：中间件日志、依赖注入、JWT 认证、后台任务
- **WebSocket 实时通信**：一次连接，持续对话，支持文字和图片双模式
- **多模态图片分析**：用户上传商品照片，AI 自动识别瑕疵并给出退货建议
- **原生聊天界面**：HTML/CSS/JS 构建，WebSocket 直连后端
- **Docker 一键部署**：GitHub Actions 自动构建 + 阿里云 ECS 公网访问

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
docker run -d -p 8000:8000 \
  -e DEEPSEEK_API_KEY=deepseek的key \
  -e SILICONFLOW_API_KEY=硅基流动key \
  crpi-3xramxlts8n8u77t.cn-guangzhou.personal.cr.aliyuncs.com/ai-agent123/ecommerce-multi-agent:latest

### 方式四：访问公网部署
text
http://你的公网IP:8000/docs          # Swagger API 文档
http://你的公网IP:8000/static/chat.html  # 实时聊天界面

### 项目演进路径
本项目是 AI Agent 开发能力从 0 到 1 的完整演进记录：
V1：单工具天气 Agent

V2：多工具生活助手

V3：RAG 增强型助手

V4：Agentic RAG 智能路由

V5：Multi-Agent 协作系统

V6：FastAPI 服务化 + Docker 容器化

V7：WebSocket 实时通信 + JWT 认证 + 多模态 + 云部署

### 作者
GitHub: [Z-ang-12]

