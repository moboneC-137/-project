"""验证完整 CLI 流程；所有 AI 请求都在本地模拟。"""

import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock

import openai
import pytest

import main


@pytest.fixture
def cli(monkeypatch, tmp_path):
    path = tmp_path / "学习 notes.md"
    path.write_text("  Python 使用缩进组织代码。\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["main.py", str(path)])
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-not-a-real-key")
    monkeypatch.delenv("CONTEXTAI_MODEL", raising=False)
    factory = MagicMock()
    monkeypatch.setattr(main.llm_client.openai, "OpenAI", factory)
    client = factory.return_value.__enter__.return_value
    client.responses.create.return_value = SimpleNamespace(
        status="completed", output_text="  示例回答。\n"
    )
    return path, factory, client


@pytest.mark.parametrize(
    "inputs,instruction",
    [
        (["1"], "请总结"),
        ([" 2 "], "请用适合初学者的语言解释"),
        (["3", "  如何组织代码？  "], "请仅根据以下文件内容回答问题"),
    ],
)
def test_three_operations(cli, monkeypatch, capsys, inputs, instruction):
    path, factory, client = cli
    reader = Mock(side_effect=inputs)
    monkeypatch.setattr("builtins.input", reader)

    main.main()

    assert reader.call_count == len(inputs)
    client.responses.create.assert_called_once()
    prompt = client.responses.create.call_args.kwargs["input"]
    assert instruction in prompt
    assert path.read_text(encoding="utf-8") in prompt
    if inputs[0] == "3":
        assert prompt.endswith("问题：\n如何组织代码？")
    output = capsys.readouterr().out
    for option in ("1. Summarize", "2. Explain", "3. Ask a question"):
        assert option in output
    assert output.endswith("Result:\n\n  示例回答。\n\n")
    assert output.count("Result:") == 1
    assert path.read_text(encoding="utf-8") == "  Python 使用缩进组织代码。\n"


@pytest.mark.parametrize("choice", ["", "0", "4", "Summarize", "1 2"])
def test_invalid_choice_does_not_call_llm(cli, monkeypatch, capsys, choice):
    monkeypatch.setattr("builtins.input", Mock(return_value=choice))
    with pytest.raises(SystemExit) as error:
        main.main()
    assert error.value.code == 1
    assert "Error: 无效的操作" in capsys.readouterr().out
    cli[1].assert_not_called()


@pytest.mark.parametrize("question", ["", " \t "])
def test_empty_question_does_not_call_llm(cli, monkeypatch, capsys, question):
    monkeypatch.setattr("builtins.input", Mock(side_effect=["3", question]))
    with pytest.raises(SystemExit) as error:
        main.main()
    assert error.value.code == 1
    assert "Error: 问题不能为空" in capsys.readouterr().out
    cli[1].assert_not_called()


@pytest.mark.parametrize("exception,message", [(EOFError, "输入已结束"), (KeyboardInterrupt, "操作已取消")])
@pytest.mark.parametrize("at_question", [False, True])
def test_interrupted_input(cli, monkeypatch, capsys, exception, message, at_question):
    inputs = ["3", exception()] if at_question else [exception()]
    monkeypatch.setattr("builtins.input", Mock(side_effect=inputs))
    with pytest.raises(SystemExit) as error:
        main.main()
    assert error.value.code == 1
    assert f"Error: {message}" in capsys.readouterr().out
    cli[1].assert_not_called()


def test_missing_key(cli, monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY")
    monkeypatch.setattr("builtins.input", Mock(return_value="1"))
    with pytest.raises(SystemExit) as error:
        main.main()
    assert error.value.code == 1
    assert "Error: 请先设置环境变量 OPENAI_API_KEY。" in capsys.readouterr().out
    cli[1].assert_not_called()


def test_api_timeout(cli, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", Mock(return_value="1"))
    cli[2].responses.create.side_effect = openai.APITimeoutError(request=Mock())
    with pytest.raises(SystemExit) as error:
        main.main()
    assert error.value.code == 1
    output = capsys.readouterr().out
    assert "Error: AI 请求超时，请稍后重试。" in output
    assert "Result:" not in output


@pytest.mark.parametrize(
    "scenario,stdin,message",
    [
        ("no_path", "", "请提供一个文件路径"),
        ("extra_path", "", "一次只能提供一个文件路径"),
        ("missing_file", "", "文件不存在"),
        ("valid_file", "4\n", "无效的操作"),
        ("valid_file", "3\n\n", "问题不能为空"),
        ("valid_file", "", "输入已结束"),
        ("valid_file", "1\n", "OPENAI_API_KEY"),
    ],
)
def test_real_process_errors(tmp_path, scenario, stdin, message):
    path = tmp_path / "notes with spaces.txt"
    path.write_text("示例文件。", encoding="utf-8")
    args = {
        "no_path": [],
        "extra_path": [str(path), str(path)],
        "missing_file": [str(tmp_path / "missing.txt")],
        "valid_file": [str(path)],
    }[scenario]
    environment = os.environ.copy()
    environment.pop("OPENAI_API_KEY", None)
    result = subprocess.run(
        [sys.executable, str(Path(main.__file__).resolve()), *args],
        input=stdin, capture_output=True, text=True, env=environment, timeout=15,
    )
    assert result.returncode == 1
    assert "Error: " in result.stdout
    assert message in result.stdout
    assert "Result:" not in result.stdout
    assert result.stderr == ""
