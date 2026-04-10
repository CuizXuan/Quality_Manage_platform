from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import cases, environments, scenarios, logs, folders, proxy

app = FastAPI(title="Quality Manage Platform - API Debug Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(proxy.router, prefix="/proxy", tags=["Proxy"])
app.include_router(cases.router)
app.include_router(environments.router)
app.include_router(scenarios.router)
app.include_router(logs.router)
app.include_router(folders.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Quality Manage Platform API", "version": "1.0.0"}
