"""
core/llm/analyzer.py - 调用 LLM 进行分析
"""
import json
import os
from openai import OpenAI
from .prompt_templates import format_qimen_result, build_qimen_prompt

def load_config(config_path: str = "config/llm_config.json") -> dict:
    """加载 LLM 配置"""
    if not os.path.exists(config_path):
        # 返回默认配置
        return {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat",
            "max_tokens": 2000,
            "temperature": 0.7
        }
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

def analyze_qimen(result: dict, matter: str, location: str,
                  api_key: str = None, base_url: str = None, model: str = None) -> str:
    """
    对奇门排盘结果进行 AI 分析。
    参数 api_key 等若为 None，则从 config 文件读取。
    返回分析文本或错误信息。
    """
    # 读取配置
    config = load_config()
    if api_key is None:
        api_key = config.get("api_key", "")
    if base_url is None:
        base_url = config.get("base_url", "https://api.deepseek.com/v1")
    if model is None:
        model = config.get("model", "deepseek-chat")

    if not api_key:
        return "错误：未配置 API Key，请在设置中填写后再试。"

    # 格式化结果
    pan_text = format_qimen_result(result)
    prompt = build_qimen_prompt(pan_text, matter, location)

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位精通奇门遁甲的专业占卜师。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=config.get("max_tokens", 2000),
            temperature=config.get("temperature", 0.7),
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"分析失败：{str(e)}"