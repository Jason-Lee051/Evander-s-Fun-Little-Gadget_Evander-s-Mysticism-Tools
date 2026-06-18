"""
core/meihua/paipan.py - 排卦：构建本卦、变卦、互卦，计算体用
"""
from typing import Dict, List, Tuple
from .bagua import TRIGRAM_MAP, TRIGRAM_WUXING, get_gua_name

def build_full_gua(upper_num: int, lower_num: int, moving_line: int) -> Dict:
    """
    输入上卦数、下卦数、动爻位置（1-6，从下往上），返回完整卦盘
    返回字典包含本卦、变卦、互卦、体用关系等
    """
    # 本卦：上卦、下卦
    upper_info = TRIGRAM_MAP[upper_num]
    lower_info = TRIGRAM_MAP[lower_num]
    ben_gua = {
        "upper": upper_num,
        "upper_name": upper_info["name"],
        "upper_symbol": upper_info["symbol"],
        "upper_wuxing": upper_info["wuxing"],
        "lower": lower_num,
        "lower_name": lower_info["name"],
        "lower_symbol": lower_info["symbol"],
        "lower_wuxing": lower_info["wuxing"],
        "name": get_gua_name(upper_info["name"], lower_info["name"]),
        "moving_line": moving_line,
    }

    # 变卦：动爻阴阳互换
    # 构建六个爻（从下往上，索引0-5对应初爻到上爻）
    # 先获取本卦上下卦的阳阴组合：乾三阳，兑上缺（上阴下阳?），需正确判断
    # 用二进制表示：阳爻为1，阴爻为0，上卦为高三位，下卦为低三位
    # 为简化，直接用八卦的阴阳表示（阳卦：乾震坎艮，阴卦：坤巽离兑）
    # 但这里我们直接用卦的阴阳二进制组合
    # 定义八卦的二进制（阳=1，阴=0），从下往上三位（下卦为低三位）
    # 乾111, 兑110, 离101, 震100, 巽011, 坎010, 艮001, 坤000 (从下往上)
    trigram_binary = {
        1: [1,1,1],  # 乾
        2: [0,1,1],  # 兑（上阴下阳？实际兑上缺，即最上一爻阴，下面两阳，所以从下往上：阳阳阴 -> 1,1,0？需确认。为准确，按传统：兑上缺，即第六爻阴，故二进制为1,1,0（从下往上））
        # 但为简化，我们用周易的二进制表示（从下往上）：
        # 乾111, 兑110, 离101, 震100, 巽011, 坎010, 艮001, 坤000
        # 以下为确认:
        # 兑：下二阳，上一阴，故从下往上：1,1,0
        # 离：中阴，上下阳：1,0,1
        # 震：下阳，上二阴：1,0,0
        # 巽：下阴，上二阳：0,1,1
        # 坎：中阳，上下阴：0,1,0
        # 艮：下阴，中阴，上阳：0,0,1
        # 坤：000
    }
    # 为简化，我们使用预定义字典
    bin_map = {
        1: [1,1,1],
        2: [1,1,0],
        3: [1,0,1],
        4: [1,0,0],
        5: [0,1,1],
        6: [0,1,0],
        7: [0,0,1],
        8: [0,0,0],
    }
    # 本卦六爻（从下往上）
    ben_lines = bin_map[lower_num] + bin_map[upper_num]  # 低三位为下卦，高三位为上卦
    # 变卦六爻
    bian_lines = ben_lines.copy()
    idx = moving_line - 1  # 转为0索引
    bian_lines[idx] = 1 - bian_lines[idx]  # 取反

    # 分离变卦上下卦
    bian_lower_bin = bian_lines[0:3]
    bian_upper_bin = bian_lines[3:6]
    # 反查卦数
    def bin_to_trigram(bin_list):
        for num, b in bin_map.items():
            if b == bin_list:
                return num
        return None
    bian_lower_num = bin_to_trigram(bian_lower_bin)
    bian_upper_num = bin_to_trigram(bian_upper_bin)
    if bian_lower_num is None or bian_upper_num is None:
        # 容错
        bian_lower_num = lower_num
        bian_upper_num = upper_num

    bian_upper_info = TRIGRAM_MAP[bian_upper_num]
    bian_lower_info = TRIGRAM_MAP[bian_lower_num]
    bian_gua = {
        "upper": bian_upper_num,
        "upper_name": bian_upper_info["name"],
        "lower": bian_lower_num,
        "lower_name": bian_lower_info["name"],
        "name": get_gua_name(bian_upper_info["name"], bian_lower_info["name"]),
    }

    # 互卦：取本卦的二、三、四爻为下卦（从下往上索引1,2,3），三、四、五爻为上卦（索引2,3,4）
    # 下互：ben_lines[1], ben_lines[2], ben_lines[3]
    hu_lower_bin = ben_lines[1:4]
    hu_upper_bin = ben_lines[2:5]
    hu_lower_num = bin_to_trigram(hu_lower_bin)
    hu_upper_num = bin_to_trigram(hu_upper_bin)
    if hu_lower_num is None or hu_upper_num is None:
        # 容错
        hu_lower_num = lower_num
        hu_upper_num = upper_num
    hu_upper_info = TRIGRAM_MAP[hu_upper_num]
    hu_lower_info = TRIGRAM_MAP[hu_lower_num]
    hu_gua = {
        "upper": hu_upper_num,
        "upper_name": hu_upper_info["name"],
        "lower": hu_lower_num,
        "lower_name": hu_lower_info["name"],
        "name": get_gua_name(hu_upper_info["name"], hu_lower_info["name"]),
    }

    # 体用：体卦为不含动爻的卦（通常为下卦），用卦为含动爻的卦（上卦）
    # 动爻在下卦还是上卦？若动爻位置1-3为下卦，4-6为上卦
    if moving_line <= 3:
        ti_num = upper_num  # 体卦为下卦？传统以静为体，动为用，动爻所在的卦为用
        # 一般体为下卦（不动的），用为上卦（动的），但这里动在下卦，则体为上卦
        # 故：若动爻在下卦，则用卦为下卦，体卦为上卦
        ti_num = upper_num
        yong_num = lower_num
    else:
        ti_num = lower_num
        yong_num = upper_num

    ti_info = TRIGRAM_MAP[ti_num]
    yong_info = TRIGRAM_MAP[yong_num]
    ti_wuxing = ti_info["wuxing"]
    yong_wuxing = yong_info["wuxing"]
    # 生克关系
    wuxing_cycle = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}  # 生
    # 判断体用生克
    sheng = wuxing_cycle.get(ti_wuxing) == yong_wuxing  # 体生用
    ke = (wuxing_cycle.get(ti_wuxing) == yong_wuxing)  # 体克用？需定义: 体克用: 体克用是体胜用
    # 更准确：用生体、用克体、体生用、体克用
    ti_sheng_yong = (wuxing_cycle.get(ti_wuxing) == yong_wuxing)
    yong_sheng_ti = (wuxing_cycle.get(yong_wuxing) == ti_wuxing)
    ti_ke_yong = (wuxing_cycle.get(ti_wuxing) == yong_wuxing)  # 此逻辑不完整
    # 使用五行相克: 木克土, 土克水, 水克火, 火克金, 金克木
    ke_map = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    ti_ke_yong = (ke_map.get(ti_wuxing) == yong_wuxing)
    yong_ke_ti = (ke_map.get(yong_wuxing) == ti_wuxing)

    relation = ""
    if yong_sheng_ti:
        relation = "用生体（吉）"
    elif ti_sheng_yong:
        relation = "体生用（泄气，凶）"
    elif yong_ke_ti:
        relation = "用克体（凶）"
    elif ti_ke_yong:
        relation = "体克用（吉）"
    else:
        relation = "体用比和（吉）"

    return {
        "ben_gua": ben_gua,
        "bian_gua": bian_gua,
        "hu_gua": hu_gua,
        "ti_num": ti_num,
        "ti_name": ti_info["name"],
        "ti_wuxing": ti_wuxing,
        "yong_num": yong_num,
        "yong_name": yong_info["name"],
        "yong_wuxing": yong_wuxing,
        "relation": relation,
        "ben_lines": ben_lines,   # 六爻列表0-5
        "bian_lines": bian_lines,
    }