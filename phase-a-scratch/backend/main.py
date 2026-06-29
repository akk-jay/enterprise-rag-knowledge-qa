"""
main.py — FastAPI 应用程序入口

提供 REST API 接口，连接前端页面和后端 RAG 引擎。

启动方式:
    cd phase-a-scratch/backend
    uvicorn main:app --reload --port 8000

API 文档:
    启动后访问 http://localhost:8000/docs 查看 Swagger UI
"""
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from pipeline import RAGPipeline

# ── 创建应用 ──
app = FastAPI(
    title="企业文档知识库问答系统",
    description="基于 RAG 技术的企业文档智能问答 API",
    version="1.0.0",
)

# 允许跨域（开发阶段前端可能在不同端口）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 初始化 RAG 引擎 ──
# 在模块加载时初始化（uvicorn --reload 模式下每次热重载会重新创建）
print("🚀 正在初始化 RAG 引擎...")
pipeline = RAGPipeline()
docs = pipeline.list_documents()
print(f"✅ 引擎就绪，已加载 {len(docs)} 份文档")
if docs:
    for d in docs:
        print(f"   📄 {d['doc_id']}: {d['chunk_count']} chunks")


# ── 数据模型 ──

class AskRequest(BaseModel):
    """提问请求"""
    question: str = Field(..., min_length=1, description="用户问题")


class AskResponse(BaseModel):
    """提问响应"""
    answer: str
    sources: list
    rewritten_query: str
    used_fallback: bool


class IngestResponse(BaseModel):
    """文档导入响应"""
    status: str
    doc_id: str
    filename: str
    format: str
    chunk_count: int
    text_length: int


class DocInfo(BaseModel):
    """文档信息"""
    doc_id: str
    chunk_count: int


# ── API 端点 ──

@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "企业文档知识库问答系统",
        "version": "1.0.0",
    }


@app.get("/api/documents", response_model=list[DocInfo])
async def list_documents():
    """列出所有已导入的文档"""
    docs = pipeline.list_documents()
    return [DocInfo(**d) for d in docs]


@app.post("/api/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    上传并导入文档。

    支持格式: PDF (.pdf), Word (.docx), 纯文本 (.txt)
    """
    # 验证文件扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {ext}。支持: PDF, DOCX, TXT",
        )

    # 保存上传的文件到临时目录
    upload_dir = Path("./uploads")
    upload_dir.mkdir(exist_ok=True)

    temp_path = upload_dir / file.filename
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {e}")

    # 导入 RAG 引擎
    try:
        result = pipeline.ingest_document(str(temp_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档导入失败: {e}")

    return IngestResponse(
        status="ok",
        doc_id=result["doc_id"],
        filename=result["filename"],
        format=result["format"],
        chunk_count=result["chunk_count"],
        text_length=result["text_length"],
    )


@app.post("/api/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """提问（RAG 问答的核心接口）"""
    try:
        result = pipeline.ask_question(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答处理失败: {e}")

    return AskResponse(**result)


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除指定文档"""
    count = pipeline.delete_document(doc_id)
    if count == 0:
        raise HTTPException(status_code=404, detail=f"文档不存在: {doc_id}")
    return {"status": "ok", "deleted_chunks": count}


# ── 前端页面 ──
frontend_dir = Path(__file__).parent.parent / "frontend"
_frontend_html = None

def _get_frontend_html():
    """缓存式读取前端 HTML"""
    global _frontend_html
    if _frontend_html is None and frontend_dir.exists():
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            _frontend_html = index_path.read_text(encoding="utf-8")
    return _frontend_html


@app.get("/ui")
async def ui_page():
    """前端界面"""
    html = _get_frontend_html()
    if html is None:
        return {"error": "前端文件未找到，请确认 frontend/index.html 存在"}
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html)


@app.get("/")
async def root_page():
    """根路径重定向到前端"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/ui")


# ── 启动入口 ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
