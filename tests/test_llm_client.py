"""离线检查 AI 调用和错误处理，不发送真实请求。"""

from contextlib import redirect_stdout
from io import StringIO
import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import openai

import check_llm
import llm_client


class LLMClientTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-not-a-real-key"}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        factory = patch("llm_client.openai.OpenAI")
        self.factory = factory.start()
        self.addCleanup(factory.stop)
        self.client = self.factory.return_value.__enter__.return_value
        self.client.responses.create.return_value = SimpleNamespace(
            status="completed", output_text="  示例回答。\n"
        )

    def test_success_preserves_answer_and_sends_prompt(self):
        self.assertEqual(llm_client.generate_text("请总结文件。"), "  示例回答。\n")
        self.client.responses.create.assert_called_once_with(
            model="gpt-5-mini", input="请总结文件。"
        )
        self.factory.assert_called_once_with(
            api_key="test-only-not-a-real-key", timeout=30.0, max_retries=0
        )
        self.factory.return_value.__exit__.assert_called_once()

    def test_model_override(self):
        os.environ["CONTEXTAI_MODEL"] = " custom-model "
        llm_client.generate_text("测试")
        self.assertEqual(self.client.responses.create.call_args.kwargs["model"], "custom-model")

    def test_missing_or_blank_key_does_not_create_client(self):
        for value in (None, "", " \n"):
            with self.subTest(value=value):
                if value is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = value
                with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                    llm_client.generate_text("测试")
        self.factory.assert_not_called()

    def test_blank_prompt_or_model_does_not_create_client(self):
        with self.assertRaisesRegex(ValueError, "提示词不能为空"):
            llm_client.generate_text(" \n")
        os.environ["CONTEXTAI_MODEL"] = " "
        with self.assertRaisesRegex(ValueError, "CONTEXTAI_MODEL"):
            llm_client.generate_text("测试")
        self.factory.assert_not_called()

    def test_api_errors_become_safe_messages(self):
        request = Mock()
        response = Mock(request=request, status_code=400)
        cases = [
            (openai.APITimeoutError(request=request), "超时"),
            (openai.AuthenticationError("private error detail", response=response, body=None), "身份验证失败"),
            (openai.RateLimitError("private error detail", response=response, body=None), "请求受限"),
            (openai.APIConnectionError(request=request), "无法连接"),
            (openai.APIError("private error detail", request=request, body=None), "AI 请求失败"),
            (openai.APIResponseValidationError(response=response, body={}), "AI 请求失败"),
        ]
        for error, message in cases:
            with self.subTest(error=type(error).__name__):
                self.client.responses.create.side_effect = error
                with self.assertRaisesRegex(RuntimeError, message) as caught:
                    llm_client.generate_text("测试")
                self.assertNotIn("private error detail", str(caught.exception))

    def test_rejects_incomplete_or_missing_status(self):
        for status in ("incomplete", "failed", None):
            with self.subTest(status=status):
                self.client.responses.create.return_value = SimpleNamespace(
                    status=status, output_text="部分回答"
                )
                with self.assertRaisesRegex(RuntimeError, "未完成回答"):
                    llm_client.generate_text("测试")

    def test_rejects_invalid_text(self):
        for text in ("", " \n", None, 42):
            with self.subTest(text=text):
                self.client.responses.create.return_value = SimpleNamespace(
                    status="completed", output_text=text
                )
                with self.assertRaisesRegex(RuntimeError, "没有返回有效文本"):
                    llm_client.generate_text("测试")
        self.client.responses.create.return_value = SimpleNamespace(status="completed")
        with self.assertRaisesRegex(RuntimeError, "无法解析"):
            llm_client.generate_text("测试")

    def test_smoke_entry_success_and_error(self):
        output = StringIO()
        with redirect_stdout(output):
            check_llm.main()
        self.assertEqual(output.getvalue(), "Result:\n\n  示例回答。\n\n")
        self.assertIn("Python 使用缩进", self.client.responses.create.call_args.kwargs["input"])

        self.client.responses.create.side_effect = openai.APITimeoutError(request=Mock())
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as caught:
            check_llm.main()
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(output.getvalue(), "Error: AI 请求超时，请稍后重试。\n")
