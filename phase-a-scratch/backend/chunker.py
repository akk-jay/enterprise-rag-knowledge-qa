"""
chunker.py — 文本分片器

把长文本切成有重叠的小块（chunk），便于检索。
每个 chunk 保留字符位置信息，方便最终答案溯源。

核心函数: chunk_text(text, chunk_size, chunk_overlap) -> List[dict]
"""
import re


def chunk_text(text, chunk_size=500, chunk_overlap=100):
    """
    将文本按结构边界切分为重叠的分片。

    切分策略（优先级从高到低）:
      1. 按段落边界 (双换行 \\n\\n)
      2. 按换行 (\\n)
      3. 按中文句尾 (。！？；)
      4. 硬切（最后手段）

    重叠机制:
      每个新分片开头包含前一个分片末尾的 chunk_overlap 个字符，
      确保跨分片边界的信息不会丢失。

    参数:
        text: 要切分的文本
        chunk_size: 每个分片的最大字符数（默认 500）
        chunk_overlap: 相邻分片的重叠字符数（默认 100）

    返回:
        list[dict]，每个元素:
          - content: 分片文本
          - index: 分片序号（0 开始）
          - char_start: 原文中的起始位置
          - char_end: 原文中的结束位置
    """
    if not text or not text.strip():
        return []

    # ── 步骤1: 按结构边界切分为"段落" ──
    segments = _split_by_structure(text, chunk_size)

    # ── 步骤2: 将段落组装成分片（带重叠） ──
    chunks = _assemble_chunks(segments, chunk_size, chunk_overlap)

    return chunks


def _split_by_structure(text, max_len):
    """
    按结构边界切分文本。
    先用大边界（段落），不满足再用小边界（句子）。
    """
    # 第一轮：按双换行切（段落级）
    segments = _split_by_separator(text, r"\n\n+")

    # 第二轮：超过 max_len 的段落继续按单换行切
    segments = _refine_segments(segments, r"\n", max_len)

    # 第三轮：超过 max_len 的段落按中文句尾切
    segments = _refine_segments(segments, r"[。！？；]", max_len)

    # 第四轮：仍然超长的，硬切
    segments = _hard_split_segments(segments, max_len)

    return segments


def _split_by_separator(text, sep_pattern):
    """按分隔符切分文本，保留非空段落"""
    parts = re.split(f"({sep_pattern})", text)
    # 重新组合：分隔符附在前一段后面
    result = []
    i = 0
    while i < len(parts):
        seg = parts[i]
        if i + 1 < len(parts) and re.match(f"^{sep_pattern}$", parts[i + 1]):
            seg += parts[i + 1]
            i += 1
        i += 1
        if seg.strip():
            result.append(seg)
    return result if result else [text]


def _refine_segments(segments, sep_pattern, max_len):
    """将超过 max_len 的段落进一步切分"""
    result = []
    for seg in segments:
        if len(seg) > max_len:
            # 尝试用更细的分隔符切分
            sub_segs = _split_by_separator(seg, sep_pattern)
            result.extend(sub_segs)
        else:
            result.append(seg)
    return result


def _hard_split_segments(segments, max_len):
    """对于仍然超长的段落，直接硬切"""
    result = []
    for seg in segments:
        if len(seg) <= max_len:
            result.append(seg)
        else:
            # 在 max_len 处切断
            for i in range(0, len(seg), max_len):
                result.append(seg[i : i + max_len])
    return result


def _assemble_chunks(segments, chunk_size, chunk_overlap):
    """
    将段落列表组装成分片。
    - 尽量把多个小段落放进同一个分片
    - 分片之间有 chunk_overlap 字符的重叠
    """
    chunks = []
    current_text = ""
    char_pos = 0  # 追踪在原文中的位置

    for seg in segments:
        # 如果加入这个段落后超出 chunk_size，先保存当前分片
        if len(current_text) + len(seg) > chunk_size and current_text:
            chunks.append(current_text)
            # 下一个分片以当前分片末尾的 overlap 字符开头
            if len(current_text) > chunk_overlap:
                current_text = current_text[-chunk_overlap:] + seg
            else:
                current_text = seg
        else:
            current_text += seg

    # 最后一个分片
    if current_text.strip():
        chunks.append(current_text)

    # 构建带元信息的返回结果
    result = []
    for i, content in enumerate(chunks):
        # 计算在原文中的大致位置
        start = text_original_pos(chunks, i)
        end = start + len(content)
        result.append({
            "content": content,
            "index": i,
            "char_start": start,
            "char_end": end,
        })

    return result


def text_original_pos(chunks, idx):
    """估算第 idx 个分片在原始文本中的位置"""
    pos = 0
    for i in range(idx):
        pos += len(chunks[i])
    return pos


# ── 快速测试 ──
if __name__ == "__main__":
    sample = (
        "第一章 总则\n\n第一条 为规范公司管理，制定本制度。\n\n"
        "第二章 考勤制度\n\n第二条 员工应按时上下班，不得迟到早退。"
        "迟到30分钟以内扣款50元；迟到30分钟以上按旷工半天处理。"
        "连续迟到3次或月度累计迟到5次，给予书面警告。\n\n"
        "第三条 因故不能到岗者，应提前向直属领导请假。\n\n"
        "第三章 休假政策\n\n"
        "第四条 员工享有国家法定节假日、年假、病假、婚假等假期。"
    )

    chunks = chunk_text(sample, chunk_size=200, chunk_overlap=50)

    for c in chunks:
        print(f"--- 分片 {c['index']} (字符 {c['char_start']}-{c['char_end']}) ---")
        print(c["content"][:100])
        print(f"长度: {len(c['content'])}")
        print()
    print(f"总片数: {len(chunks)}")
