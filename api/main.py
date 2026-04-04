


import fastapi


from fastapi import FastAPI, HTTPException
app = fastapi.FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}