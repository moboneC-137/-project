# ContextAI V0 Plan and Progress

## How to Use This Document

这份文档同时记录 V0 的范围和开发进度。

- `- [ ]` 表示尚未完成。
- `- [x]` 表示已经完成并验证。
- 一次只推进一个小步骤。
- 只有通过该步骤的验证方法后，才把它标记为完成。
- 当前步骤完成后，再进入下一步。

## Current Status

- **Current phase:** Testing
- **Current step:** Step 4.3 - Test the CLI and errors（Phase 4 离线测试全部通过；Step 3.5 真实 API 验收仍待完成）

## Goal

ContextAI V0 是一个 Python 命令行工具。用户提供一个本地 `.txt` 或 `.md` 文件后，可以选择让 AI 总结内容、解释内容，或者针对内容提出一个问题。

V0 的目标是验证最核心的产品假设：当 AI 操作可以直接从本地文件开始时，用户是否能够用更少的步骤获得有用的结果。

## User Story

作为一名用户，我希望把本地文本文件的路径交给 ContextAI，并选择一个 AI 操作，从而无需手动打开聊天工具、上传文件和重复描述文件内容。

## Expected User Flow

1. 用户在终端中运行：

   ```bash
   python main.py notes.txt
   ```

2. 程序检查用户是否提供了文件路径，以及文件是否存在、可读取并属于支持的类型。
3. 程序读取文件内容。
4. 程序显示三个可选操作：
   - Summarize
   - Explain
   - Ask a question
5. 用户选择一个操作。
6. 如果用户选择 `Ask a question`，程序继续要求用户输入问题。
7. 程序把文件内容和用户选择的操作发送给 LLM。
8. 程序在终端中输出 LLM 返回的结果，随后程序结束运行（一次运行只执行用户选择的一个操作，不循环询问是否继续）。
9. 如果任何步骤失败，程序显示清楚、可理解的错误信息。

## V0 Scope

### Supported

- 一次处理一个本地文件。
- 支持 UTF-8 编码的 `.txt` 文件。
- 支持 UTF-8 编码的 `.md` 文件。
- 支持 `Summarize` 操作。
- 支持 `Explain` 操作。
- 支持 `Ask a question` 操作。
- 使用命令行与用户交互。
- 通过远程 LLM API 生成结果。
- 使用 `pytest` 编写自动化测试。
- 使用 Git 和 GitHub 管理源代码及版本历史。

### Not Supported

- GUI。
- Finder 或 Windows 文件右键菜单。
- PDF、Word、图片及其他文件格式。
- 同时处理多个文件。
- AI Agent 或自动执行多步骤任务。
- Local LLM。
- 数据库、聊天记录或长期记忆。
- 用户账户和登录系统。
- 文件内容修改或自动覆盖原文件。
- 流式输出、联网搜索和复杂 prompt 配置。

## Design Constraints

- 保持模块化，让命令行界面只负责接收输入和展示结果。
- 文件读取、操作构建和 LLM 调用保持相互独立，便于测试和替换。
- 不为未来功能提前实现复杂框架，只保留清晰的模块边界。
- V0 不直接修改用户文件，只读取内容并在终端输出结果。
- API key 不写入源代码，也不提交到 Git。
- 文件内容过长导致超出 LLM 上下文长度时，V0 不做截断或分段处理，按一次普通的 LLM 请求失败处理（复用错误处理逻辑）。

---

## V0 Progress Checklist

## Phase 1 - Planning

### Step 1.1 - Define the problem

- [x] 写出 ContextAI 的项目愿景。
- [x] 明确当前处理本地文件时步骤过多的问题。
- [x] 把 V0 限制为 Python CLI 工具。

**Verification:** 项目愿景、核心问题和 V0 形式已经能够用简短语言说明。

### Step 1.2 - Define the V0 scope

- [x] 定义支持的文件类型：`.txt` 和 `.md`。
- [x] 定义三个 AI 操作：Summarize、Explain、Ask a question。
- [x] 定义本版本不包含的功能。
- [x] 定义预期用户流程。
- [x] 写出初版错误场景和验收标准。

**Verification:** `Supported` 和 `Not Supported` 中不存在相互冲突的功能。

### Step 1.3 - Review and confirm the plan

- [x] 检查 Expected User Flow 是否符合预期。
- [x] 检查 Supported 是否遗漏 V0 必需功能。
- [x] 检查 Not Supported 是否混入 V0 必需功能。
- [x] 确认这份计划可以作为 V0 开发边界。

**Verification:** 用户明确确认 V0 范围，可以进入 Design 阶段。

## Phase 2 - Design

### Step 2.1 - Choose the LLM interface

- [x] 选择 V0 使用的 LLM API（选定：OpenAI）。
- [x] 确定模型名称如何配置（环境变量 `CONTEXTAI_MODEL`，默认 `gpt-5-mini`；Step 3.5 已核对官方模型文档，账户实际访问仍待真实请求验证）。
- [x] 确定 API key 使用的环境变量名称（`OPENAI_API_KEY`，沿用 `openai` 库的默认读取名）。
- [x] 明确 LLM 请求失败时应该返回什么错误（缺 key → 提示设置环境变量；请求失败/超时/限流 → 捕获后转成清楚的一句话错误，程序正常退出，不抛原始堆栈）。

**Verification:** 可以说明程序需要哪些配置，但 API key 没有出现在代码或文档示例值中。

### Step 2.2 - Design the CLI interaction

- [x] 确认启动命令为 `python main.py <file-path>`（Planning 阶段已定，本步骤确认无变化）。
- [x] 确认三个操作的选择方式（启动后打印数字菜单，用户输入 `1`/`2`/`3` 选择，不接受操作名文本）。
- [x] 确认 Ask a question 的提问方式（选 `3` 后追加一行 `input()` 读取问题；问题为空按错误处理退出，不做重试循环，和其他校验错误保持一致）。
- [x] 设计成功输出的基本格式（固定 `Result:` 前缀 + 空行 + LLM 原始文本，不加多余装饰）。
- [x] 设计错误信息和退出状态（统一 `Error: ` 前缀 + 一句话；成功退出码 0，任何错误退出码 1，不区分错误类型）。

**Verification:** 能够用一段完整的终端示例演示三种操作的交互流程。

### Step 2.3 - Design the project structure

- [x] 确定最小目录结构（补记：已在提前进行的"分文件"步骤中完成，见下方文件清单）。
- [x] 分离 CLI、文件处理和 LLM 调用职责（`main.py` / `file_reader.py` / `operations.py` / `llm_client.py` 四个空模块）。
- [x] 确定测试文件的位置（`tests/` 目录，与四个模块一一对应）。
- [x] 确定依赖和配置文件（`requirements.txt`，具体依赖等 Step 3.1 添加；配置通过环境变量，见 Step 2.1）。
- [x] 检查设计是否方便未来接入 GUI 或右键菜单（四个核心模块不依赖 CLI，未来新入口可直接 import 复用）。

**Verification:** 每个文件或模块都有单一、清楚的职责，并且没有为未来版本提前建立复杂框架。

## Phase 3 - Implementation

### Step 3.1 - Create the project skeleton

- [x] 创建经过确认的目录和空文件。
- [x] 初始化本地 Git 仓库，并完成第一次 commit（提前于原计划，覆盖 Planning 文档和文件骨架）。
- [x] 创建 Python 虚拟环境（`.venv/`，Python 3.13.5，已在 `.gitignore` 中排除）。
- [x] 添加最小依赖（`openai` + `pytest`，写入 `requirements.txt`）。
- [x] 创建 `.gitignore`，排除虚拟环境、缓存和秘密配置。
- [x] 确认最小程序可以启动（`main.py` 导入其余三个模块 + `llm_client.py` 导入 `openai`，运行退出码 0，无导入错误）。

**Verification:** 运行入口命令时程序可以正常启动，不出现导入错误。

### Step 3.2 - Accept and validate a file path

- [x] 接收命令行中的文件路径。
- [x] 处理没有提供路径的情况。
- [x] 检查路径是否存在。
- [x] 检查路径是否指向普通文件。
- [x] 检查扩展名是否为 `.txt` 或 `.md`。

**Verification:** 分别使用有效文件、不存在的文件、文件夹和不支持的文件进行手动检查。

实现与工具验证已完成：使用项目 `.venv` 运行实际 CLI，验证缺少参数、有效 `.txt` / `.md`、含空格路径、不存在的文件、文件夹、不支持的扩展名、多余参数，以及项目中的 `V0_PLAN.md`，共 9 项通过；成功退出码为 0，错误退出码为 1。

### Step 3.3 - Read the file

- [x] 使用 UTF-8 读取 `.txt` 文件。
- [x] 使用 UTF-8 读取 `.md` 文件。
- [x] 处理无法读取的文件。
- [x] 处理非 UTF-8 文件。
- [x] 处理空文件。

**Verification:** 程序能返回有效文本，并为每种失败情况显示清楚的错误。

实现与工具验证已完成：`read_file(path)` 读取 UTF-8 文本，拒绝空文件及纯空白文本，有效文本不做首尾裁剪；CLI 暂时打印读取内容供检查。使用项目 `.venv` 验证 12 项实际 CLI 场景（含读取权限不足及 Step 3.2 的回归检查）、3 项文本保留检查、1 项模拟校验后文件消失的读取错误，全部通过。以上为工具验证结果，尚未记录用户亲自运行的结果。

### Step 3.4 - Build the three AI operations

- [x] 为 Summarize 构建最小 prompt。
- [x] 为 Explain 构建最小 prompt。
- [x] 为 Ask a question 构建最小 prompt。
- [x] 拒绝空问题。
- [x] 保持 prompt 构建逻辑与 CLI 分离。

**Verification:** 给定固定文件内容时，每种操作都能生成可预测结构的 prompt。

实现与工具验证已完成：`operations.py` 提供 `build_summarize_prompt(text)`、`build_explain_prompt(text)`、`build_question_prompt(text, question)`，只返回提示词字符串。使用项目 `.venv` 验证三种提示词包含完整文件文字、问题首尾空白被清除、重复调用结果一致，以及空字符串、纯空格、换行和制表符组成的问题均被拒绝，全部通过。尚未调用 AI 或接入 CLI 菜单；以上为工具验证结果，尚未记录用户亲自运行的结果。

### Step 3.5 - Connect the LLM

- [x] 从环境变量读取 API key。
- [ ] 调用选定的 LLM API（代码和模拟测试完成，待真实请求验证）。
- [ ] 返回模型生成的文本（模拟测试通过，待取得真实回答）。
- [x] 处理 API 配置缺失。
- [x] 处理请求失败、超时和无效响应（离线模拟验证通过）。

**Verification:** 使用测试文件成功获得一次真实 LLM 响应，同时确认 API key 未被 Git 跟踪。

实现：`llm_client.generate_text(prompt)` 读取环境变量，使用 Responses API，返回 `output_text`；设置请求超时为 30 秒并关闭自动重试，拒绝未完成或空文本响应。`check_llm.py` 将 `examples/notes.txt` 读取、构建总结提示词并发送给 AI，成功打印 `Result:`，失败打印 `Error: ` 并退出 1。

离线验证：项目 `.venv` 中运行 `.venv/bin/python -m pytest -q`，8 个测试、16 个子场景通过；另外验证无密钥的实际进程无 traceback、退出 1，以及原文件读取入口正常。`.env` 被忽略且未被 Git 跟踪，当前 Git 跟踪文件未发现匹配常见 OpenAI API key 格式的内容。真实 API 验收尚未完成：当前工具进程未配置 `OPENAI_API_KEY`，用户已表示拥有密钥，待在本机终端配置后运行。

环境修复：旧 `.venv` 的部分依赖带有 `dataless` 标记，导入卡在文件读取；保留为被 Git 忽略的 `.venv-backup-step35/`，重新建立 `.venv` 并按 `requirements.txt` 安装依赖，当前验证版本为 `openai 3.12.0`、`pytest 9.1.1`。

本机 zsh 配置与真实验收（输入密钥时不回显；环境变量仅对当前终端及子进程生效）：

```zsh
read -rs 'OPENAI_API_KEY?请粘贴 API key，然后按回车：'
export OPENAI_API_KEY
printf '\n'
.venv/bin/python check_llm.py
```

官方参考：[文本生成与 output_text](https://developers.openai.com/api/docs/guides/text)、[GPT-5 mini](https://developers.openai.com/api/docs/models/gpt-5-mini)、[API 配置入门](https://developers.openai.com/api/docs/quickstart)。

### Step 3.6 - Complete the CLI flow

- [x] 显示三个操作供用户选择。
- [x] 验证用户输入的操作。
- [x] 在 Ask a question 模式中读取问题。
- [x] 把文件内容、操作和问题交给 LLM 层。
- [x] 在终端显示最终结果。
- [x] 用户错误发生时不显示未处理的 traceback。

**Verification:** 从启动命令开始，三种操作都可以完整运行到结果输出。

实现与离线验证已完成：`main.py` 在读取文件后显示数字菜单，调用 `operations.py` 构建对应提示词，再通过 `llm_client.generate_text()` 获取回答，按 `Result:` + 空行 + 原始回答输出。一次运行只执行一个操作。无效选择、空问题、文件错误、配置错误和 LLM 请求错误均以 `Error: ` 提示并退出 1；输入结束（EOF）和 Ctrl+C 也会正常报告错误。

`tests/test_cli.py` 新增 23 个测试场景：三种操作经过真实文件读取、提示词构建和 LLM 封装，仅模拟 OpenAI 客户端；同时验证输入校验、中断、缺 key 和模拟 API 超时。其中 7 个场景运行实际 CLI 子进程，确认错误退出码 1、无 traceback。运行 `.venv/bin/python -m pytest -q`，完整套件 **31 passed, 16 subtests passed**；`git diff --check` 通过。

上述为工具离线验证，未发送真实 API 请求，也不代表用户亲自运行成功。当前工具环境未配置 `OPENAI_API_KEY`，Step 3.5 的真实验收项继续保留未完成。在已配置密钥的终端运行 `.venv/bin/python main.py examples/notes.txt`，分别选择 `1`、`2`、`3` 可进行真实交互验收。下一开发步骤为 Step 4.1 文件处理测试。

## Phase 4 - Testing

### Step 4.1 - Test file handling

- [x] 测试有效 `.txt` 文件。
- [x] 测试有效 `.md` 文件。
- [x] 测试文件不存在。
- [x] 测试路径是文件夹。
- [x] 测试不支持的扩展名。
- [x] 测试空文件。
- [x] 测试非 UTF-8 文件。

**Verification:** 运行相关 `pytest` 测试，结果全部通过。

工具验证已完成：`tests/test_file_reader.py` 新增 15 个测试场景，使用 pytest 临时目录创建文件，覆盖上述七项，并检查中文及含空格路径、文本首尾空白与 Unicode 内容完整保留、纯空白文件、读取权限不足和校验后文件消失。权限不足通过模拟 `PermissionError` 确定性验证，其余场景使用实际临时文件；无需 API key 或网络，不修改用户文件。本步骤无需改动 `file_reader.py`。

运行 `.venv/bin/python -m pytest -q`，完整套件 **46 passed, 16 subtests passed**，包含新增的 15 个文件处理测试；`git diff --check` 通过。以上为工具验证结果，尚未记录用户亲自运行的结果。下一步为 Step 4.2 提示词测试；Step 3.5 真实 API 验收状态不变。

### Step 4.2 - Test AI operations

- [x] 测试 Summarize prompt。
- [x] 测试 Explain prompt。
- [x] 测试 Ask a question prompt。
- [x] 测试空问题。
- [x] 使用 mock 避免单元测试真实调用 LLM API。

**Verification:** 没有 API key 和网络连接时，单元测试仍然能够通过。

工具验证已完成：`tests/test_operations.py` 新增 9 个测试，检查总结与解释的任务要求、问答仅依据文件及信息不足时明确说明的要求、原文完整保留、问题首尾空白清除且内部换行保留，以及 5 种空问题。提示词函数直接测试；现有 CLI 和 LLM 测试中的 OpenAI 客户端使用 mock，不发送真实 API 请求。无需修改 `operations.py`。

离线验证时清除测试启动环境的 `OPENAI_API_KEY`，并通过 mock 将测试主进程的 `socket.socket.connect` 和 `connect_ex` 设置为调用即失败，再执行 `pytest.main(['-q'])`。CLI 子进程不继承 socket mock，但显式移除 API key，所测错误场景在网络请求前结束。完整套件 **55 passed, 16 subtests passed**；`git diff --check` 通过。以上为工具验证，不代表真实 LLM 回答质量已经验收。

### Step 4.3 - Test the CLI and errors

- [x] 测试没有提供命令行参数。
- [x] 测试无效操作选择。
- [x] 测试缺少 API key。
- [x] 测试模拟的 LLM API 失败。
- [x] 检查错误信息是否容易理解。
- [x] 运行完整测试套件。

**Verification:** `pytest` 全部通过，主要错误路径没有未处理异常。

本步骤复用 Step 3.6 已添加的 `tests/test_cli.py`，本次完整套件运行再次通过。复查确认缺参数、无效选择、缺 key 和模拟 API 超时均有测试；错误信息说明失败原因及可采取的操作，退出码为 1，实际 CLI 子进程错误场景无 traceback。LLM 层的认证失败、限流、连接失败和无效响应继续由 `tests/test_llm_client.py` 覆盖。Phase 4 离线测试完成，Step 3.5 真实 API 验收继续保留未完成；尚未执行 Phase 5 的 GitHub 发布。

## Phase 5 - Deployment and Version Control

### Step 5.1 - Publish to GitHub

（本地 Git 初始化和早期 commit 已提前到 Step 3.1 完成，这里只处理远端仓库。）

- [x] 复查 `.gitignore` 是否完整。
- [x] 创建 GitHub 仓库（按用户选择复用现有 `moboneC-137/-project`）。
- [x] 把本地代码发布到 GitHub（通过已连接的 GitHub 工具完成）。

**Verification:** GitHub 仓库中存在源代码，且不包含虚拟环境、缓存或 API key。

2026-09-12 发布前本地检查完成：补充 `.venv-*/`、`venv/`、`*.py[cod]` 和 `.env.*` 忽略规则，保留 `.env.example` 可提交。`git check-ignore` 确认虚拟环境及其备份、Python/pytest 缓存、`.env`、`.env.local` 和 `.DS_Store` 被排除；13 个待上传文件和当前 Git 历史未匹配到常见 OpenAI/GitHub token 或私钥标记（模式扫描不等于穷尽检查）。清除测试启动环境的 `OPENAI_API_KEY` 后运行完整套件，结果为 **55 passed, 16 subtests passed**，`git diff --check` 通过。

发布完成：复用用户选定的仓库 `https://github.com/moboneC-137/-project`，本地远端名为 `origin`。因本机 HTTPS Git 未配置登录凭据，命令行 `git push` 未成功；随后通过已连接的 GitHub 工具创建提交 `238469e` 并正常推进 `main`，保留远端原有 README、MIT License 和提交历史，同时合并 `.gitignore` 规则。通过 `git fetch` 读取该提交后，比对本地与远端完整 Git tree，SHA 均为 `2dca49b3ed474b9349f384c1ec5cb2a84dec0850`；远端共有 15 个文件，包含源码、测试、示例和依赖清单，不包含虚拟环境或缓存。原本地提交历史保留在 `local-v0-history` 分支，`main` 用于跟踪已发布的 `origin/main`。后续若使用命令行推送，仍需在本机配置 GitHub 登录。Step 3.5 的真实 API 验收状态不变；下一开发步骤为 Step 5.2 使用文档。

### Step 5.2 - Write usage documentation

- [ ] 编写安装步骤。
- [ ] 编写 API key 配置步骤。
- [ ] 编写运行示例。
- [ ] 编写测试命令。
- [ ] 记录 V0 支持和不支持的功能。

**Verification:** 在一个新的环境中，只阅读文档即可安装并运行程序。

### Step 5.3 - Add continuous integration

- [ ] 创建 GitHub Actions workflow。
- [ ] 在 workflow 中安装 Python 和项目依赖。
- [ ] 在 workflow 中运行 `pytest`。
- [ ] 验证测试成功时 workflow 通过。
- [ ] 验证测试失败时 workflow 失败。

**Verification:** GitHub 上最近一次 CI workflow 成功完成。

## Phase 6 - Monitoring and Feedback

### Step 6.1 - Run the V0 acceptance check

- [ ] 手动测试一个 `.txt` 文件。
- [ ] 手动测试一个 `.md` 文件。
- [ ] 手动测试 Summarize。
- [ ] 手动测试 Explain。
- [ ] 手动测试 Ask a question。
- [ ] 手动检查主要错误场景。
- [ ] 运行全部自动化测试。

**Verification:** 所有手动检查和自动化测试均通过。

### Step 6.2 - Collect feedback

- [ ] 记录完成一个 AI 操作所需的步骤。
- [ ] 记录输出是否对用户有帮助。
- [ ] 记录最常见的失败或困惑。
- [ ] 把新功能建议放入未来版本列表，不直接加入 V0。
- [ ] 根据反馈决定下一轮 Planning 的重点。

**Verification:** 至少形成一份简短的 V0 反馈记录和下一版本候选目标。

## V0 Final Acceptance Checklist

- [ ] `python main.py <file-path>` 可以启动程序。
- [ ] `.txt` 和 `.md` 文件可以被正确读取。
- [ ] 三个 AI 操作都可以完整运行。
- [ ] Ask a question 可以接收用户问题。
- [ ] 常见错误会显示明确的信息并正常结束。
- [ ] 核心逻辑可以在不真实调用 LLM API 的情况下测试。
- [ ] 所有 `pytest` 测试通过。
- [ ] 安装、配置、运行和测试文档完整。
- [ ] API key 未写入代码或 Git 历史。
- [ ] 代码已推送到 GitHub。
- [ ] GitHub Actions CI 运行成功。
- [ ] 用户完成 V0 验收并确认可以进入下一轮 Planning。

只有上面的项目全部完成并验证后，ContextAI V0 才算完成。
