#!/bin/bash
# ============================================================
#  企业文档知识库问答系统 — 一键安装启动脚本
#  用法: bash setup.sh
# ============================================================
set -e

echo "============================================"
echo "  企业文档知识库问答系统 — 一键安装"
echo "============================================"
echo ""

# 1. 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ 请先安装 Python 3.11+"
    echo "   https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
echo "✅ Python: $($PYTHON --version)"

# 2. 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
cd phase-a-scratch
$PYTHON -m pip install -r requirements.txt -q
cd ..
echo "✅ 依赖安装完成"

# 3. 配置 API Key
if [ ! -f phase-a-scratch/backend/.env ]; then
    echo ""
    echo "⚙️  配置 API Key..."
    cp phase-a-scratch/backend/.env.example phase-a-scratch/backend/.env
    echo ""
    echo "⚠️  请在 phase-a-scratch/backend/.env 中填入你的 API Key:"
    echo "   DASHSCOPE_API_KEY=sk-你的key"
    echo ""
    echo "   免费注册: https://dashscope.aliyun.com"
    echo ""
    read -p "已配置好 API Key？按回车继续... "
else
    echo "✅ .env 已存在，跳过配置"
fi

# 4. 导入文档
echo ""
echo "📄 导入测试文档..."
cd phase-a-scratch/backend
$PYTHON ingest_all.py
cd ../..

# 5. 启动
echo ""
echo "============================================"
echo "  🚀 启动服务..."
echo "  访问: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo "  按 Ctrl+C 停止"
echo "============================================"
cd phase-a-scratch/backend
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port 8000
