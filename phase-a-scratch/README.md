# Phase A — 手写 RAG 知识库问答系统

从零实现的 RAG（检索增强生成）企业文档问答系统，不依赖 Dify/LangChain 等框架。

## 架构

```
用户浏览器 (frontend/index.html)
       ↓ HTTP
backend/main.py (FastAPI)
       ↓
backend/pipeline.py (RAG 编排器)
       ↓
  ┌────┼────┬──────┬──────┐
  ↓    ↓     ↓      ↓      ↓
parser chunker embedder retriever generator
```

## 快速开始

### 1. 配置 API Key

```bash
cd phase-a-scratch/backend
# 编辑 .env 文件，填入你的通义千问 API Key
# DASHSCOPE_API_KEY=sk-你的key
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 导入文档

```bash
cd phase-a-scratch/backend
python ingest_all.py
```

这会导入 Phase B 的 5 份测试文档（员工手册、IT安全制度、产品手册、财务报销制度、入职指南）。

### 4. 启动服务

```bash
uvicorn backend.main:app --reload --port 8000
```

### 5. 打开浏览器

访问 `http://localhost:8000/` 进入问答界面。

API 文档: `http://localhost:8000/docs`

## API 接口

| 方法 | 路径 | 功能 |
|------|------|------|
| `GET` | `/` | 前端界面 |
| `POST` | `/api/upload` | 上传文档 |
| `POST` | `/api/ask` | 提问 |
| `GET` | `/api/documents` | 文档列表 |
| `DELETE` | `/api/documents/{id}` | 删除文档 |

## 测试

```bash
cd phase-a-scratch/backend
python test_pipeline.py
```

用 10 道测试题验证系统，目标准确率 ≥ 85%。

## 模块说明

| 文件 | 职责 |
|------|------|
| `config.py` | 读取 .env 配置 |
| `parser.py` | PDF/DOCX/TXT → 纯文本 |
| `chunker.py` | 文本 → 重叠分片 |
| `embedder.py` | 文本 → 向量（通义千问 API） |
| `vector_store.py` | ChromaDB 增删查 |
| `bm25.py` | BM25 关键词检索 |
| `retriever.py` | 混合检索（向量+BM25） |
| `rewriter.py` | 口语 → 书面语 |
| `prompts.py` | 提示词模板 |
| `generator.py` | LLM 生成答案 |
| `pipeline.py` | 串联所有模块 |
| `main.py` | FastAPI 入口 |
| `ingest_all.py` | 批量导入脚本 |
| `test_pipeline.py` | 端到端测试 |

## 技术栈

- Python 3.11 + FastAPI
- ChromaDB（向量库，本地持久化）
- 通义千问 qwen3-max（LLM）
- 通义千问 text-embedding-v3（Embedding）
- BM25（关键词检索，rank-bm25 + jieba）
