"""校验 .txt / .md 文件路径，并读取 UTF-8 文本。"""

from pathlib import Path

SUPPORTED_EXTENSIONS = {".txt", ".md"}


def validate_file(path_str: str) -> Path:
    """检查路径是否指向存在且扩展名受支持的普通文件。"""
    path = Path(path_str)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在：{path_str}")

    if not path.is_file():
        raise ValueError(f"路径不是普通文件：{path_str}")

    if path.suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("只支持 .txt 或 .md 文件。")

    return path


def read_file(path: Path) -> str:
    """读取已校验路径的文本；无法读取、编码错误或内容为空时报告错误。"""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise ValueError(f"文件不是有效的 UTF-8 文本：{path}") from e
    except OSError as e:
        raise OSError(f"无法读取文件，请检查读取权限以及文件是否仍然存在：{path}") from e

    if not text.strip():
        raise ValueError(f"文件内容为空或只有空白字符：{path}")

    return text
