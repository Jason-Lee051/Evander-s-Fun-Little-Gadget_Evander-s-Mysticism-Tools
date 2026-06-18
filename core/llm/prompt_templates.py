"""
core/llm/prompt_templates.py - 格式化占卜结果为文本并生成分析提示词
"""

# ========== 奇门遁甲部分（原有） ==========
def format_qimen_result(result: dict) -> str:
    """将奇门遁甲排盘结果格式化为清晰文本"""
    lines = []
    lines.append(f"**排盘时间**：{result.get('datetime', '')}")
    lines.append(f"**日柱**：{result.get('day_gz', '')}   **时柱**：{result.get('hour_gz', '')}")
    lines.append(f"**局数**：{result.get('dun_type', '')}{result.get('ju', '')}局   **节气**：{result.get('jieqi', '')} {result.get('yuan', '')}")
    lines.append("")
    lines.append("**九宫信息**：")
    gong_names = {
        1: "坎1宫", 8: "艮8宫", 3: "震3宫", 4: "巽4宫",
        9: "离9宫", 2: "坤2宫", 7: "兑7宫", 6: "乾6宫",
        5: "中5宫"
    }
    for info in result.get('pan_info', []):
        gong = info['gong']
        name = gong_names.get(gong, f"宫{gong}")
        if gong == 5:
            lines.append(f"{name}：（寄坤2）星{info.get('star','')}，天盘{info.get('tian_pan','')}，地盘{info.get('di_pan','')}")
        else:
            lines.append(f"{name}：神{info.get('shen','')}，星{info.get('star','')}，门{info.get('door','')}，天盘{info.get('tian_pan','')}，地盘{info.get('di_pan','')}")
    return "\n".join(lines)

def build_qimen_prompt(pan_text: str, matter: str, location: str) -> str:
    """生成奇门遁甲分析提示词（评分强制放在开头）"""
    prompt = f"""你是一位精通奇门遁甲的占卜师。请根据以下排盘结果，结合用户提供的预测事项和地点，进行详细、易懂的断局分析。

要求：
1. **首先，在回答的最开头给出针对所问事项的综合评分（百分制），并简要说明评分依据。**
   评分应基于盘中吉凶、用神旺衰、格局组合等因素综合给出。
2. 接着简要解释盘局特点（如用神落宫、吉凶格局）。
3. 然后结合事项“{matter}”和地点“{location}”，给出针对性结论和建议。
4. 如果涉及方位、时间，请结合盘内信息提示。
5. 语气平和，避免绝对化。

排盘结果：
{pan_text}

请开始分析："""
    return prompt

# ========== 梅花易数部分（新增） ==========
def format_meihua_result(gua_data: dict) -> str:
    """格式化梅花易数卦盘为文本"""
    from core.meihua.render import format_meihua_result as _format
    return _format(gua_data)

def build_meihua_prompt(pan_text: str, question: str, background: str = "") -> str:
    """生成梅花易数分析提示词（评分放在开头）"""
    prompt = f"""你是一位精通《梅花易数》的资深易学专家。请根据以下卦象信息，为问卦者提供细致、有洞察力的解读。

要求：
1. **首先，在回答的最开头给出针对所问事项的综合评分（百分制），并简要说明评分依据。**
   评分应基于体用生克、卦象吉凶、爻辞启示等因素综合给出。
2. 接着进行卦象总览，解释本卦、变卦、互卦的核心含义。
3. 详细分析体用生克关系，说明对所问之事的吉凶影响。
4. 解读动爻的爻辞及其启示。
5. 最后给出综合建议，语言通俗易懂。

【问卦者信息】：
所问事项：{question}
背景：{background if background else "无额外信息"}

【卦象数据】：
{pan_text}

请开始分析："""
    return prompt