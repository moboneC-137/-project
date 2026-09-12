"""读取环境变量，调用 OpenAI，并返回生成的文本。"""

import os

import openai

DEFAULT_MODEL = "gpt-5-mini"
REQUEST_TIMEOUT = 30.0


def generate_text(prompt: str) -> str:
    """发送非空提示词；返回完整回答，失败时报告简短错误。"""
    if not prompt.strip():
        raise ValueError("提示词不能为空。")

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("请先设置环境变量 OPENAI_API_KEY。")

    model = os.environ.get("CONTEXTAI_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise ValueError("CONTEXTAI_MODEL 不能为空，请填写模型名称或取消该变量。")

    try:
        with openai.OpenAI(
            api_key=api_key,
            timeout=REQUEST_TIMEOUT,
            max_retries=0,
        ) as client:
            response = client.responses.create(model=model, input=prompt)
    except openai.APITimeoutError as e:
        raise RuntimeError("AI 请求超时，请稍后重试。") from e
    except openai.AuthenticationError as e:
        raise RuntimeError("API 身份验证失败，请检查 OPENAI_API_KEY。") from e
    except openai.RateLimitError as e:
        raise RuntimeError("API 请求受限，请检查账户额度或稍后重试。") from e
    except openai.APIConnectionError as e:
        raise RuntimeError("无法连接 OpenAI，请检查网络连接。") from e
    except openai.APIError as e:
        raise RuntimeError("AI 请求失败，请检查模型配置和请求内容，或稍后重试。") from e

    if getattr(response, "status", None) != "completed":
        raise RuntimeError("AI 未完成回答，请稍后重试。")

    try:
        text = response.output_text
    except (AttributeError, TypeError) as e:
        raise RuntimeError("AI 返回了无法解析的文本响应。") from e

    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("AI 没有返回有效文本，请重试或调整问题。")

    return text
