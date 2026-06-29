"""
generator.py — LLM 答案生成器

RAG 的最后一步："G"（Generation，生成）。

把用户问题 + 检索到的文档片段发给 LLM，
LLM 根据文档内容生成答案。

用通义千问 qwen3-max，temperature=0 确保输出确定性。
"""
from openai import OpenAI
from config import settings
from prompts import SYSTEM_PROMPT, build_user_prompt, FALLBACK_ANSWER

# 创建 API 客户端（全局复用）
_client = OpenAI(
    api_key=settings.api_key,
    base_url=settings.llm_base_url,
)


def generate_answer(question, context_chunks):
    """
    基于检索到的文档片段生成答案。

    参数:
        question: 用户问题
        context_chunks: 检索到的相关文档片段列表

    返回:
        str: AI 生成的答案
    """
    # 如果没有检索到任何内容，直接返回兜底回复
    if not context_chunks:
        return FALLBACK_ANSWER

    # 构建提示词
    user_prompt = build_user_prompt(question, context_chunks)

    try:
        response = _client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.llm_temperature,   # 0 = 确定性输出
            max_tokens=settings.llm_max_tokens,      # 1024
        )

        answer = response.choices[0].message.content
        return answer.strip()

    except Exception as e:
        # LLM 调用失败时返回错误信息
        return (
            f"抱歉，AI 服务暂时不可用。\n\n"
            f"错误信息: {e}\n\n"
            f"请检查 API Key 和网络连接后重试。"
        )


# ── 快速测试 ──
if __name__ == "__main__":
    # 模拟一次问答
    test_chunks = [
        {
            "content": "员工年假天数规定：工龄满1年不足5年，年假5天；满5年不足10年，年假10天；满10年不足20年，年假15天；满20年以上，年假20天。",
            "metadata": {"filename": "员工手册.pdf", "chunk_index": 5},
        },
    ]

    answer = generate_answer("公司年假有几天？", test_chunks)
    print(answer)
