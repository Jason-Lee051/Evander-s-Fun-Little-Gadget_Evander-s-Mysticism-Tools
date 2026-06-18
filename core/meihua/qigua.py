"""
core/meihua/qigua.py - 起卦方法（数字、时间、汉字等）
"""
import datetime
from typing import Tuple

from .bagua import TRIGRAM_MAP

def qigua_by_number(num1: int, num2: int, num3: int) -> Tuple[int, int, int]:
    """
    数字起卦：三个数字分别对应上卦数、下卦数、动爻数
    规则：上卦 = num1 % 8（余0为8），下卦 = num2 % 8，动爻 = num3 % 6（余0为6）
    返回 (上卦数, 下卦数, 动爻位置1-6)
    """
    upper = num1 % 8
    if upper == 0:
        upper = 8
    lower = num2 % 8
    if lower == 0:
        lower = 8
    moving = num3 % 6
    if moving == 0:
        moving = 6
    return upper, lower, moving

def qigua_by_time(dt: datetime.datetime) -> Tuple[int, int, int]:
    """
    时间起卦：使用年、月、日、时（地支数）计算
    年：公历年份，月：数字1-12，日：数字1-31，时：地支序数（子1...亥12）
    上卦 = (年 + 月 + 日) % 8，下卦 = (年 + 月 + 日 + 时) % 8，动爻 = (年 + 月 + 日 + 时) % 6
    注意：传统多用农历，此处简化用公历数字，如需农历请引入第三方库
    """
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    # 时辰地支序数（子时23-1为1，丑时1-3为2，... 亥时21-23为12）
    # 简化：用小时对应地支，这里取 hour//2 + 1（23点为子时）
    di_zhi = (hour + 1) // 2 % 12 + 1  # 1-12

    upper_num = (year + month + day) % 8
    if upper_num == 0:
        upper_num = 8
    lower_num = (year + month + day + di_zhi) % 8
    if lower_num == 0:
        lower_num = 8
    moving = (year + month + day + di_zhi) % 6
    if moving == 0:
        moving = 6
    return upper_num, lower_num, moving

def qigua_by_characters(text: str, mode: str = "stroke") -> Tuple[int, int, int]:
    """
    汉字起卦（测字）：按笔画数或字数
    mode: 'stroke' 笔画数（需要汉字笔画库，未实现），'word' 字数
    当前仅支持按字数：上卦 = 总字数 % 8，下卦 = 第一个字笔画（暂用1），动爻 = 总字数 % 6
    实际使用请完善笔画数
    """
    if mode == "word":
        total = len(text)
        upper = total % 8
        if upper == 0:
            upper = 8
        # 下卦可取第二个数，这里简单用第一个字的笔画数（暂为1）
        # 实际需要笔画库，此处简化
        lower = 1  # 待完善
        moving = total % 6
        if moving == 0:
            moving = 6
        return upper, lower, moving
    else:
        # 笔画数模式需映射表，本示例未实现
        raise NotImplementedError("笔画数起卦需汉字笔画数据库，暂未支持")