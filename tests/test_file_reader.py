"""使用临时文件验证路径校验、UTF-8 读取和失败信息。"""

from pathlib import Path

import pytest

from file_reader import read_file, validate_file


@pytest.mark.parametrize("extension", [".txt", ".md"])
def test_valid_file_preserves_text(tmp_path, extension):
    path = tmp_path / f"学习 notes{extension}"
    content = "  # Python 笔记\n\n使用缩进组织代码。🐍\n  "
    path.write_text(content, encoding="utf-8")

    validated = validate_file(str(path))

    assert validated == path
    assert read_file(validated) == content
    assert path.read_bytes() == content.encode("utf-8")


def test_missing_file(tmp_path):
    path = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError, match="文件不存在") as error:
        validate_file(str(path))

    assert str(path) in str(error.value)


def test_directory_with_supported_suffix_is_rejected(tmp_path):
    path = tmp_path / "folder.txt"
    path.mkdir()

    with pytest.raises(ValueError, match="路径不是普通文件"):
        validate_file(str(path))


@pytest.mark.parametrize("filename", ["notes.pdf", "notes", "notes.txt.exe"])
def test_unsupported_extension(tmp_path, filename):
    path = tmp_path / filename
    path.write_text("示例内容。", encoding="utf-8")

    with pytest.raises(ValueError, match=r"只支持 \.txt 或 \.md 文件"):
        validate_file(str(path))


@pytest.mark.parametrize("content", ["", "   ", "\n\t\r\n", "\u3000"])
def test_empty_or_whitespace_file(tmp_path, content):
    path = tmp_path / "empty.txt"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="文件内容为空或只有空白字符"):
        read_file(validate_file(str(path)))


@pytest.mark.parametrize("content", [b"\xff\xfe\x00", b"text\xe4\xb8"])
def test_invalid_utf8_file(tmp_path, content):
    path = tmp_path / "invalid.md"
    path.write_bytes(content)

    with pytest.raises(ValueError, match="文件不是有效的 UTF-8 文本"):
        read_file(validate_file(str(path)))


def test_permission_denied_becomes_readable_error(tmp_path, monkeypatch):
    path = tmp_path / "private.txt"
    path.write_text("示例内容。", encoding="utf-8")
    validated = validate_file(str(path))

    # 模拟操作系统拒绝读取，避免 chmod 在不同用户权限下产生不同结果。
    def deny_read(self, *args, **kwargs):
        raise PermissionError("permission denied")

    monkeypatch.setattr(Path, "read_text", deny_read)

    with pytest.raises(OSError, match="无法读取文件，请检查读取权限") as error:
        read_file(validated)

    assert str(path) in str(error.value)


def test_file_removed_after_validation(tmp_path):
    path = tmp_path / "removed.txt"
    path.write_text("示例内容。", encoding="utf-8")
    validated = validate_file(str(path))
    path.unlink()

    with pytest.raises(OSError, match="无法读取文件"):
        read_file(validated)
