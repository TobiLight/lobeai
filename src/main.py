#!/usr/bin/python3
# File: main.py
from fastapi import FastAPI
import uvicorn
from src.db import db
from asyncio import create_subprocess_shell, subprocess


async def init_app():
    """Initialize app"""
    app = FastAPI(version="1.0.0")
    try:
        process = await create_subprocess_shell("prisma db push; prisma generate",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print(f"Command 'prisma db push; prisma generate' executed successfully.")
        else:
            print(f"Error executing command 'prisma db push; prisma generate': {stderr.decode()}")
            exit(1)  # Exit the script with an error code
    except Exception as e:
        print(f"Exception while executing command 'prisma db push; prisma generate': {e}")
        exit(1)  # Exit the script with an error code

    @app.on_event("startup")
    async def startup():
        try:
            await db.connect()
            print("✅ Database Connected!")
        except:
            print("An error has occured")

    @app.on_event("shutdown")
    async def shutdown():
        await db.disconnect()
    
    from src import api
    app.include_router(api)
    return app


app = await init_app()

if __name__ == "__main__":
    uvicorn.run('src.main:app', host="0.0.0.0", port=8000, reload=True)
