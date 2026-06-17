"""
core/qimen/render.py - 将排盘结果转换为展示数据（可后续优化）
"""

def render_for_display(pan_result: dict) -> dict:
    """
    输入：paipan 返回的结果字典
    输出：适合 UI 展示的字典，比如添加吉凶标签等。
    目前直接返回原字典。
    """
    # 可在此进行吉凶判断等处理，为每个宫添加颜色标记
    return pan_result