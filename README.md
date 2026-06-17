# Evander's Mysticism Tools 玄学工具箱
基于 PySide6 开发的跨平台奇门遁甲时家排盘桌面应用，精准历法推演 + LLM 智能解盘。

本工具依托天文库精准计算二十四节气，完整实现标准时家奇门排盘逻辑；采用多线程异步计算解决 UI 主线程卡死问题，搭配年份节气缓存大幅提升重复排盘速度。内置可视化九宫盘面，支持对接所有兼容 OpenAI 协议的大模型自动断局。项目模块化分层架构，预留扩展接口，后续可新增八字、六爻等术数功能。

![主界面示意](screenshot.png)
---
## ✨ 主要特性
- **奇门遁甲完整排盘**
  自动推算节气、局数、三元，生成地盘/天盘/九星/八门/八神全量数据；九宫格可视化区分吉凶色彩（吉绿凶红、三奇金色高亮）。
- **AI 智能解盘分析**
  兼容 DeepSeek、OpenAI 等标准 API 大模型，输入预测事项与方位后一键生成通俗断局文本，分析结果支持一键复制。
- **可视化灵活配置面板**
  图形界面修改 API Key、模型名称、温度等参数；敏感密钥配置文件已加入 `.gitignore`，避免隐私泄露。
- **流畅无阻塞计算**
  使用 QThread 分离 UI 线程与天文计算，搭配节气年份缓存，首次/重复排盘均不会造成窗口卡死。
- **跨平台兼容**
  原生支持 Windows / macOS / Linux 全系统运行。

---
## 🚀 快速部署
### 1. 克隆仓库 & 初始化虚拟环境
```bash
git clone https://github.com/Jason-Lee051/Evander-s-Fun-Little-Gadget_Evander-s-Mysticism-Tools.git
cd Evander-s-Fun-Little-Gadget_Evander-s-Mysticism-Tools

# 创建虚拟环境
python -m venv venv

# Windows 激活环境
venv\Scripts\activate

# 安装全部依赖
pip install -r requirements.txt
```

### 2. 配置 LLM（可选，无需 AI 分析可跳过）
复制配置模板生成私有配置文件，填入你的大模型 API 密钥：
```bash
cp config/llm_config.example.json config/llm_config.json
# 使用文本编辑器修改 llm_config.json，填入 API Key、接口地址、模型名
```

### 3. 启动程序
```bash
python main.py
```

---
## 📖 使用指南
1. **执行排盘**
   顶部菜单「奇门遁甲」→「开始排盘...」，弹窗填写预测事项、所在位置，确认后自动后台计算盘面。
2. **查看九宫盘局**
   主窗口渲染完整奇门九宫格，吉门/吉神标记绿色，凶门/凶神标记红色，三奇天干金色突出显示。
3. **AI 智能分析**
   排盘完成后点击底部「智能分析」按钮，大模型解读结果弹出独立窗口，支持全文字复制。
4. **修改 LLM 参数**
   顶部菜单「设置」→「LLM API 设置...」，可视化修改密钥、模型、采样温度等参数。

---
## 🛠️ 技术栈
- GUI：PySide6 (Qt for Python)
- 天文历法计算：ephem
- LLM 接口：openai ≥ 1.0
- 预留绘图依赖：matplotlib

---
## 📂 项目目录结构
```
.
├── config/                  # 配置文件目录
│   ├── llm_config.example.json  # LLM 配置模板（开源提交）
│   └── llm_config.json          # 私有密钥配置（.gitignore 忽略）
├── core/                    # 核心业务逻辑
│   ├── base.py              # 术数通用抽象基类
│   ├── llm/                 # 大模型调用、提示词管理
│   └── qimen/               # 奇门遁甲核心（节气历法、排盘算法、盘面渲染）
├── ui/                      # 全部图形界面代码
│   ├── main_window.py       # 程序主窗口
│   ├── qimen_view.py        # 奇门九宫绘制控件
│   └── 各类弹窗对话框
├── assets/                  # 字体、图标静态资源
├── main.py                  # 程序入口
├── requirements.txt         # 依赖清单
└── .gitignore               # 忽略密钥、缓存、虚拟环境等文件
```

---
## ⚠️ 注意事项
1. **API 密钥安全**：`config/llm_config.json` 已写入 `.gitignore`，请勿将包含密钥的配置提交至公开仓库。
2. **Python 版本**：运行环境 Python ≥ 3.8。
3. **历法精度说明**：节气计算基于 ephem 天文库，绝大多数年份精准，极少数跨年边界日期存在微小偏差。

---
## 🔮 未来开发计划
- 新增六爻、八字等传统术数模块
- 本地排盘历史记录存储与查询
- 盘面图片导出保存功能
- 多语言界面国际化支持

---
## 🤝 贡献指南
欢迎提交功能迭代与 Bug 修复：
1. Fork 本仓库
2. 新建特性分支开发
3. 提交修改并发起 Pull Request

---
## 📮 联系与反馈
- 问题反馈：[GitHub Issues](https://github.com/Jason-Lee051/Evander-s-Fun-Little-Gadget_Evander-s-Mysticism-Tools/issues)
- 作者主页：[Jason-Lee051](https://github.com/Jason-Lee051)

**Enjoy your mystical journey! ✨**
