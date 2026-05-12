import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

from api.routes import router

app = FastAPI(
    title="SHUIMUMUU 星空極光塔羅",
    description="你的每日塔羅占卜小工具",
    version="1.0.0",
)

# CORS 設定（允許所有來源，方便部署）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(router, prefix="/api")

# 靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/sw.js")
async def service_worker():
    """Service Worker（需從根目錄回應以確保 scope 正確）"""
    return FileResponse(
        "static/sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.get("/manifest.json")
async def manifest():
    """PWA Manifest"""
    return FileResponse("static/manifest.json", media_type="application/json")


@app.get("/")
async def root():
    """首頁"""
    return FileResponse("static/index.html")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
