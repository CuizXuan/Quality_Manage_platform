# API Debug Tool

轻量级 API 调试与管理工具，支持通过粘贴 cURL / Fetch 请求快速解析并调试接口。

## 功能

- 📋 **请求解析器** — 粘贴 cURL / Fetch，自动识别并填充请求信息
- 🔧 **接口调试** — 支持 GET/POST/PUT/DELETE/PATCH，Headers/Params/Body 编辑
- 📊 **响应展示** — JSON 格式化高亮、状态码/耗时/大小统计
- 📁 **集合管理** — 接口保存到集合，形成本地文档库
- 🕐 **历史记录** — 自动保存请求历史，支持快速回放
- ⚡ **压力测试** — 循环调用 + 并发测试（开发中）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | FastAPI + httpx |
| 存储 | LocalStorage（本期）/ SQLite（后期） |

## 项目结构

```
api-debug-tool/
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── views/       # 页面
│   │   ├── stores/       # Pinia 状态
│   │   ├── api/          # API 调用
│   │   └── utils/        # 工具函数
│   ├── 启动脚本.bat
│   └── package.json
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 入口
│   │   └── routers/      # 路由
│   ├── 启动脚本.bat
│   └── requirements.txt
├── docs/                  # 设计文档
└── SPRINT-1-任务清单.md   # 开发任务
```

## 快速启动

### 1. 安装依赖

**前端**
```bash
cd frontend
npm install --registry https://registry.npmmirror.com
```

**后端**
```bash
cd backend
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2. 启动服务

**前端**（端口 3000）
```bash
cd frontend
npm run dev
```

**后端**（端口 8000）
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

或使用脚本（双击运行）：
- `frontend/启动脚本.bat`
- `backend/启动脚本.bat`

### 3. 访问

- 前端：http://localhost:3000
- 后端 API 文档：http://localhost:8000/docs

## 使用流程

1. 在 **请求解析器** 粘贴 cURL 或 Fetch 命令
2. 点击 **智能解析**，自动填充请求信息
3. 修改参数后点击 **发送**
4. 在 **响应区** 查看结果
5. 点击 💾 保存到集合

## 开发说明

- 前端请求通过后端 `/proxy` 接口转发，解决跨域问题
- 后端 `/proxy/batch` 接口支持批量转发，用于压力测试
- LocalStorage 存储集合和历史，无需数据库即可使用
