"""Step 3.5：使用固定示例文件验证一次真实 AI 调用。"""

from pathlib import Path
import sys

import file_reader
import llm_client
import operations


def main() -> None:
    sample_path = Path(__file__).parent / "examples" / "notes.txt"

    try:
        path = file_reader.validate_file(str(sample_path))
        text = file_reader.read_file(path)
        prompt = operations.build_summarize_prompt(text)
        answer = llm_client.generate_text(prompt)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Result:")
    print()
    print(answer)


if __name__ == "__main__":
    main()
