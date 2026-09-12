"""验证提示词的任务要求、原文保留和问题校验，不调用 LLM。"""

import pytest

from operations import (
    build_explain_prompt,
    build_question_prompt,
    build_summarize_prompt,
)


FILE_TEXT = "  # Python 笔记\n\n缩进表示代码块。🐍\n\tprint('hello')\n  "


def test_summarize_prompt():
    prompt = build_summarize_prompt(FILE_TEXT)

    instruction, content = prompt.split("\n\n文件内容：\n", maxsplit=1)
    assert "总结" in instruction
    assert "主要观点" in instruction
    assert content == FILE_TEXT


def test_explain_prompt():
    prompt = build_explain_prompt(FILE_TEXT)

    instruction, content = prompt.split("\n\n文件内容：\n", maxsplit=1)
    assert "初学者" in instruction
    assert "解释" in instruction
    assert "关键概念" in instruction
    assert content == FILE_TEXT


@pytest.mark.parametrize(
    "question", ["缩进有什么作用？\n请举例。", " \t缩进有什么作用？\n请举例。\n\u3000"]
)
def test_question_prompt_preserves_file_and_trims_question(question):
    prompt = build_question_prompt(FILE_TEXT, question)

    instruction, remainder = prompt.split("\n\n文件内容：\n", maxsplit=1)
    content, rendered_question = remainder.rsplit("\n\n问题：\n", maxsplit=1)
    assert "仅根据以下文件内容回答问题" in instruction
    assert "没有足够信息，请明确说明" in instruction
    assert content == FILE_TEXT
    assert rendered_question == "缩进有什么作用？\n请举例。"


@pytest.mark.parametrize("question", ["", "   ", "\n", "\t\r\n ", "\u3000"])
def test_blank_question_is_rejected(question):
    with pytest.raises(ValueError, match="问题不能为空"):
        build_question_prompt(FILE_TEXT, question)
