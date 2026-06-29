"""
vector_store.py — ChromaDB 向量库封装

ChromaDB 是轻量级向量数据库，支持本地持久化（无需 Docker）。
这里把它封装成 VectorStore 类，提供增删查等基本操作。

向量数据库的作用：
  存储文档分片 + 对应的向量，支持"语义相似度搜索"。
  比如搜"发工资时间"，能匹配到"薪资发放日期"（意思相近但用词不同）。

核心类: VectorStore
"""
import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings
from embedder import embed_texts, embed_single


# ChromaDB 集合名称（相当于关系数据库的"表"）
COLLECTION_NAME = "enterprise_docs"


class VectorStore:
    """
    ChromaDB 向量库封装。

    用法:
        store = VectorStore("./chroma_data")
        store.add_chunks("doc_001", chunks)
        results = store.search("查询文本", top_k=3)
        store.delete_document("doc_001")
        docs = store.list_documents()
    """

    def __init__(self, persist_dir=None):
        """
        初始化向量库。

        参数:
            persist_dir: 数据持久化目录，默认为配置中的值
        """
        persist_dir = persist_dir or settings.chroma_persist_dir

        # 创建持久化客户端（数据存到本地磁盘，重启不丢失）
        self._client = chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # 获取或创建集合
        # ChromaDB 默认使用余弦距离（all-MiniLM-L6-v2 的嵌入函数会被我们覆盖）
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # 使用余弦距离
        )

    def add_chunks(self, doc_id, chunks):
        """
        将一个文档的所有分片存入向量库。

        流程：文本 → 嵌入向量 → 存入 ChromaDB

        参数:
            doc_id: 文档唯一 ID（如文件名+时间戳的 hash）
            chunks: 分片列表，每个含 content、index、char_start、char_end

        返回:
            int: 存入的分片数量
        """
        if not chunks:
            return 0

        # 1. 提取所有分片文本
        texts = [c["content"] for c in chunks]

        # 2. 批量获取嵌入向量
        vectors = embed_texts(texts)

        # 3. 生成唯一 ID 和元数据
        ids = []
        metadatas = []
        documents = []

        for i, chunk in enumerate(chunks):
            # 每个分片一个唯一 ID
            chunk_id = f"{doc_id}_{chunk.get('index', i)}"
            ids.append(chunk_id)

            # 元数据：用于溯源和过滤
            metadatas.append({
                "doc_id": doc_id,
                "chunk_index": chunk.get("index", i),
                "char_start": chunk.get("char_start", 0),
                "char_end": chunk.get("char_end", 0),
            })

            # 原始文本
            documents.append(chunk["content"])

        # 4. 存入 ChromaDB
        self._collection.add(
            ids=ids,
            embeddings=vectors,
            documents=documents,
            metadatas=metadatas,
        )

        return len(chunks)

    def search(self, query, top_k=None):
        """
        向量相似度搜索。

        参数:
            query: 查询文本
            top_k: 返回结果数，默认用配置值

        返回:
            list[dict]: 按相似度降序排列的结果
            每项: {content, metadata, score}
        """
        top_k = top_k or settings.top_k

        # 获取查询向量
        query_vector = embed_single(query)

        # ChromaDB 查询
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, self._collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        # 格式化结果
        formatted = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                distance = results["distances"][0][i]

                # 余弦距离 → 余弦相似度: similarity = 1 - distance
                # 余弦距离范围 [0, 2]，所以相似度范围 [-1, 1]
                # 我们 clamp 到 [0, 1]
                score = 1.0 - distance
                score = max(0.0, min(1.0, score))

                formatted.append({
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": round(score, 4),
                })

        return formatted

    def delete_document(self, doc_id):
        """
        删除某个文档的所有分片。

        参数:
            doc_id: 要删除的文档 ID

        返回:
            int: 删除的分片数量
        """
        # 找到该文档的所有分片
        existing = self._collection.get(
            where={"doc_id": doc_id},
            include=["metadatas"],
        )

        if not existing["ids"]:
            return 0

        # 删除
        self._collection.delete(ids=existing["ids"])
        return len(existing["ids"])

    def list_documents(self):
        """
        列出所有已导入的文档摘要。

        返回:
            list[dict]: 每项 {doc_id, chunk_count}
        """
        # 获取所有数据
        all_data = self._collection.get(include=["metadatas"])

        if not all_data["ids"]:
            return []

        # 按 doc_id 分组统计
        doc_stats = {}
        for meta in all_data["metadatas"]:
            doc_id = meta.get("doc_id", "unknown")
            if doc_id not in doc_stats:
                doc_stats[doc_id] = {"doc_id": doc_id, "chunk_count": 0}
            doc_stats[doc_id]["chunk_count"] += 1

        return list(doc_stats.values())

    def get_all_chunks(self):
        """
        获取所有分片（用于重建 BM25 索引）。

        返回:
            list[dict]: 所有分片，每项含 content 和 metadata
        """
        all_data = self._collection.get(
            include=["documents", "metadatas"]
        )

        if not all_data["ids"]:
            return []

        chunks = []
        for i in range(len(all_data["ids"])):
            chunks.append({
                "content": all_data["documents"][i],
                "metadata": all_data["metadatas"][i],
            })

        return chunks

    def count(self):
        """返回总分片数"""
        return self._collection.count()


# ── 快速测试 ──
if __name__ == "__main__":
    import tempfile
    import os

    # 用临时目录测试
    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(tmpdir)

        # 模拟添加分片
        test_chunks = [
            {"content": "年假5天", "index": 0, "char_start": 0, "char_end": 4},
            {"content": "迟到扣50元", "index": 1, "char_start": 5, "char_end": 11},
            {"content": "密码12位", "index": 2, "char_start": 12, "char_end": 17},
        ]

        n = store.add_chunks("test_doc", test_chunks)
        print(f"添加了 {n} 个分片")

        print(f"\n总文档数: {len(store.list_documents())}")
        print(f"总片数: {store.count()}")

        # 搜索
        results = store.search("休假", top_k=2)
        print(f"\n搜索 '休假':")
        for r in results:
            print(f"  分数: {r['score']:.4f} | {r['content']}")
