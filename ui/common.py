"""
ui/common.py - 公共绘图常量、颜色、字体、吉凶定义
"""

# 背景与线条
BG_COLOR = 'black'
LINE_COLOR = 'gold'
LINE_WIDTH = 3

# 八神颜色
JI_SHEN = {'值符', '太阴', '六合', '九天'}       # 吉神 -> 绿色
XIONG_SHEN = {'腾蛇', '白虎', '玄武', '九地'}    # 凶神 -> 红色

# 八门颜色
JI_MEN = {'休门', '生门', '开门'}                # 吉门 -> 绿色
XIONG_MEN = {'伤门', '杜门', '景门', '死门', '惊门'}  # 凶门 -> 红色

# 九星颜色（统一白色）
STAR_COLOR = 'white'

# 天干颜色：三奇乙丙丁亮金色，六仪浅灰
def get_gan_color(gan: str) -> str:
    if gan in ('乙', '丙', '丁'):
        return 'gold'
    return 'lightgray'

# 宫位文字颜色（备用）
GONG_NUMBER_COLOR = 'gray'