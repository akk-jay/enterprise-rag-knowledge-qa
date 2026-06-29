# 企业文档知识库问答 Agent

基于 RAG（检索增强生成）技术的企业级文档知识库问答系统。

## 项目结构

- `phase-b-dify/` - Dify 平台实现（RAG 工作流）
- `phase-a-scratch/` - 手写代码实现（后续）
- `notes/` - 学习笔记

## 快速开始

### 环境要求
- Docker + Dify
- Python 3.x
- 国内大模型 API Key（DeepSeek / 通义千问）

### 阶段 B：Dify 平台

1. 启动 Dify：`docker compose up -d`（在 dify/docker 目录）
2. 访问 http://localhost
3. 将 `phase-b-dify/documents/` 下的文档上传至 Dify 知识库
4. 按 `phase-b-dify/dify-workflow-config.md` 配置工作流
5. 使用 `phase-b-dify/test-questions.md` 验证效果

### 阶段 A：手写实现（待开发）

Python + FastAPI + Chroma 从零实现 RAG。
