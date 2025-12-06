# DesktopLobby

**让你的桌面"活"起来——与《碧蓝档案》中的学生相伴的每一天。**

DesktopLobby 是一款基于 Python 开发的桌面美化应用，灵感源自《碧蓝档案》的主界面大厅。它不仅将你喜爱的学生"值日员"带到桌面上，更通过智能对话与动态交互，为你带来真实而温暖的陪伴体验。告别原版固定的布局与台词，这里的一切由你定义：自由切换角色表情、随意调整位置与大小，更可突破预设对话的限制，借助 AI 与学生展开**轻松、自然、随心所欲**的日常聊天。

[English Version](#english-version)

## ✨ 主要特色

- **灵动角色**：支持加载多个 2D 角色，每个角色拥有独立的表情系统与平滑动画。
- **智能对话**：通过可自定义样式与位置的对话气泡，角色会与你主动交流，也随时倾听你的心声。
- **沉浸背景**：动态背景窗口将嵌入系统壁纸之上、图标之下，营造无缝的桌面沉浸感。
- **记忆永存**：所有聊天记录、角色状态与设置均安全存储于本地数据库，陪伴的点点滴滴皆可回溯。
- **AI 随心聊**：内置多款 AI 模型支持（如 qwen），并采用插件式模板设计，未来扩展新模型轻松无压力。
- **深度自定义**：通过直观的 JSON 配置文件，细致调节字体、大小、动画速度……打造独一无二的桌面伙伴。

## 🛠 技术架构

- **Python** – 核心开发语言
- **PySide6** – 现代化跨平台 GUI 框架
- **Pillow (PIL)** – 图像处理与渲染
- **pygame.mixer** – 背景音乐与音效播放
- **peewee** – 轻量级 ORM，管理 SQLite 数据库
- **ruamel.yaml** – 解析 Unity 导出的动画 YAML 文件
- **scipy & numpy** – 实现流畅的插值动画，精准还原 Unity 动画效果
- **openai / llama_cpp_python** – 支持云端与本地 AI 模型，驱动智能对话

## 🚀 快速上手

1.  **获取代码**
    ```bash
    git clone https://github.com/LjcYounger/DesktopLobby.git
    cd DesktopLobby
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

3.  **立即启动**
    ```bash
    python main.py
    ```
    你的第一位桌面伙伴即将上线！

## 🎨 个性化定制

### 🤖 添加新的 AI 模型
DesktopLobby 提供了友好的图形化配置界面，你可以直接在设置中添加并配置新的 AI 模型，无需修改代码。

### 👥 添加新角色
目前角色系统基于 Spine 动画，由于 Spine 官方运行时库尚未支持 Python，**暂无法直接添加新的 Spine 角色**。我们正在积极探索可行的技术方案，未来将支持更多角色导入方式。

## 🔌 外部输入支持
程序启动后，会在 `localhost` 上自动尝试开启 Socket 监听（端口范围 10000–10009）。你可以通过发送外部信号与程序交互，实现更灵活的自动化控制或第三方集成。

## 🌈 未来展望

1.  **多角色互动**：让桌面上的学生们能够彼此交谈，营造更生动的场景氛围。
2.  **Spine 角色支持**：计划通过内嵌 HTML 引擎（如使用 spine-ts 运行时）实现对 Spine 角色的完整支持，突破当前的技术限制。

---

<a id="english-version"></a >
# DesktopLobby

**Bring your desktop to life — everyday companionship with students from *Blue Archive*.**

DesktopLobby is a Python‑based desktop customization application inspired by the main lobby of *Blue Archive*. It brings your favorite student "duty officers" onto your desktop, offering not just a visual presence but also intelligent conversation and dynamic interaction for a genuinely warm companion experience. Move beyond the original game's fixed layouts and lines — here everything is yours to define: freely switch character expressions, adjust position and size at will, and go beyond preset dialogues to have **casual, natural, and free‑flowing** daily chats with students powered by AI.

## ✨ Features

- **Lively Characters** – Load multiple 2D characters, each with independent expression systems and smooth animations.
- **Smart Dialogue** – Characters communicate through customizable speech bubbles, initiating conversations and always ready to listen.
- **Immersive Background** – A dynamic background window embeds between your wallpaper and desktop icons, creating a seamless immersive experience.
- **Persistent Memory** – All chat history, character states, and settings are securely stored in a local database, so every moment of companionship can be revisited.
- **AI‑Powered Chats** – Built‑in support for multiple AI models (e.g., qwen) with a plugin‑style template system, making future model extensions effortless.
- **Deep Customization** – Fine‑tune fonts, sizes, animation speed, and more through intuitive JSON configuration files — create a desktop companion that is uniquely yours.

## 🛠 Tech Stack

- **Python** – Core programming language
- **PySide6** – Modern cross‑platform GUI framework
- **Pillow (PIL)** – Image processing and rendering
- **pygame.mixer** – Background music and sound effects
- **peewee** – Lightweight ORM for SQLite database management
- **ruamel.yaml** – Parses animation YAML files exported from Unity
- **scipy & numpy** – Enable smooth interpolation animations, accurately reproducing Unity animation effects
- **openai / llama_cpp_python** – Support for cloud and local AI models, powering intelligent conversations

## 🚀 Quick Start

1.  **Clone the repository**
    ```bash
    git clone https://github.com/LjcYounger/DesktopLobby.git
    cd DesktopLobby
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**
    ```bash
    python main.py
    ```
    Your first desktop companion is about to appear!

## 🎨 Customization

### 🤖 Adding New AI Models
DesktopLobby provides a user‑friendly graphical configuration interface. You can add and configure new AI models directly in the settings — no code changes required.

### 👥 Adding New Characters
The current character system is built on Spine animations. Because the official Spine runtime does not yet support Python, **adding new Spine characters directly is not currently possible**. We are actively exploring feasible technical solutions and plan to support more character import methods in the future.

## 🔌 External Input Support
After startup, the program automatically attempts to open a Socket listener on `localhost` (ports 10000–10009). You can send external signals to interact with the application, enabling more flexible automation or third‑party integration.

## 🌈 Future Plans

1.  **Multi‑character Interaction** – Allow students on the desktop to talk with each other, creating a more lively scene atmosphere.
2.  **Spine Character Support** – Plan to introduce full Spine character support by embedding an HTML engine (e.g., using spine‑ts runtime), overcoming current technical limitations.

## 📄 License
This project is licensed under the MIT License. You are welcome to use and contribute freely.

## 🤝 Contributions & Feedback
If you have ideas, find bugs, or want to contribute, feel free to open an Issue or submit a Pull Request! Let's build a better desktop companionship experience together.