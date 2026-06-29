"""
ingest_all.py — 批量导入脚本

一键导入 Phase B 的 5 份测试文档。
运行一次即可，之后重启服务不需要重新导入（ChromaDB 会持久化数据）。

用法:
    cd phase-a-scratch/backend
    python ingest_all.py
"""
from pathlib import Path
from pipeline import RAGPipeline

# 5 份测试文档（来自 Phase B）
DOCUMENTS = [
    "员工手册.pdf",
    "IT安全管理制度.pdf",
    "产品手册-云办公平台.docx",
    "财务报销制度.docx",
    "新员工入职指南.txt",
]

# 文档目录（相对于 backend 目录）
DOCUMENTS_DIR = Path(__file__).parent.parent.parent / "phase-b-dify" / "documents"


def main():
    print("=" * 60)
    print("  企业文档知识库 — 批量文档导入")
    print("=" * 60)
    print()

    # 检查文档目录
    if not DOCUMENTS_DIR.exists():
        print(f"❌ 文档目录不存在: {DOCUMENTS_DIR}")
        return

    # 初始化 RAG 引擎
    print("🔧 正在初始化 RAG 引擎...")
    pipeline = RAGPipeline()
    print()

    # 逐一导入
    total_chunks = 0
    success = 0
    failed = 0

    for doc_name in DOCUMENTS:
        file_path = DOCUMENTS_DIR / doc_name

        if not file_path.exists():
            print(f"  ⚠️  跳过（文件不存在）: {doc_name}")
            failed += 1
            continue

        try:
            result = pipeline.ingest_document(str(file_path))
            print(f"  ✅ {doc_name}")
            print(f"     格式: {result['format']} | 分片: {result['chunk_count']} | 字符: {result['text_length']}")
            total_chunks += result["chunk_count"]
            success += 1
        except Exception as e:
            print(f"  ❌ {doc_name}: {e}")
            failed += 1

    print()
    print("=" * 60)
    print(f"  导入完成: 成功 {success} 份, 失败 {failed} 份, 共 {total_chunks} 个分片")
    print("=" * 60)

    # 显示文档列表
    docs = pipeline.list_documents()
    if docs:
        print(f"\n当前知识库有 {len(docs)} 份文档:")
        for d in docs:
            print(f"  📄 {d['doc_id']}: {d['chunk_count']} chunks")


if __name__ == "__main__":
    main()
