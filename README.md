# 企业文档知识库问答 Agent

基于 RAG（检索增强生成）技术的企业级文档知识库问答系统。

## 项目概述

针对企业内部文档管理分散、信息检索效率低的痛点，基于 RAG 技术搭建垂直领域知识库问答系统。支持上传 PDF/Word/TXT 文档，AI 自动解析文档内容，实现精准问答与文档总结功能，降低人工查阅成本。

## 项目结构

```
企业问答知识库/
├── README.md                          # 项目说明
├── phase-b-dify/                      # Phase B: Dify 平台实现
│   ├── dify-workflow-config.md        # Dify 工作流配置（7 节点）
│   ├── prompts/                       # Prompt 模板
│   │   ├── system-prompt.md           # 系统提示词（4 道防线）
│   │   └── user-prompt.md             # 用户提示词模板
│   ├── documents/                     # 测试文档集（5 份）
│   │   ├── 员工手册.pdf               # 含考勤/休假/薪酬/行为规范
│   │   ├── IT安全管理制度.pdf          # IT 安全规范
│   │   ├── 产品手册-云办公平台.docx     # 产品使用手册
│   │   ├── 财务报销制度.docx           # 财务报销流程
│   │   ├── 新员工入职指南.txt          # 入职流程说明
│   │   └── 生成*.py                   # 文档生成脚本
│   ├── test-questions.md              # 10 道测试题
│   └── test-results.md                # 测试结果记录
├── phase-a-scratch/                   # Phase A: 手写代码实现
│   ├── README.md                      # Phase A 说明
│   ├── requirements.txt               # Python 依赖
│   ├── backend/                       # 后端模块
│   │   ├── main.py                    # FastAPI 应用入口
│   │   ├── pipeline.py                # RAG 流程编排器
│   │   ├── config.py                  # 配置中心
│   │   ├── parser.py                  # 文档解析（PDF/DOCX/TXT）
│   │   ├── chunker.py                 # 智能文本分片
│   │   ├── embedder.py                # Embedding API 客户端
│   │   ├── vector_store.py            # ChromaDB 向量库封装
│   │   ├── bm25.py                    # BM25 关键词检索
│   │   ├── retriever.py               # 混合检索引擎
│   │   ├── rewriter.py                # 查询改写
│   │   ├── prompts.py                 # 提示词模板
│   │   ├── generator.py               # LLM 答案生成
│   │   ├── ingest_all.py              # 批量导入脚本
│   │   └── test_pipeline.py           # 端到端测试
│   └── frontend/                      # 前端
│       └── index.html                 # 单页 Web 界面
├── notes/                             # 学习笔记
│   └── rag-notes.md                   # RAG 核心概念笔记
├── 各流程解释/                         # 流程说明文档
│   ├── RAG切片策略及解释.txt           # 分片策略详解
│   ├── dify工作流编排.txt              # 工作流设计说明
│   └── prompt规范模板.txt              # Prompt 模板说明
└── docs/                              # 设计文档
    └── superpowers/
        ├── specs/                     # 设计规格说明
        └── plans/                     # 实现计划
```

## 技术架构

```
用户浏览器 (frontend/index.html)
       ↓ HTTP
backend/main.py (FastAPI)
       ↓
backend/pipeline.py (RAG 编排器)
       ↓
  ┌────┼────┬──────┬──────┬──────────┐
  ↓    ↓     ↓      ↓      ↓          ↓
parser chunker embedder retriever generator
                      ↓
              ┌───────┴───────┐
              ↓               ↓
       vector_store        bm25
         (ChromaDB)    (rank-bm25 + jieba)
```

## 快速开始

### 环境要求

- Python 3.11+
- Docker + Dify（Phase B）
- 通义千问 API Key（DashScope）

### Phase B: Dify 平台

1. 启动 Dify：`docker compose up -d`（在 dify/docker 目录）
2. 访问 http://localhost
3. 将 `phase-b-dify/documents/` 下的文档上传至 Dify 知识库
4. 按 `phase-b-dify/dify-workflow-config.md` 配置工作流
5. 使用 `phase-b-dify/test-questions.md` 验证效果

### Phase A: 手写实现

```bash
# 1. 安装依赖
cd phase-a-scratch
pip install -r requirements.txt

# 2. 配置 API Key
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 DASHSCOPE_API_KEY

# 3. 导入文档
cd backend
python ingest_all.py

# 4. 启动服务
uvicorn main:app --reload --port 8000

# 5. 打开浏览器
# 访问 http://localhost:8000
```

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| `GET` | `/` | 前端界面 |
| `POST` | `/api/upload` | 上传文档 |
| `POST` | `/api/ask` | 提问（RAG 核心接口） |
| `GET` | `/api/documents` | 文档列表 |
| `DELETE` | `/api/documents/{id}` | 删除文档 |

## RAG 核心流程

```
文档上传 → 解析 → 分片 → 嵌入 → 存储 → [用户提问] → 查询改写 → 混合检索 → 生成答案
```

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| chunk_size | 500 | 每块文本大小 |
| chunk_overlap | 100 | 块间重叠大小 |
| Top-K | 3 | 检索返回条数 |
| 相似度阈值 | 0.7 | 过滤低相关片段 |
| 向量权重 | 0.7 | 混合检索向量侧权重 |
| BM25 权重 | 0.3 | 混合检索关键词侧权重 |
| Temperature | 0 | LLM 生成确定性 |

### Prompt 四道防线

1. **角色限定** — "你是一个企业知识库问答助手"
2. **范围限定** — "仅根据参考文档内容回答"
3. **相似度过滤** — 低于 0.7 分的片段直接丢弃
4. **诚实约定** — 不知道就说不知道，不编造

## 项目成果

- 系统完成开发并部署至本地环境
- 支持 3 类文档格式（PDF/Word/TXT）上传与问答
- 答案准确率达 85%+，文档总结关键信息覆盖率达 90%+
- 动态分片策略相比固定分片检索命中率提升约 15%

## 技术栈

- **LLM**: 通义千问 qwen3-max
- **Embedding**: 通义千问 text-embedding-v3
- **向量库**: ChromaDB（本地持久化）
- **关键词检索**: BM25 (rank-bm25 + jieba)
- **Web 框架**: FastAPI + Uvicorn
- **文档解析**: PyMuPDF + python-docx
- **前端**: 原生 HTML/CSS/JS（单页应用）
- **平台**: Dify（Phase B）
