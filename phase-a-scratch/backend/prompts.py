"""
prompts.py — 提示词模板

RAG 系统的最终答案质量高度依赖提示词设计。
这里的模板沿用了 Phase B（Dify）验证过的四道防线：
  1. 角色限定 — 你只能做知识库问答
  2. 范围限定 — 只能用参考文档内容回答
  3. 相似度过滤 — 不相关内容不强行回答
  4. 诚实约定 — 不知道就说不知道

核心:
  - SYSTEM_PROMPT: 系统级指令，定义 AI 的行为规范
  - build_user_prompt(): 构建包含问题和检索结果的用户提示词
"""

# ── 系统提示词 ──
# 这是发给 LLM 的"角色说明书"，定义了它的行为准则。
# temperature=0 确保 LLM 严格遵循这些规则。

SYSTEM_PROMPT = """你是一个企业知识库问答助手。

## 你的任务
仅根据下方"参考文档"中的内容回答用户问题。

## 严格规则
1. **只能使用**参考文档中明确写到的信息来回答
2. 如果文档中**没有答案**，直接回复："根据现有文档，未找到相关信息。"
3. **不要编造、推测或补充**文档外的任何内容
4. 回答时**必须注明**信息来自哪个文档、哪个章节

## 回答格式
1. 先给出**简短结论**（1-2句话，直接回答用户问题）
2. 再**展开说明**（引用文档中的具体内容）
3. 最后附上**出处**

格式示例：
来源：《员工手册》- 第二章 休假政策 > 2.1 年假"""


def build_user_prompt(question, context_chunks):
    """
    构建用户提示词——把问题和检索到的文档片段组合起来。

    参数:
        question: 用户的原始问题
        context_chunks: 检索到的分片列表，每项含 content 和 metadata

    返回:
        完整的用户提示词字符串
    """
    if not context_chunks:
        # 没有任何检索结果时
        return (
            f"用户问题：{question}\n\n"
            "（无参考文档内容）\n\n"
            "请根据以上文档内容回答用户问题。"
            "如果文档中没有相关信息，请明确告知。"
        )

    # 格式化每个检索到的片段
    chunks_text = []
    for i, chunk in enumerate(context_chunks, 1):
        # 提取元信息
        meta = chunk.get("metadata", {})
        filename = meta.get("filename", meta.get("doc_id", "未知文档"))
        chunk_idx = meta.get("chunk_index", i - 1)

        # 构建片段标注
        chunks_text.append(
            f"---片段{i}---\n"
            f"来源：{filename}，分片{chunk_idx}\n"
            f"{chunk['content']}\n"
        )

    chunks_combined = "\n".join(chunks_text)

    # 组合最终提示词
    return (
        f"用户问题：{question}\n\n"
        f"参考文档内容如下：\n\n"
        f"{chunks_combined}\n"
        f"请根据以上文档内容回答用户问题。"
        f"如果文档中没有相关信息，请明确告知。"
    )


# ── 兜底回复（检索无结果时的回答） ──
FALLBACK_ANSWER = (
    "抱歉，根据现有文档未找到相关信息。\n\n"
    "建议您：\n"
    "1. 尝试换个关键词提问\n"
    "2. 确认该内容是否在已上传的文档范围内\n"
    "3. 联系管理员补充相关文档"
)


# ── 查询改写提示词 ──
REWRITE_SYSTEM_PROMPT = """你是一个查询重写助手。用户会用一个口语化的问题来提问，你需要把它改写成一个正式、清晰的查询语句，方便在文档知识库中检索。

规则：
1. 保留原问题的核心意图，不要添加或删除信息
2. 使用正式的书面语言
3. 补充隐含的关键词（如缩写展开、同义词）
4. 直接输出改写后的查询，不要加任何解释，不要加标点符号

示例：
输入："年假有几天"
输出："公司带薪年假天数规定"

输入："迟到怎么处罚"
输出："员工迟到处罚规定 考勤违纪处理办法"

输入："怎么连VPN"
输出："VPN连接方法 VPN使用规范 远程访问配置"

输入："发工资"
输出："薪资发放时间 工资发放日期 薪酬发放周期"

输入："发票丢了"
输出："发票丢失补办流程 发票遗失处理办法"
"""


# ── 快速测试 ──
if __name__ == "__main__":
    # 模拟一些检索结果
    fake_chunks = [
        {
            "content": "员工年假天数：满1年不足5年，年假5天；满5年不足10年，年假10天。",
            "metadata": {"filename": "员工手册.pdf", "chunk_index": 3},
        },
        {
            "content": "年假需提前一周申请，经部门经理批准后方可休假。",
            "metadata": {"filename": "员工手册.pdf", "chunk_index": 4},
        },
    ]

    prompt = build_user_prompt("公司年假有几天？", fake_chunks)
    print(prompt)
