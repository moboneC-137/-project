"""为总结、解释和提问构建提示词，返回准备发给 AI 的文字。"""


def build_summarize_prompt(text: str) -> str:
    """根据文件内容构建总结提示词。"""
    return f"请总结以下文件内容，提炼主要观点。\n\n文件内容：\n{text}"


def build_explain_prompt(text: str) -> str:
    """根据文件内容构建解释提示词。"""
    return (
        "请用适合初学者的语言解释以下文件内容，并说明其中的关键概念。"
        f"\n\n文件内容：\n{text}"
    )


def build_question_prompt(text: str, question: str) -> str:
    """根据文件内容和非空问题构建问答提示词。"""
    question = question.strip()
    if not question:
        raise ValueError("问题不能为空，请输入你想问的问题。")

    return (
        "请仅根据以下文件内容回答问题；如果文件中没有足够信息，请明确说明。"
        f"\n\n文件内容：\n{text}"
        f"\n\n问题：\n{question}"
    )
