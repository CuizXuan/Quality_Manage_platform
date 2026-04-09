from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import proxy

app = FastAPI(title="API Debug Tool Backend")

# CORS 配置 - 允许前端本地调用
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有，生产环境应限制为具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(proxy.router, prefix="/proxy", tags=["Proxy"])


@app.get("/")
async def root():
    return {"message": "API Debug Tool Backend", "version": "1.0.0"}
