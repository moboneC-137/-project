"""CLI 入口：读取文件、选择 AI 操作，并展示结果或错误信息。"""

import sys

import file_reader
import llm_client
import operations


def main() -> None:
    """程序入口，对应 `python main.py <file-path>` 这条命令。"""
    if len(sys.argv) < 2:
        print("Error: 请提供一个文件路径。用法: python main.py <file-path>")
        sys.exit(1)

    if len(sys.argv) > 2:
        print("Error: 一次只能提供一个文件路径；路径含空格时请加引号。")
        sys.exit(1)

    path_str = sys.argv[1]

    try:
        path = file_reader.validate_file(path_str)
        text = file_reader.read_file(path)

        print("请选择一个操作：")
        print("1. Summarize")
        print("2. Explain")
        print("3. Ask a question")
        choice = input("请输入 1、2 或 3：").strip()

        if choice == "1":
            prompt = operations.build_summarize_prompt(text)
        elif choice == "2":
            prompt = operations.build_explain_prompt(text)
        elif choice == "3":
            question = input("请输入你的问题：")
            prompt = operations.build_question_prompt(text, question)
        else:
            raise ValueError("无效的操作，请输入 1、2 或 3。")

        answer = llm_client.generate_text(prompt)
    except EOFError:
        print("\nError: 输入已结束，请重新运行并输入操作或问题。")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nError: 操作已取消。")
        sys.exit(1)
    except (OSError, ValueError, RuntimeError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Result:")
    print()
    print(answer)


if __name__ == "__main__":
    main()
