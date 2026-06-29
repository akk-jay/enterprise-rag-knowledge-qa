"""
pipeline.py — RAG 流程编排器

把所有模块串联起来，提供两个核心操作:
  1. ingest_document() — 导入文档（解析 → 分片 → 嵌入 → 存储）
  2. ask_question()    — 回答问题（改写 → 检索 → 生成）

这是整个系统的"总指挥"，API 层只调用这两个方法。
"""
import hashlib
import time
from pathlib import Path

from config import settings
from parser import parse_document
from chunker import chunk_text
from vector_store import VectorStore
from bm25 import BM25Index
from retriever import Retriever
from rewriter import rewrite_query
from generator import generate_answer
from prompts import FALLBACK_ANSWER


class RAGPipeline:
    """
    RAG 流程编排器。

    用法:
        pipeline = RAGPipeline()
        pipeline.ingest_document("/path/to/doc.pdf")
        result = pipeline.ask_question("公司年假有几天？")
    """

    def __init__(self):
        """初始化所有组件"""
        # 向量库（持久化到本地磁盘）
        self.vector_store = VectorStore()

        # BM25 关键词索引（内存中，启动时从向量库重建）
        self.bm25_index = BM25Index()
        self._rebuild_bm25_index()

        # 混合检索器
        self.retriever = Retriever(self.vector_store, self.bm25_index)

    # ── 文档导入 ──

    def ingest_document(self, file_path):
        """
        导入一份文档：解析 → 分片 → 存储。

        参数:
            file_path: 文档文件路径

        返回:
            dict {
                "doc_id": "文档唯一ID",
                "filename": "文件名",
                "format": "pdf/docx/txt",
                "chunk_count": 分片数,
                "text_length": 原文总字符数
            }
        """
        file_path = Path(file_path)

        # 1. 解析文档
        parsed = parse_document(str(file_path))

        # 2. 生成文档唯一 ID（基于文件名 + 时间戳）
        doc_id = _make_doc_id(parsed["filename"])

        # 3. 分片
        chunks = chunk_text(
            parsed["text"],
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        # 4. 把文档信息写入每个分片的元数据（用于最终答案溯源）
        for chunk in chunks:
            if "metadata" not in chunk:
                chunk["metadata"] = {}
            chunk["metadata"]["filename"] = parsed["filename"]
            chunk["metadata"]["format"] = parsed["format"]

        # 5. 存入向量库（自动嵌入 + 存储）
        self.vector_store.add_chunks(doc_id, chunks)

        # 6. 重建 BM25 索引（因为新增了分片）
        self._rebuild_bm25_index()

        return {
            "doc_id": doc_id,
            "filename": parsed["filename"],
            "format": parsed["format"],
            "chunk_count": len(chunks),
            "text_length": len(parsed["text"]),
        }

    # ── 问答 ──

    def ask_question(self, question):
        """
        回答问题：改写 → 检索 → 生成。

        参数:
            question: 用户的自然语言问题

        返回:
            dict {
                "answer": "AI 生成的答案",
                "sources": [{"content": "...", "score": 0.92, "filename": "..."}, ...],
                "rewritten_query": "改写后的查询",
                "used_fallback": false
            }
        """
        # 1. 查询改写（口语 → 书面语）
        rewritten = rewrite_query(question)

        # 2. 混合检索
        retrieved = self.retriever.retrieve(
            rewritten,
            top_k=settings.top_k,
            threshold=settings.similarity_threshold,
        )

        # 3. 判断是否有有效检索结果
        if not retrieved:
            # 兜底：没有找到相关内容
            return {
                "answer": FALLBACK_ANSWER,
                "sources": [],
                "rewritten_query": rewritten,
                "used_fallback": True,
            }

        # 4. 提取来源信息
        sources = []
        for r in retrieved:
            sources.append({
                "content": r["content"],
                "score": r["score"],
                "filename": r.get("metadata", {}).get("filename", "未知文档"),
                "chunk_index": r.get("metadata", {}).get("chunk_index", 0),
            })

        # 5. LLM 生成答案
        answer = generate_answer(question, retrieved)

        return {
            "answer": answer,
            "sources": sources,
            "rewritten_query": rewritten,
            "used_fallback": False,
        }

    # ── 文档管理 ──

    def list_documents(self):
        """列出所有已导入的文档"""
        return self.vector_store.list_documents()

    def delete_document(self, doc_id):
        """
        删除文档及其所有分片。

        返回:
            int: 删除的分片数
        """
        count = self.vector_store.delete_document(doc_id)
        if count > 0:
            self._rebuild_bm25_index()
        return count

    # ── 内部方法 ──

    def _rebuild_bm25_index(self):
        """从向量库中取出所有分片，重建 BM25 索引"""
        all_chunks = self.vector_store.get_all_chunks()
        if all_chunks:
            self.bm25_index.build_index(all_chunks)


def _make_doc_id(filename):
    """生成文档唯一 ID"""
    raw = f"{filename}_{time.time()}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]


# ── 快速测试 ──
if __name__ == "__main__":
    import sys

    pipeline = RAGPipeline()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "ingest" and len(sys.argv) > 2:
            # python pipeline.py ingest <文件路径>
            result = pipeline.ingest_document(sys.argv[2])
            print(f"✓ 已导入: {result['filename']}")
            print(f"  格式: {result['format']}")
            print(f"  分片数: {result['chunk_count']}")
            print(f"  总字符: {result['text_length']}")

        elif command == "ask" and len(sys.argv) > 2:
            # python pipeline.py ask <问题>
            result = pipeline.ask_question(sys.argv[2])
            print(f"改写查询: {result['rewritten_query']}")
            print(f"兜底模式: {result['used_fallback']}")
            print(f"来源数: {len(result['sources'])}")
            print(f"\n--- 答案 ---")
            print(result["answer"])
            if result["sources"]:
                print(f"\n--- 来源 ---")
                for s in result["sources"]:
                    print(f"  [{s['score']:.2f}] {s['filename']}")

        elif command == "list":
            docs = pipeline.list_documents()
            print(f"已导入 {len(docs)} 份文档:")
            for d in docs:
                print(f"  {d['doc_id']}: {d['chunk_count']} 个分片")

        elif command == "delete" and len(sys.argv) > 2:
            count = pipeline.delete_document(sys.argv[2])
            print(f"✓ 已删除 {count} 个分片")

    else:
        print("用法:")
        print("  python pipeline.py ingest <文件路径>")
        print("  python pipeline.py ask <问题>")
        print("  python pipeline.py list")
        print("  python pipeline.py delete <文档ID>")
