"""
bm25.py — BM25 关键词检索

BM25 是经典的关键词匹配算法，通过统计词频来评估文本相关性。
向量检索擅长语义相似，BM25 擅长精确关键词匹配。
两者互补，组合成混合检索效果最好。

中文需要先分词，这里用 jieba 分词库。

核心类: BM25Index
  - build_index(chunks)   → 构建索引
  - search(query, top_k)  → 检索
"""
import jieba
import numpy as np
from rank_bm25 import BM25Okapi


class BM25Index:
    """
    BM25 关键词检索索引。

    用法:
        idx = BM25Index()
        idx.build_index(chunks)           # chunks = [{"content": "...", ...}, ...]
        results = idx.search("年假", 3)   # 返回 Top-3
    """

    def __init__(self):
        self._chunks = []       # 存储所有分片引用
        self._tokenized = []    # 分词后的分片文本
        self._bm25 = None       # BM25Okapi 实例

    def build_index(self, chunks):
        """
        用分片列表构建 BM25 索引。

        参数:
            chunks: 分片列表，每个元素需含 "content" 键
        """
        self._chunks = list(chunks)

        # 对每个分片做中文分词
        self._tokenized = []
        for c in self._chunks:
            tokens = _tokenize(c["content"])
            self._tokenized.append(tokens)

        # 构建 BM25 模型
        if self._tokenized:
            self._bm25 = BM25Okapi(self._tokenized)

    def search(self, query, top_k=3):
        """
        搜索与 query 最相关的分片。

        参数:
            query: 查询文本
            top_k: 返回结果数

        返回:
            list[dict]，每个包含 content, metadata, bm25_score（已归一化到 0-1）
        """
        if not self._bm25 or not self._chunks:
            return []

        # 分词查询
        query_tokens = _tokenize(query)

        # 获取 BM25 分数
        scores = self._bm25.get_scores(query_tokens)

        if len(scores) == 0:
            return []

        # 取 top-k
        top_indices = np.argsort(scores)[::-1][:top_k]

        # 归一化分数到 0-1
        min_score = np.min(scores)
        max_score = np.max(scores)

        results = []
        for idx in top_indices:
            raw_score = scores[idx]
            if raw_score <= 0:
                continue

            # Min-max 归一化
            if max_score > min_score:
                normalized = (raw_score - min_score) / (max_score - min_score)
            else:
                normalized = 0.5  # 所有分数相同时

            chunk = self._chunks[idx]
            results.append({
                "content": chunk.get("content", ""),
                "metadata": chunk.get("metadata", {}),
                "bm25_score": round(float(normalized), 4),
            })

        return results


def _tokenize(text):
    """
    中文文本分词。

    用 jieba 搜索引擎模式分词，提高召回率。
    搜索引擎模式会把长词再切分为短词，例如：
      "企业知识库" → ["企业", "知识", "知识库", "库"]
    这样用户搜"知识"时也能匹配到"知识库"。
    """
    # 清洗文本：去掉换行和多余空格
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())

    # jieba 搜索引擎模式分词
    tokens = jieba.lcut_for_search(text)

    # 去掉空白 token 和单字符标点
    tokens = [t.strip() for t in tokens if t.strip() and len(t.strip()) > 1]

    return tokens


# ── 快速测试 ──
if __name__ == "__main__":
    # 模拟一些文档分片
    test_chunks = [
        {"content": "公司年假根据工龄确定：满1年5天，满5年10天，满10年15天，满20年20天。"},
        {"content": "员工迟到处罚：迟到30分钟以内扣款50元，30分钟以上按旷工半天处理。"},
        {"content": "密码要求：长度至少12位，必须包含大写字母、小写字母、数字、特殊符号中的至少三类。"},
        {"content": "报销流程：填写报销单，附发票，部门经理审批，财务审核，出纳付款。"},
        {"content": "新员工入职需携带身份证、学历证书、离职证明，到人力资源部办理入职手续。"},
    ]

    idx = BM25Index()
    idx.build_index(test_chunks)

    # 测试检索
    print("=== 搜索 '年假天数' ===")
    for r in idx.search("年假天数", top_k=2):
        print(f"  分数: {r['bm25_score']:.4f} | {r['content'][:60]}")

    print("\n=== 搜索 '迟到处罚扣钱' ===")
    for r in idx.search("迟到处罚扣钱", top_k=2):
        print(f"  分数: {r['bm25_score']:.4f} | {r['content'][:60]}")

    print("\n=== 搜索 '入职需要带什么' ===")
    for r in idx.search("入职需要带什么", top_k=2):
        print(f"  分数: {r['bm25_score']:.4f} | {r['content'][:60]}")
