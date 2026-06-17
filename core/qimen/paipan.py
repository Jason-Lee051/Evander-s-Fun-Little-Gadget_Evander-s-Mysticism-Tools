"""
core/qimen/paipan.py - 奇门遁甲时家排盘核心算法
依赖：datetime, core.qimen.calendar
"""

import datetime
from typing import Dict, Any
from core.qimen.calendar import (
    day_ganzhi, hour_ganzhi, get_solar_terms, find_ju_and_dun,
    TIAN_GAN, DI_ZHI, JIA_ZI
)

# 九宫顺序
GONG_ORDER = [1, 8, 3, 4, 9, 2, 7, 6]  # 八宫（不含5）
GONG_ORDER_FULL = [1, 8, 3, 4, 5, 9, 2, 7, 6]

# 地盘干顺序
DI_PAN_ORDER = ['戊', '己', '庚', '辛', '壬', '癸', '丁', '丙', '乙']
# 九星名称
STAR_NAMES = ['天蓬', '天芮', '天冲', '天辅', '天禽', '天心', '天柱', '天任', '天英']
# 八门名称
DOOR_NAMES = ['休门', '生门', '伤门', '杜门', '景门', '死门', '惊门', '开门']
# 八神名称
SHEN_NAMES = ['值符', '腾蛇', '太阴', '六合', '白虎', '玄武', '九地', '九天']

# 星、门、神对应旬首的起始
XUN_SHOU_MAP = {
    '甲子': ('天蓬', '休门'),
    '甲戌': ('天芮', '死门'),
    '甲申': ('天冲', '伤门'),
    '甲午': ('天辅', '杜门'),
    '甲辰': ('天禽', '死门'),  # 中五寄坤二，门随死门
    '甲寅': ('天心', '开门'),
}

# 星、门原宫位
STAR_BASE_GONG = {'天蓬':1, '天芮':2, '天冲':3, '天辅':4, '天禽':5, '天心':6, '天柱':7, '天任':8, '天英':9}
DOOR_BASE_GONG = {'休门':1, '死门':2, '伤门':3, '杜门':4, '景门':9, '惊门':7, '开门':6, '生门':8}


def pai_pan(current_dt: datetime.datetime, matter: str = "", location: str = "") -> Dict[str, Any]:
    """
    执行奇门遁甲时家排盘，返回结果字典。
    current_dt: 当前时间（本地时间）
    matter, location: 用户输入的事项和位置
    """
    # 1. 节气与用局
    year = current_dt.year
    terms = get_solar_terms(year)
    # 如果靠近年尾，可能需要下一年的节气，此处简化，以当前年份计算
    dun_type, ju, jieqi, yuan = find_ju_and_dun(current_dt, terms)

    # 2. 日柱时柱
    day_gz_idx, day_gz = day_ganzhi(current_dt.date())
    hour = current_dt.hour
    hour_gz_idx, hour_gz = hour_ganzhi(day_gz_idx, hour)
    hour_tg = TIAN_GAN[hour_gz_idx % 10]
    hour_dz = DI_ZHI[hour_gz_idx % 12]

    # 3. 地盘干排布
    di_pan = {}   # {宫数: 天干}
    start_gong = ju  # 戊的起始宫
    # 九宫顺序（阳顺阴逆）
    order = list(range(1, 10))  # 1~9
    if dun_type == '阴遁':
        order = order[::-1]
    start_idx = order.index(start_gong)
    reordered = order[start_idx:] + order[:start_idx]
    for gong, gan in zip(reordered, DI_PAN_ORDER):
        di_pan[gong] = gan

    # 4. 确定旬首、值符星、值使门
    # 找出时柱所在的旬首
    xun_shou_name = None
    for name, idx in [('甲子',0), ('甲戌',10), ('甲申',20), ('甲午',30), ('甲辰',40), ('甲寅',50)]:
        if idx <= hour_gz_idx < idx+10:
            xun_shou_name = name
            break
    zhi_fu_star, zhi_shi_door = XUN_SHOU_MAP[xun_shou_name]

    # 5. 天盘干排布：时干落宫，将旬首对应的六仪加到时干宫
    shi_gan_gong = None
    for g, gan in di_pan.items():
        if gan == hour_tg:
            shi_gan_gong = g
            break
    # 旬首六仪
    xun_shou_gan = {'甲子':'戊','甲戌':'己','甲申':'庚','甲午':'辛','甲辰':'壬','甲寅':'癸'}[xun_shou_name]
    xun_shou_gong = None
    for g, gan in di_pan.items():
        if gan == xun_shou_gan:
            xun_shou_gong = g
            break

    tian_pan = {}
    seq = DI_PAN_ORDER  # 戊己庚辛壬癸丁丙乙
    if dun_type == '阴遁':
        seq = list(reversed(seq))
    xun_idx = seq.index(xun_shou_gan)
    fly_order = list(range(1, 10))  # 1-9
    if dun_type == '阴遁':
        fly_order = fly_order[::-1]
    start_fly_idx = fly_order.index(shi_gan_gong)
    reordered_fly = fly_order[start_fly_idx:] + fly_order[:start_fly_idx]
    reordered_seq = seq[xun_idx:] + seq[:xun_idx]
    for gong, gan in zip(reordered_fly, reordered_seq):
        tian_pan[gong] = gan

    # 6. 九星排布（值符落时干宫，其余星按顺时针填满九宫）
    star_pos = {}
    star_order = STAR_NAMES  # 天蓬1 ... 天英9
    star_idx = star_order.index(zhi_fu_star)
    # 星盘一律顺排（飞宫顺序1-9）
    fly_star = list(range(1, 10))
    start_idx_star = fly_star.index(shi_gan_gong)
    reordered_star_fly = fly_star[start_idx_star:] + fly_star[:start_idx_star]
    reordered_star = star_order[star_idx:] + star_order[:star_idx]
    for gong, star in zip(reordered_star_fly, reordered_star):
        star_pos[gong] = star

    # 7. 八门排布（值使门随时支，阳顺阴逆只布八宫，中5寄坤2）
    door_base_gong = DOOR_BASE_GONG[zhi_shi_door]
    xun_shou_dz = xun_shou_name[1]  # 子/戌/申/午/辰/寅
    xun_dz_idx = DI_ZHI.index(xun_shou_dz)
    hour_dz_idx = DI_ZHI.index(hour_dz)
    offset = (hour_dz_idx - xun_dz_idx) % 12

    # 只使用八宫序列
    gong_seq_for_door = [1, 8, 3, 4, 9, 2, 7, 6]
    if dun_type == '阴遁':
        gong_seq_for_door = gong_seq_for_door[::-1]
    base = 2 if door_base_gong == 5 else door_base_gong  # 中5寄坤2
    idx = gong_seq_for_door.index(base)
    zhi_shi_gong = gong_seq_for_door[(idx + offset) % 8]

    door_pos = {}
    door_order = DOOR_NAMES  # 休生伤杜景死惊开
    start_door_idx = door_order.index(zhi_shi_door)
    ordered_doors = door_order[start_door_idx:] + door_order[:start_door_idx]
    ordered_gongs = gong_seq_for_door[gong_seq_for_door.index(zhi_shi_gong):] + \
                    gong_seq_for_door[:gong_seq_for_door.index(zhi_shi_gong)]
    for gong, door in zip(ordered_gongs, ordered_doors):
        door_pos[gong] = door
    door_pos[5] = door_pos.get(2, '')  # 中宫寄坤2

    # 8. 八神排布（值符落时干宫，阳顺阴逆，只布八宫）
    shen_pos = {}
    zhi_fu_gong_for_shen = shi_gan_gong
    if zhi_fu_gong_for_shen == 5:
        zhi_fu_gong_for_shen = 2  # 中5寄坤2

    shen_order = SHEN_NAMES  # 值符,腾蛇,太阴,六合,白虎,玄武,九地,九天
    if dun_type == '阴遁':
        shen_order = [shen_order[0]] + list(reversed(shen_order[1:]))

    gong_list = [1, 8, 3, 4, 9, 2, 7, 6]
    if dun_type == '阴遁':
        gong_list = list(reversed(gong_list))

    start_idx_shen = gong_list.index(zhi_fu_gong_for_shen)
    ordered_gongs_shen = gong_list[start_idx_shen:] + gong_list[:start_idx_shen]
    for gong, shen in zip(ordered_gongs_shen, shen_order):
        shen_pos[gong] = shen
    shen_pos[5] = ''

    # 组装九宫信息
    pan_info = []
    for gong in GONG_ORDER_FULL:
        info = {
            'gong': gong,
            'di_pan': di_pan.get(gong, ''),
            'tian_pan': tian_pan.get(gong, ''),
            'star': star_pos.get(gong, ''),
            'door': door_pos.get(gong, ''),
            'shen': shen_pos.get(gong, ''),
        }
        pan_info.append(info)

    return {
        'dun_type': dun_type,
        'ju': ju,
        'jieqi': jieqi,
        'yuan': yuan,
        'day_gz': day_gz,
        'hour_gz': hour_gz,
        'matter': matter,
        'location': location,
        'datetime': current_dt.strftime("%Y-%m-%d %H:%M"),
        'pan_info': pan_info,
    }