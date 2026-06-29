"""
rewriter.py — 查询改写器

用户提问偏口语化（"迟到咋处理？"），文档用的是书面语（"迟到处罚规定"）。
直接用原问题检索可能匹配不到文档内容。

查询改写 = 把口语转书面语 + 补充同义词，提高检索命中率。

如果 API 调用失败，会返回原始问题（不阻断流程）。
"""
from openai import OpenAI
from config import settings
from prompts import REWRITE_SYSTEM_PROMPT

# 创建 API 客户端（全局复用）
_client = OpenAI(
    api_key=settings.api_key,
    base_url=settings.llm_base_url,
)


def rewrite_query(original_question):
    """
    将用户口语化问题改写为书面语查询。

    参数:
        original_question: 用户输入的原始问题

    返回:
        str: 改写后的查询短语

    示例:
        rewrite_query("迟到咋处理")  → "员工迟到处罚处理办法"
        rewrite_query("年假有几天")  → "公司带薪年假天数规定"
    """
    # 如果问题本身已经比较正式（长度 > 20 字），可能不需要改写
    # 但简单起见，一律走改写流程（成本很低，一次调用约 0.001 元）

    try:
        response = _client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": original_question},
            ],
            temperature=0,      # 确定性输出
            max_tokens=100,     # 改写结果一般很短
        )

        rewritten = response.choices[0].message.content.strip()

        # 清理：去掉 LLM 可能添加的引号、换行等
        rewritten = rewritten.strip('"\'').replace("\n", " ").strip()

        # 如果改写结果为空或和原文一样，返回原文
        if not rewritten:
            return original_question

        return rewritten

    except Exception as e:
        # 容错：API 失败时用原问题，不阻断流程
        print(f"[警告] 查询改写失败: {e}，将使用原问题检索")
        return original_question


# ── 快速测试 ──
if __name__ == "__main__":
    tests = [
        "年假有几天",
        "迟到怎么处罚",
        "工资什么时候发",
        "怎么连VPN",
        "报销发票丢了怎么办",
    ]
    for q in tests:
        rewritten = rewrite_query(q)
        print(f"  {q}")
        print(f"  → {rewritten}")
        print()
