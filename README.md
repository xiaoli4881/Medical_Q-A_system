# 🩺 Medical Q&A System

本项目是一个基于 **RAG（Retrieval-Augmented Generation）** 的医疗智能问答系统，包含前后端两部分。  
系统可通过自然语言查询医学相关问题，并基于知识库提供精准回答。

---

## 📂 项目结构

```
Medical_Q-A_system-main/
├── LICENSE
├── medical_system_back/         # 后端代码
│   └── rag_api/
│       ├── A.db                 # 数据库文件
│       ├── run.py               # 后端启动入口
│       ├── requirements.txt     # Python 依赖
│       └── app/
│           ├── main.py          # FastAPI 主程序
│           ├── config.py        # 配置文件
│           ├── db.py            # 数据库连接
│           ├── models.py        # 数据模型定义
│           ├── routers/         # 接口路由
│           │   ├── message.py   # 聊天记录接口
│           │   ├── session.py   # 会话管理接口
│           │   └── upload.py    # 文档上传接口
│           └── services/        # 服务逻辑层
│               ├── chat.py      # 聊天逻辑
│               ├── pdf.py       # PDF 文档解析
│               └── rag.py       # 检索增强生成 (RAG) 核心逻辑
│
└── medical_system_front/        # 前端代码 (Vue 3 + TypeScript)
    ├── src/
    │   ├── App.vue
    │   ├── main.ts
    │   └── assets/              # 图片与样式
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

---

## 🚀 后端运行方式

### 1️⃣ 创建虚拟环境并安装依赖

```bash
cd medical_system_back/rag_api
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ 启动 FastAPI 服务

```bash
python run.py
```

默认运行在：  
👉 `http://127.0.0.1:8000`

你也可以访问：  
- `http://127.0.0.1:8000/docs` 查看 Swagger API 文档。

---

## 💻 前端运行方式

```bash
cd medical_system_front
npm install
npm run dev
```

默认启动后访问：  
👉 `http://127.0.0.1:5173`

---

## 🔗 前后端联调说明

前端会通过 Axios 调用后端接口。  
在 `medical_system_front/src` 中可根据需要修改后端地址：

```ts
// 示例
const BASE_URL = "http://127.0.0.1:8000";
```

---

## 🧠 技术栈

### 后端
- FastAPI
- SQLite3
- RAG（Retrieval-Augmented Generation）
- LangChain / SentenceTransformer
- Pydantic
- Uvicorn

### 前端
- Vue 3
- TypeScript
- Vite
- Axios
- Tailwind / Element Plus（可选）

---

## 📘 项目亮点

- ✅ 支持医学文档上传与问答  
- ✅ 支持上下文连续对话  
- ✅ 采用 RAG 技术融合检索与生成，提高回答准确率  
- ✅ 前后端分离结构，易扩展与部署  

---

## 📜 许可证

本项目遵循 MIT License。详情见 [LICENSE](LICENSE)。

---

## ✨ 作者信息

**Medical Q&A System Team**  
weidongli@hubu.stu.edu.cn
