```markdown

\# 玄学工具箱 · 奇门遁甲排盘与 AI 分析



基于 PySide6 的奇门遁甲时家排盘桌面应用，支持九宫格可视化与 LLM 智能解盘。



!\[主界面示意](screenshot.png) <!-- 若有截图可替换 -->



\---



\## ✨ 主要特性



\- \*\*奇门遁甲排盘\*\*：自动计算节气、局数、三元，排布地盘、天盘、九星、八门、八神，九宫格彩色显示（吉凶分色）。

\- \*\*AI 智能分析\*\*：支持 OpenAI API 兼容的 LLM（如 DeepSeek），自动生成断局建议，结果可复制。

\- \*\*灵活配置\*\*：API Key、模型、温度等参数可通过界面设置，敏感配置自动忽略提交。

\- \*\*跨平台\*\*：Windows / macOS / Linux。



\---



\## 📦 安装与运行



```bash

git clone https://github.com/Jason-Lee051/Evander-s-Fun-Little-Gadget\_Evander-s-Mysticism-Tools.git

cd Evander-s-Fun-Little-Gadget\_Evander-s-Mysticism-Tools

python -m venv venv

\# Windows: venv\\Scripts\\activate

\# macOS/Linux: source venv/bin/activate

pip install -r requirements.txt

```



配置 LLM（可选）：

```bash

cp config/llm\_config.example.json config/llm\_config.json

\# 编辑 config/llm\_config.json 填入你的 API Key

```



启动：

```bash

python main.py

```



\---



\## 🧭 使用指南



1\. \*\*排盘\*\*：菜单「奇门遁甲」→「开始排盘...」，输入事项与位置，点击确定。

2\. \*\*查看盘局\*\*：九宫格显示，吉神/吉门为绿色，凶神/凶门为红色，三奇天干为金色。

3\. \*\*AI 分析\*\*：排盘后点击「🧠 智能分析」按钮，分析结果在新窗口展示，可复制全文。

4\. \*\*API 设置\*\*：菜单「设置」→「LLM API 设置...」可修改模型参数。



\---



\## 🛠 技术栈



\- PySide6 (Qt for Python)

\- ephem（天文计算）

\- openai ≥1.0

\- matplotlib（预留）



\---



\## 📂 目录结构



```

.

├── config/

│   ├── llm\_config.example.json   # 配置模板

│   └── llm\_config.json           # 实际配置（需自行创建，已忽略）

├── core/

│   ├── base.py                   # 术数基类

│   ├── llm/                      # LLM 调用与提示词

│   └── qimen/                    # 奇门排盘核心（日历、排盘、渲染）

├── ui/                           # GUI 界面（主窗口、各对话框、绘制控件）

├── main.py

├── requirements.txt

└── .gitignore

```



\---



\## ⚠️ 注意事项



\- \*\*API Key 安全\*\*：`config/llm\_config.json` 已加入 `.gitignore`，切勿提交到公开仓库。

\- Python 版本要求 ≥3.8。

\- 节气计算基于 `ephem`，精确但少数年份边界可能需要微调。



\---



\## 🔮 未来计划



\- 增加其他术数（六爻、八字等）

\- 排盘历史记录

\- 导出图片

\- 多语言支持



\---



\## 🤝 贡献



Fork → 特性分支 → 提交 → Pull Request。



\---



\## 📬 联系



\[Issue](https://github.com/Jason-Lee051/Evander-s-Fun-Little-Gadget\_Evander-s-Mysticism-Tools/issues) 或联系作者 \[Jason-Lee051](https://github.com/Jason-Lee051)。



\---



\*\*Enjoy your mystical journey!\*\* 🌟

```

