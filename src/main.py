#!/usr/bin/python3
# File: main.py
# Author: Oluwatobiloba Light
from fastapi import FastAPI, HTTPException
import uvicorn
from src.db import db
from fastapi.middleware.cors import CORSMiddleware
from prisma import errors


def init_app():
    """Initialize app"""
    app = FastAPI(version="1.0.0")
    origins = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://localhost",
        "https://stuttern-hackathon-fe-g179.vercel.app/",
        "https://stuttern-hackathon-fe-g179.vercel.app",
    ]

    app.add_middleware(CORSMiddleware,
                       allow_origins=origins,
                       allow_credentials=True,
                       allow_methods=["GET", "POST", "PUT", "DELETE",
                                      "OPTION"],
                       allow_headers=["Content-Type", "Authorization",
                                      "WWW-AUTHENTICATE"])

    @app.on_event("startup")
    async def startup():
        try:
            await db.connect()
            print("✅ Database Connected!")
        except errors.PrismaError as e:
            print("error: ", e)
            print("❌ DB Connection failed")
            raise Exception("Database connection failed!")

    @app.on_event("shutdown")
    async def shutdown():
        await db.disconnect()

    from src import api
    app.include_router(api)
    return app


app = init_app()

if __name__ == "__main__":
    uvicorn.run('src.main:app', host="0.0.0.0", port=8000, reload=True)
