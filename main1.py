from loguru import logger
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()


@app.get('/')
async def check():
    logger.info('Alive')
    return 'Alive'


@app.get("/get_ip_address")
async def test(request: Request):
    print(request.headers)
    print(request.client)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9500)
