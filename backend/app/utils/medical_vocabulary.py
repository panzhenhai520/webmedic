"""
医疗词汇库
用于 Mock 模式的关键词提取

维护说明：
1. 可以随时添加新的词汇到各个字典中
2. 每个字典的 key 是标准化名称，value 是可能出现的各种说法
3. 添加专科词汇时，建议按科室分类注释
4. 支持中文医学术语和口语化表达
"""

# 身体部位词库（包含方位）
BODY_PARTS = {
    # 头颈部
    "头部": ["头", "头部", "颅", "颅内"],
    "颈部": ["颈", "颈部", "颈椎", "脖子"],
    "面部": ["面", "面部", "脸", "脸部"],
    "眼": ["眼", "眼睛", "眼部", "眼球"],
    "耳": ["耳", "耳朵", "耳部"],
    "鼻": ["鼻", "鼻子", "鼻部"],
    "口": ["口", "口腔", "嘴"],
    "咽喉": ["咽", "喉", "咽喉", "喉咙"],

    # 躯干
    "胸部": ["胸", "胸部", "胸腔"],
    "腹部": ["腹", "腹部", "肚子"],
    "背部": ["背", "背部"],
    "腰部": ["腰", "腰部"],
    "臀部": ["臀", "臀部", "屁股"],

    # 四肢
    "肩部": ["肩", "肩部", "肩膀"],
    "上臂": ["上臂", "大臂"],
    "前臂": ["前臂", "小臂"],
    "肘部": ["肘", "肘部", "胳膊肘"],
    "腕部": ["腕", "腕部", "手腕"],
    "手部": ["手", "手部"],
    "手指": ["手指", "指头", "拇指", "食指", "中指", "无名指", "小指"],
    "大腿": ["大腿", "腿"],
    "小腿": ["小腿"],
    "膝部": ["膝", "膝盖", "膝关节"],
    "踝部": ["踝", "脚踝"],
    "足部": ["足", "脚", "足部", "脚部"],
    "脚趾": ["脚趾", "趾头"],

    # 骨科专业 - 骨骼
    "颅骨": ["颅骨", "头骨"],
    "颈椎": ["颈椎", "颈椎骨"],
    "胸椎": ["胸椎", "胸椎骨"],
    "腰椎": ["腰椎", "腰椎骨"],
    "骶骨": ["骶骨", "骶椎"],
    "尾骨": ["尾骨", "尾椎"],
    "肋骨": ["肋骨", "肋"],
    "胸骨": ["胸骨"],
    "锁骨": ["锁骨"],
    "肩胛骨": ["肩胛骨", "肩胛"],
    "肱骨": ["肱骨"],
    "桡骨": ["桡骨"],
    "尺骨": ["尺骨"],
    "腕骨": ["腕骨"],
    "掌骨": ["掌骨"],
    "指骨": ["指骨"],
    "髋骨": ["髋骨", "髂骨"],
    "股骨": ["股骨", "大腿骨"],
    "髌骨": ["髌骨", "膝盖骨"],
    "胫骨": ["胫骨"],
    "腓骨": ["腓骨"],
    "跗骨": ["跗骨"],
    "跖骨": ["跖骨"],
    "趾骨": ["趾骨"],

    # 骨科专业 - 关节
    "肩关节": ["肩关节"],
    "肘关节": ["肘关节"],
    "腕关节": ["腕关节"],
    "髋关节": ["髋关节"],
    "膝关节": ["膝关节"],
    "踝关节": ["踝关节"],
    "脊柱": ["脊柱", "脊椎", "脊梁骨"],

    # 内脏器官
    "心脏": ["心脏", "心"],
    "肺": ["肺", "肺部"],
    "肝脏": ["肝", "肝脏"],
    "胆囊": ["胆", "胆囊"],
    "胰腺": ["胰", "胰腺"],
    "脾脏": ["脾", "脾脏"],
    "胃": ["胃", "胃部"],
    "肠": ["肠", "肠道", "小肠", "大肠"],
    "十二指肠": ["十二指肠"],
    "结肠": ["结肠"],
    "直肠": ["直肠"],
    "肾脏": ["肾", "肾脏"],
    "膀胱": ["膀胱"],
    "子宫": ["子宫"],
    "卵巢": ["卵巢"],
    "前列腺": ["前列腺"],
    "甲状腺": ["甲状腺"],
}

# 方位词
DIRECTIONS = {
    "左": ["左", "左侧", "左边"],
    "右": ["右", "右侧", "右边"],
    "上": ["上", "上部", "上方"],
    "下": ["下", "下部", "下方"],
    "前": ["前", "前部", "前方"],
    "后": ["后", "后部", "后方"],
    "内": ["内", "内侧"],
    "外": ["外", "外侧"],
    "中": ["中", "中部", "中央"],
}

# 症状词库
SYMPTOMS = {
    "疼痛": ["痛", "疼", "疼痛", "痛感", "酸痛", "刺痛", "胀痛", "隐痛", "绞痛"],
    "头晕": ["晕", "头晕", "眩晕", "晕眩"],
    "恶心": ["恶心", "想吐", "反胃"],
    "呕吐": ["呕吐", "吐"],
    "发热": ["发热", "发烧", "烧", "热"],
    "咳嗽": ["咳", "咳嗽"],
    "气短": ["气短", "气促", "呼吸困难", "喘"],
    "乏力": ["乏力", "无力", "疲劳", "累"],
    "失眠": ["失眠", "睡不着", "睡眠不好", "睡不好", "睡眠不太好", "睡眠也不好", "睡眠也不太好",
               "睡得不好", "睡得不太好", "睡眠差", "睡眠质量差", "睡不踏实", "睡眠不佳", "睡觉不好"],
    "腹泻": ["腹泻", "拉肚子", "拉稀"],
    "便秘": ["便秘", "大便困难"],
    "水肿": ["水肿", "肿", "肿胀"],
    "麻木": ["麻", "麻木", "发麻"],
    "瘙痒": ["痒", "瘙痒"],
    "出血": ["出血", "流血"],
    "皮疹": ["皮疹", "疹子", "红疹"],
}

# 常见疾病/诊断词库
DISEASES = {
    # 消化系统
    "胆囊息肉": ["胆囊息肉"],
    "胆囊炎": ["胆囊炎"],
    "胆结石": ["胆结石", "胆石症"],
    "肝囊肿": ["肝囊肿"],
    "脂肪肝": ["脂肪肝"],
    "胃炎": ["胃炎"],
    "胃溃疡": ["胃溃疡"],

    # 循环系统
    "高血压": ["高血压", "血压高"],
    "冠心病": ["冠心病"],
    "心律失常": ["心律失常", "心律不齐"],

    # 呼吸系统
    "支气管炎": ["支气管炎"],
    "肺炎": ["肺炎"],
    "哮喘": ["哮喘"],

    # 骨骼肌肉系统
    "颈椎病": ["颈椎病"],
    "腰椎间盘突出": ["腰椎间盘突出", "腰突"],
    "骨质增生": ["骨质增生", "骨刺"],
    "关节炎": ["关节炎"],

    # 内分泌系统
    "糖尿病": ["糖尿病", "血糖高"],
    "甲亢": ["甲亢", "甲状腺功能亢进"],
    "甲减": ["甲减", "甲状腺功能减退"],

    # 泌尿系统
    "肾结石": ["肾结石"],
    "尿路感染": ["尿路感染"],
}

# 时间词
TIME_PATTERNS = [
    (r'(\d+)\s*年', '年'),
    (r'(\d+)\s*个月', '个月'),
    (r'(\d+)\s*月', '月'),
    (r'(\d+)\s*周', '周'),
    (r'(\d+)\s*天', '天'),
    (r'(\d+)\s*日', '天'),
    (r'(\d+)\s*小时', '小时'),
    (r'(\d+)\s*分钟', '分钟'),
]


def extract_body_parts(text: str) -> list:
    """
    从文本中提取身体部位（包含方位）
    方位只在与部位紧邻时才组合，避免将时间词中的"前"误识别为方位

    Args:
        text: 输入文本

    Returns:
        提取到的身体部位列表
    """
    import re
    found_parts = []

    # 方位词列表（只匹配明确的方位短语，不匹配单独的"前"等模糊字符）
    direction_patterns = ["左侧", "右侧", "左边", "右边", "上方", "下方", "前方", "后方", "内侧", "外侧"]

    # 提取部位：直接从文本中找部位关键词，不强制组合方位
    for part, keywords in BODY_PARTS.items():
        for keyword in keywords:
            if keyword in text:
                # 检查该部位前是否紧跟明确方位词（如"左侧颈部"）
                prefixed = False
                for dir_pat in direction_patterns:
                    if dir_pat + keyword in text:
                        combined = f"{dir_pat.rstrip('侧边方')}{part}"
                        if combined not in found_parts:
                            found_parts.append(combined)
                        prefixed = True
                        break
                if not prefixed:
                    if part not in found_parts:
                        found_parts.append(part)
                break

    return found_parts


def extract_symptoms(text: str) -> list:
    """
    从文本中提取症状

    Args:
        text: 输入文本

    Returns:
        提取到的症状列表
    """
    found_symptoms = []

    for symptom, keywords in SYMPTOMS.items():
        for keyword in keywords:
            if keyword in text:
                if symptom not in found_symptoms:
                    found_symptoms.append(symptom)
                break

    return found_symptoms


def extract_diseases(text: str) -> list:
    """
    从文本中提取疾病/诊断

    Args:
        text: 输入文本

    Returns:
        提取到的疾病列表
    """
    found_diseases = []

    for disease, keywords in DISEASES.items():
        for keyword in keywords:
            if keyword in text:
                if disease not in found_diseases:
                    found_diseases.append(disease)
                break

    return found_diseases


def extract_duration(text: str) -> str:
    """
    从文本中提取时间

    Args:
        text: 输入文本

    Returns:
        提取到的时间描述
    """
    import re

    for pattern, unit in TIME_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            return f"{matches[-1]}{unit}"

    return ""


# 正则模式：用于捕捉口语化表达，无法用简单子串匹配的症状描述
# 格式: (regex_pattern, canonical_symptom_name)
SYMPTOM_REGEX_PATTERNS = [
    (r'睡[眠觉]?[也还]?[不没][太很]?[好佳]', '失眠'),
    (r'睡[得]?[不没][太很]?[好踏实]', '失眠'),
]

# 否定词：出现在部位/症状前方或部位与症状之间时，表示该项为阴性
# 排在前面的较长词优先匹配，避免"没有"被拆成"没"
NEGATION_WORDS = ["没有", "不再", "否认", "未见", "未", "无", "不", "没"]

# 连接词：连接多个部位，使其共享同一症状（如"颈部和腰部都疼痛"）
CONJUNCTION_WORDS = ["还有", "以及", "和", "与", "及", "跟", "加上", "、"]


def _greedy_tokenize(text: str) -> list:
    """
    贪心最长匹配分词：对文本从左到右扫描，优先匹配更长的关键词。
    这样 "头晕" 会整体被识别为症状，而不会让 "头" 误命中 "头部"；
    "恶心" 整体识别为症状，而不会让 "心" 误命中 "心脏"。

    Returns:
        list of (token_type, canonical_name, start, end)
        token_type: 'body' | 'symptom'
    """
    import re

    # 建立关键词列表，按长度降序（贪心最长优先）
    all_tokens = []
    for name, keywords in BODY_PARTS.items():
        for kw in keywords:
            all_tokens.append(('body', name, kw))
    for name, keywords in SYMPTOMS.items():
        for kw in keywords:
            all_tokens.append(('symptom', name, kw))
    all_tokens.sort(key=lambda x: len(x[2]), reverse=True)

    matched = []   # (type, name, start, end)
    used = set()   # 已匹配的字符位置

    i = 0
    while i < len(text):
        best = None
        for token_type, name, kw in all_tokens:
            kw_len = len(kw)
            if text[i:i + kw_len] == kw:
                positions = set(range(i, i + kw_len))
                if not positions & used:
                    best = (token_type, name, i, i + kw_len)
                    break
        if best:
            matched.append(best)
            used.update(range(best[2], best[3]))
            i = best[3]
        else:
            i += 1

    # 正则后处理：补充口语化表达（如"睡眠也不太好"）
    for pattern, symptom_name in SYMPTOM_REGEX_PATTERNS:
        for m in re.finditer(pattern, text):
            span = set(range(m.start(), m.end()))
            if not span & used:
                matched.append(('symptom', symptom_name, m.start(), m.end()))
                used.update(span)

    matched.sort(key=lambda x: x[2])
    return matched


def _has_negation(text: str, start: int, end: int) -> bool:
    """检查 text[start:end] 区间内是否含有否定词（长词优先，避免"没有"被"没"误判）"""
    segment = text[start:end]
    for neg in NEGATION_WORDS:  # 已按长度降序排列
        if neg in segment:
            return True
    return False


def _has_conjunction(text: str, start: int, end: int) -> bool:
    """检查 text[start:end] 区间内是否含有连接词"""
    segment = text[start:end]
    return any(conj in segment for conj in CONJUNCTION_WORDS)


# 并列间隙允许的中性字符：仅含这些字符时，两个症状视为同一并列组
_PARALLEL_NEUTRAL = set("、，, \u3000")


def _is_parallel_gap(text: str, start: int, end: int) -> bool:
    """
    判断两个症状 token 之间的间隙是否为并列关系（可传播否定作用域）。

    规则：
    - 间隙为空（直接相邻）→ 并列
    - 间隙仅含标点（、，）或连接词（和/与/还有…）→ 并列
    - 间隙含实义词（如"有""但""却"）→ 括号关闭，不传播

    例：
      "头晕恶心"   gap=""    → True   （"没有头晕恶心" → 两者均否定）
      "头晕、恶心" gap="、"  → True
      "头晕，恶心" gap="，"  → True
      "头晕，有恶心" gap="，有" → False （"有"是实义词，括号关闭）
    """
    segment = text[start:end]
    if not segment:
        return True
    # 间隙含连接词视为并列
    if any(conj in segment for conj in CONJUNCTION_WORDS):
        return True
    # 间隙仅含中性标点视为并列
    return all(c in _PARALLEL_NEUTRAL for c in segment)


def extract_complaint_pairs(text: str) -> tuple:
    """
    从患者文本中提取主诉的主谓结构：(部位, 症状) 对 + 独立症状。

    核心逻辑：
    1. 贪心最长匹配分词，避免"恶心"→心脏、"头晕"→头部等误识别
    2. 否定词检测：部位前方或部位与症状间隙中含否定词时跳过该配对
       例："没有腹痛" / "颈部不疼痛" → 均不提取
    3. 连接词分组：被"和/与/还有"连接的多个部位共享同一症状
       例："颈部和腰部都疼痛" → [("颈部","疼痛"), ("腰部","疼痛")]
    4. 剩余独立症状（无对应部位）直接列出

    Args:
        text: 患者发言文本

    Returns:
        pairs: list of (body_part_name, symptom_name)
        standalone_symptoms: list of symptom names
        standalone_body_parts: list of body part names（有部位但无对应症状）
    """
    matched = _greedy_tokenize(text)

    pairs = []
    standalone_symptoms = []
    standalone_body_parts = []
    paired_indices = set()

    i = 0
    while i < len(matched):
        if i in paired_indices:
            i += 1
            continue

        token = matched[i]

        if token[0] == 'body':
            # ── 1. 检查部位前方的否定词（窗口：部位起始前 3 字符）──────────────
            prefix_start = max(0, token[2] - 3)
            prefix_negated = _has_negation(text, prefix_start, token[2])

            # ── 2. 收集连接词相连的部位组（如"颈部和腰部"）──────────────────────
            body_group = [i]
            j = i + 1
            while j < len(matched):
                if j in paired_indices:
                    j += 1
                    continue
                nxt = matched[j]
                prev_end = matched[body_group[-1]][3]
                gap = nxt[2] - prev_end
                if nxt[0] == 'body' and gap <= 8 and _has_conjunction(text, prev_end, nxt[2]):
                    body_group.append(j)
                    j += 1
                else:
                    break

            # ── 3. 在部位组后寻找匹配的症状 ─────────────────────────────────────
            last_body_end = matched[body_group[-1]][3]
            found_symptom = None
            symptom_idx = None
            gap_negated = False

            for k in range(j, len(matched)):
                if k in paired_indices:
                    continue
                sym = matched[k]
                if sym[0] == 'body':
                    break  # 遇到下一个部位，停止
                if sym[0] == 'symptom' and sym[2] - last_body_end <= 5:
                    gap_negated = _has_negation(text, last_body_end, sym[2])
                    found_symptom = sym[1]
                    symptom_idx = k
                    break

            # ── 4. 标记消耗，根据否定情况决定输出 ───────────────────────────────
            for bi in body_group:
                paired_indices.add(bi)
            if found_symptom is not None:
                paired_indices.add(symptom_idx)

            if not prefix_negated and not gap_negated:
                if found_symptom is not None:
                    # 部位组中每个部位都配上同一症状
                    for bi in body_group:
                        pairs.append((matched[bi][1], found_symptom))
                else:
                    # 有部位但未找到症状
                    for bi in body_group:
                        bp_name = matched[bi][1]
                        if bp_name not in standalone_body_parts:
                            standalone_body_parts.append(bp_name)
            # 否定情况：直接丢弃，不写入任何输出列表

        elif token[0] == 'symptom':
            # ── 检查症状前方的否定词（窗口：症状起始前 3 字符）──────────────────
            prefix_start = max(0, token[2] - 3)
            prefix_neg = _has_negation(text, prefix_start, token[2])

            if prefix_neg:
                # 否定作用域传播：向后收集与当前症状并列的症状，一并否定。
                # 并列判断：两 token 之间的间隙仅含标点或连接词（无实义词）。
                # 例："没有头晕恶心" → 头晕、恶心均否定
                #     "没有头晕，有恶心" → "，有"含实义词"有" → 括号关闭 → 恶心保留
                paired_indices.add(i)
                group_end_pos = token[3]
                k = i + 1
                while k < len(matched):
                    if k in paired_indices:
                        k += 1
                        continue
                    nxt = matched[k]
                    if nxt[0] != 'symptom':
                        break
                    if _is_parallel_gap(text, group_end_pos, nxt[2]):
                        paired_indices.add(k)
                        group_end_pos = nxt[3]
                        k += 1
                    else:
                        break
                # 整个并列组均被否定，不写入任何输出列表
            else:
                if token[1] not in standalone_symptoms:
                    standalone_symptoms.append(token[1])
                paired_indices.add(i)

        i += 1

    return pairs, standalone_symptoms, standalone_body_parts
