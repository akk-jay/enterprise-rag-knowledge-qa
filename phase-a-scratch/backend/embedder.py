"""
embedder.py — 嵌入（Embedding）API 客户端

把文本转换成向量（一串数字），用于相似度搜索。

使用通义千问的 Embedding API（OpenAI 兼容接口）。
一次调用可以处理多条文本（批量模式），比逐条调用高效得多。

核心函数:
  - embed_texts(texts)  → 批量转换
  - embed_single(text)  → 单条转换
"""
from openai import OpenAI
from config import settings

# 创建 API 客户端（全局复用）
_client = OpenAI(
    api_key=settings.api_key,
    base_url=settings.embedding_base_url,
)


def embed_texts(texts):
    """
    批量将文本转换为向量。

    参数:
        texts: 文本列表，如 ["文本1", "文本2", "文本3"]

    返回:
        向量列表，如 [[0.1, 0.2, ...], [0.3, 0.4, ...], ...]

    示例:
        vectors = embed_texts(["你好世界", "这是测试"])
        print(len(vectors))      # 2
        print(len(vectors[0]))   # 1536 (向量维度)
    """
    if not texts:
        return []

    try:
        response = _client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
        )
    except Exception as e:
        raise RuntimeError(
            f"Embedding API 调用失败: {e}\n"
            f"请检查: 1) API Key 是否正确  2) 网络是否通畅  3) 模型名是否可用 ({settings.embedding_model})"
        )

    # 按 index 排序（API 返回顺序可能不一致）
    data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in data]


def embed_single(text):
    """
    单条文本转向量（自动调用批量接口）。

    参数:
        text: 一段文本

    返回:
        向量 list[float]
    """
    results = embed_texts([text])
    return results[0]


# ── 快速测试 ──
if __name__ == "__main__":
    test_text = "企业知识库问答系统"
    vector = embed_single(test_text)
    print(f"输入文本: {test_text}")
    print(f"向量维度: {len(vector)}")
    print(f"前5个值: {vector[:5]}")
