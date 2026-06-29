"""
retriever.py — 混合检索器

RAG 系统的核心检索逻辑。

单一检索方式的局限:
  - 纯向量检索：可能漏掉精确关键词匹配（如"年假" vs "带薪休假"）
  - 纯关键词检索：无法理解语义相似（如"发工资" vs "薪资发放"）

混合检索 = 向量检索(0.7) + BM25关键词检索(0.3)
  两者互补，取长补短。

核心类: Retriever
"""
import numpy as np
from config import settings


class Retriever:
    """
    混合检索器——融合向量检索和 BM25 关键词检索。

    用法:
        retriever = Retriever(vector_store, bm25_index)
        results = retriever.retrieve("公司年假有几天？", top_k=3)

    返回的结果中，每个片段包含:
      - content: 文本内容
      - score: 综合分数 (0-1)
      - vector_score: 向量相似度分数
      - bm25_score: BM25 关键词分数
      - metadata: 来源信息
    """

    def __init__(self, vector_store, bm25_index):
        """
        参数:
            vector_store: VectorStore 实例
            bm25_index: BM25Index 实例
        """
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.vector_weight = settings.vector_weight  # 默认 0.7
        self.bm25_weight = settings.bm25_weight      # 默认 0.3

    def retrieve(self, query, top_k=None, threshold=None):
        """
        执行混合检索。

        流程:
          1. 向量检索（语义相似）
          2. BM25 检索（关键词匹配）
          3. 分数归一化
          4. 加权合并
          5. 排序 + 过滤

        参数:
            query: 查询文本
            top_k: 返回结果数（默认用配置值）
            threshold: 相似度阈值，低于此值的结果丢弃

        返回:
            list[dict]: 按综合分数降序排列的结果
        """
        top_k = top_k or settings.top_k
        threshold = threshold or settings.similarity_threshold

        # ── 第1步: 向量检索 ──
        vector_results = self.vector_store.search(query, top_k=top_k)

        # ── 第2步: BM25 关键词检索 ──
        bm25_results = self.bm25_index.search(query, top_k=top_k)

        # ── 第3步: 两边结果归一化 ──
        vector_results = _normalize_scores(vector_results, "score")
        bm25_results = _normalize_scores(bm25_results, "bm25_score")

        # ── 第4步: 加权合并 ──
        merged = _merge_results(
            vector_results,
            bm25_results,
            self.vector_weight,
            self.bm25_weight,
        )

        # ── 第5步: 排序 + 按阈值过滤 ──
        merged.sort(key=lambda x: x["score"], reverse=True)

        # 过滤低于阈值的结果
        filtered = [r for r in merged if r["score"] >= threshold]

        # 返回 top_k
        return filtered[:top_k]


def _normalize_scores(results, score_key):
    """
    将结果列表中的分数归一化到 [0, 1] 区间。

    使用 Min-Max 归一化:
      normalized = (score - min) / (max - min)
    """
    if not results:
        return results

    scores = [r[score_key] for r in results]
    min_s = min(scores)
    max_s = max(scores)

    if max_s == min_s:
        # 所有分数相同，给个中等分数
        for r in results:
            r[score_key] = 0.5
    else:
        for r in results:
            r[score_key] = (r[score_key] - min_s) / (max_s - min_s)

    return results


def _merge_results(vector_results, bm25_results, v_weight, b_weight):
    """
    合并两路检索结果。

    策略:
      - 为每个独特的分片分配一个"内容指纹"（用内容的前 100 字符）
      - 如果分片同时出现在两路结果中，加权合并其分数
      - 如果只出现在一路，另一路分数视为 0
    """
    # 用字典去重合并
    merged = {}

    # 处理向量结果
    for r in vector_results:
        key = _content_key(r["content"])
        merged[key] = {
            "content": r["content"],
            "metadata": r.get("metadata", {}),
            "vector_score": r.get("score", 0),
            "bm25_score": 0,
        }

    # 处理 BM25 结果
    for r in bm25_results:
        key = _content_key(r["content"])
        if key in merged:
            # 这个分片两路都检索到了
            merged[key]["bm25_score"] = r.get("bm25_score", 0)
        else:
            merged[key] = {
                "content": r["content"],
                "metadata": r.get("metadata", {}),
                "vector_score": 0,
                "bm25_score": r.get("bm25_score", 0),
            }

    # 计算综合分数
    for item in merged.values():
        item["score"] = round(
            v_weight * item["vector_score"] + b_weight * item["bm25_score"], 4
        )

    return list(merged.values())


def _content_key(content):
    """生成内容指纹（前 100 字符去空白）"""
    clean = "".join(content.split())[:100]
    return clean


# ── 快速测试 ──
if __name__ == "__main__":
    from vector_store import VectorStore
    from bm25 import BM25Index
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        store = VectorStore(tmpdir)
        bm25 = BM25Index()

        # 模拟添加文档
        chunks = [
            {"content": "年假天数：满1年5天，满5年10天，满10年15天，满20年20天。",
             "index": 0, "char_start": 0, "char_end": 50},
            {"content": "迟到30分钟以内扣款50元，30分钟以上按旷工半天处理。",
             "index": 1, "char_start": 51, "char_end": 100},
        ]
        store.add_chunks("test", chunks)
        bm25.build_index([
            {"content": c["content"], "metadata": {"chunk_index": c["index"]}}
            for c in chunks
        ])

        retriever = Retriever(store, bm25)
        results = retriever.retrieve("年假", top_k=2)

        print("搜索 '年假':")
        for r in results:
            print(f"  综合: {r['score']:.4f} | 向量: {r['vector_score']:.4f} | BM25: {r['bm25_score']:.4f}")
            print(f"  内容: {r['content'][:60]}")
