#!/usr/bin/python3
# File: main.py
from fastapi import FastAPI
import uvicorn
from src.db import db
from asyncio import create_subprocess_shell, subprocess
from fastapi.middleware.cors import CORSMiddleware


def init_app():
    """Initialize app"""
    app = FastAPI(version="1.0.0")
    origins = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost",
        "http://localhost:8080",
        "*"
    ]

    @app.on_event("startup")
    async def startup():
        try:
            await db.connect()
            print("✅ Database Connected!")
        except:
            print("❌ An error has occured")

    @app.on_event("shutdown")
    async def shutdown():
        await db.disconnect()

    from src import api
    app.add_middleware(CORSMiddleware,
                       allow_origins=origins,
                       allow_credentials=True,
                       allow_methods=["*"],
                       allow_headers=["*"],)
    app.include_router(api)
    return app


app = init_app()

if __name__ == "__main__":
    uvicorn.run('src.main:app', host="0.0.0.0", port=8000, reload=True)
