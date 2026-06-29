"""
test_pipeline.py — 端到端测试脚本

用 Phase B 的 10 道测试题逐一测试 RAG 引擎。
输出每题的问题、回答、来源和判定结果。

运行前提:
    1. 已设置 .env 中的 API Key
    2. 已运行 ingest_all.py 导入文档

用法:
    cd phase-a-scratch/backend
    python test_pipeline.py
"""
from pipeline import RAGPipeline

# 10 道测试题（来自 Phase B）
# (编号, 问题, 期望来源文档)
TEST_QUESTIONS = [
    (1, "公司年假有几天？", "员工手册-2.1"),
    (2, "迟到怎么处罚？", "员工手册-1.3"),
    (3, "公司密码有什么要求？", "IT安全管理制度-2.2"),
    (4, "报销发票丢了怎么办？", "财务报销制度-3.3"),
    (5, "云办公平台怎么创建团队？", "产品手册-3.1"),
    (6, "新员工的电脑是谁给装的？", "入职指南-四"),
    (7, "公司什么时候发工资？", "员工手册-3.1"),
    (8, "怎么连接公司VPN？", "IT安全管理制度-4.1"),
    (9, "报销单需要谁来审批？", "财务报销制度-五"),
    (10, "春节放假几天？", "（应返回未找到）"),
]


def main():
    print("=" * 70)
    print("  企业知识库 RAG 系统 — 端到端测试（10 题）")
    print("=" * 70)
    print()

    # 初始化引擎
    print("🔧 初始化 RAG 引擎...")
    pipeline = RAGPipeline()
    docs = pipeline.list_documents()

    if not docs:
        print("❌ 知识库为空！请先运行: python ingest_all.py")
        return

    print(f"✅ 已加载 {len(docs)} 份文档\n")
    print("=" * 70)
    print()

    # 统计
    accurate = 0
    partial = 0
    wrong = 0
    not_found_correct = 0

    # 逐题测试
    for num, question, expected_source in TEST_QUESTIONS:
        print(f"📋 第{num}题: {question}")
        print(f"   期望来源: {expected_source}")

        try:
            result = pipeline.ask_question(question)
        except Exception as e:
            print(f"   ❌ 运行异常: {e}")
            wrong += 1
            print()
            continue

        print(f"   改写查询: {result['rewritten_query']}")

        if result["used_fallback"]:
            # 触发了兜底回复
            if num == 10:
                print(f'   [OK] 正确返回「未找到」（符合预期）')
                not_found_correct += 1
            else:
                print(f"   ⚠️  未检索到内容（可能有问题，需人工判断）")
                print(f"   回答摘要: {result['answer'][:100]}")
                partial += 1
        else:
            # 有检索结果
            print(f"   来源数: {len(result['sources'])}")
            for s in result['sources']:
                print(f"      [{s['score']:.2f}] {s['filename']}")

            print(f"   回答:")
            answer_preview = result["answer"].replace("\n", "\\n")
            print(f"   {result['answer'][:200]}")

            # 简单自动判断：检查来源是否匹配
            sources_match = any(
                expected_source.split("-")[0] in s.get("filename", "")
                for s in result["sources"]
            )

            if sources_match:
                print(f"   ✅ 来源匹配（文档正确）")
                accurate += 1
            else:
                print(f"   ⚠️  来源不匹配，需人工判断")
                partial += 1

        print()

    # ── 统计 ──
    print("=" * 70)
    print("  测试统计")
    print("=" * 70)
    print(f"  准确 (含来源匹配):  {accurate} 题")
    print(f"  部分准确 (待确认):   {partial} 题")
    print(f"  正确返回未找到:      {not_found_correct} 题 (第10题)")
    print(f"  错误:                {wrong} 题")
    print()

    total_valid = accurate + not_found_correct
    print(f"  有效响应率: {total_valid}/10 = {total_valid * 10}%")
    print(f"  目标准确率: ≥ 85%")
    print(f"  当前状态: {'✅ 达标' if total_valid >= 9 else '⚠️ 需优化'}")
    print()

    # 详细判定说明
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  人工复核清单")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  请对上面每个 ⚠️ 标记的题目进行人工判断：")
    print("    - 答案是否正确？是否编造了文档外内容？")
    print("    - 是否注明了来源出处？")
    print('    - 第10题是否返回了「未找到相关信息」？')
    print()


if __name__ == "__main__":
    main()
