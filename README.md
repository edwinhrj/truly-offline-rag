# 爱漫调企业私有大模型

AI Desktop App 是一个基于 Python 的桌面应用程序，集成了 Flask 后端和 Vue.js 构建的现代 Web 前端，同时通过 PyQt6 封装成一个桌面应用。该应用主要支持处理 PDF 文档、提取上下文信息并通过大语言模型实现聊天对话。

## 特性

- **AI 聊天**  
  使用增强提示（RAG：检索增强生成）机制，通过结合 PDF 中的上下文和用户查询回答问题。

- **PDF 文档处理**  
  支持上传 PDF 文件并自动解析、拆分成文本块，存储至 SQLite 数据库中供后续语义检索使用。

- **向量检索**  
  基于 Ollama 提供的嵌入模型，将文本转换为向量表示，并利用余弦相似度检索相关文档块。

- **模型管理**  
  利用 Ollama 框架自动安装、启动服务并拉取所需 AI 模型（例如 deepseek-r1:1.5b）。

- **桌面运行**  
  通过 PyQt6 启动 Flask 服务器并在 QWebEngineView 中加载前端页面，提供无缝的桌面体验。

## 项目目录结构
``` bash
rag_pipeline/
├── backend/
│   ├── init.py               # 后端包初始化（可选）
│   ├── server.py             # 主 Flask 应用，注册 API 端点（如 /api/chat, /health）
│   ├── ollama/
│   │   ├── ollama_manager.py # 管理 Ollama 安装、启动和模型拉取
│   │   ├── models_config.py  # 存储模型名称及相关配置
│   ├── pdf_helper/
│   │   ├── init.py           # 标识 pdf_helper 为包
│   │   ├── embed_model.py    # 嵌入模型（调用 Ollama /api/embed 端点获取嵌入）
│   │   ├── parse.py          # PDF 解析及文本拆分
│   │   ├── store.py          # 处理 SQLite 连接，创建虚拟表并存储 PDF 文档块
│   │   └── retrieval.py      # 查询嵌入、检索相关文本块以及构建增强提示
│   └── routes/
│       └── sqlite_routes.py  # 提供 PDF 上传和清除数据库的端点 (/sqlite/upload, /sqlite/clear)
├── frontend/
│   ├── dist/                 # Vue.js 前端构建后的静态文件
│   └── src/                  # 前端源代码
│       ├── views/
│       │   ├── Home.vue      # 系统状态与 PDF 上传页面
│       │   └── Chat.vue      # 聊天交互页面（调用 /api/chat 端点）
│       └── App.vue           # 主 Vue 应用组件
├── main.py                   # 桌面启动器：使用 PyQt6 启动 Flask 服务器并加载前端
└── packaging/
    └── build.py              # 打包脚本：使用 PyInstaller 和 npm 构建单文件可执行应用
```

## 依赖

- **后端：**
  - Python 3.x
  - Flask、Flask-CORS
  - HTTPX
  - SQLite（含 vec0 扩展，如 vec0.dll）
  - Langchain（用于 PDF 加载及文本拆分）
  - NumPy、Requests、psutil 等

- **前端：**
  - Vue.js（依赖 npm 管理）

- **桌面环境：**
  - PyQt6（GUI 与 QWebEngineView）

- **打包工具：**
  - PyInstaller
  - Node.js 与 npm

## 安装与运行

### 开发环境

1. **克隆项目并安装后端依赖**
   
   在项目根目录下创建虚拟环境，然后安装依赖：
   
   ```bash
   python -m venv venv
   source venv/bin/activate     # Linux/macOS
   venv\Scripts\activate        # Windows
   pip install -r requirements.txt
   ```
  （确保 requirements.txt 中包含所有必需的依赖库）

2. **构建前端**
   
    进入 frontend 目录，安装依赖并构建：

    ```
    cd frontend
    npm install
    npm run build
    ```

    构建后的文件将存放在 frontend/dist 下。

3. **启动应用**
    在项目根目录执行：

    ```
    python main.py
    ```

    这将启动 Flask 服务，并在桌面上打开一个窗口加载前端页面（地址 http://127.0.0.1:8080）。

### PDF 上传与文件上传

**PDF 上传**

在 Home.vue 页面中，你可以检查系统状态并通过界面上传 PDF 文件。系统会自动解析 PDF 并将文本块存入数据库中。

**文件上传**

upload.vue 页面专门用于文件上传，允许用户上传任意文件。文件上传后，将由后端处理（例如，解析、存储或其他自定义逻辑）。

**聊天交互**

在 Chat.vue 页面中输入查询，系统将基于上传的文件内容进行语义检索，并结合用户查询生成回答。

## 打包与分发
运行打包脚本以生成单文件可执行程序：
```
python packaging/build.py
```
该脚本将会：

1. 清理之前的构建文件（dist/、build/ 目录）。

2. 构建 Vue.js 前端。

3. 使用 PyInstaller 将整个应用打包成一个独立可执行文件（支持 Windows、macOS 及 Unix）。

## 其它注意事项
- **Ollama 模型管理**
    当首次运行时，请确保 Ollama 已安装并配置正确。系统将自动检测并（如有需要）下载/安装 Ollama 及所需模型。

- **数据库操作**
    PDF 上传后，系统会在 SQLite 数据库中创建虚拟向量表（使用 vec0 扩展），支持基于余弦相似度的检索。

- **反馈与调试**
    日志信息将在控制台输出，便于调试与问题排查。
