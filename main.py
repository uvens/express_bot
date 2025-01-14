import os
from http import HTTPStatus
from uuid import UUID

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from loguru import logger
# from dep import get_bot

# В этом и последующих примерах импорт из `pybotx` будет производиться
# через звёздочку для краткости. Однако, это не является хорошей практикой.
from pybotx import *

load_dotenv()
collector = HandlerCollector()

BOT_ID = os.environ.get('BOT_ID')
CTS_URL = os.environ.get('CTS_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')


@collector.command("/echo", description="Send back the received message body")
async def echo_handler(message: IncomingMessage, bot: Bot) -> None:
    await bot.answer_message(message.body)


# Сюда можно добавлять свои обработчики команд
# или копировать примеры кода, расположенные ниже.


bot = Bot(
    collectors=[collector],
    bot_accounts=[
        BotAccountWithSecret(
            # Не забудьте заменить эти учётные данные на настоящие,
            # когда создадите бота в панели администратора.
            id=UUID(BOT_ID),
            cts_url=CTS_URL,
            secret_key=SECRET_KEY,
        ),
    ],
)

app = FastAPI()
app.add_event_handler("startup", bot.startup)
app.add_event_handler("shutdown", bot.shutdown)


# На этот эндпоинт приходят команды BotX
# (сообщения и системные события).
@app.post("/command")
async def command_handler(request: Request) -> JSONResponse:
    bot.async_execute_raw_bot_command(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


# На этот эндпоинт приходят события BotX для SmartApps, обрабатываемые синхронно.
@app.post("/smartapps/request")
async def sync_smartapp_event_handler(request: Request) -> JSONResponse:
    response = await bot.sync_execute_raw_smartapp_event(
        await request.json(),
        request_headers=request.headers,
    )
    return JSONResponse(response.jsonable_dict(), status_code=HTTPStatus.OK)


# К этому эндпоинту BotX обращается, чтобы узнать
# доступность бота и его список команд.
@app.get("/status")
async def status_handler(request: Request) -> JSONResponse:
    status = await bot.raw_get_status(
        dict(request.query_params),
        request_headers=request.headers,
    )
    return JSONResponse(status)


@app.get("/token")
async def get_token() -> str:
    token = await bot.get_token(bot_id=UUID(os.environ.get('BOT_ID')))
    os.environ['TOKEN'] = token
    return token


@app.get('/')
async def check():
    logger.info('Check')
    logger.info(f'{bot.state}')
    return 'Alive'


# На этот эндпоинт приходят коллбэки с результатами
# выполнения асинхронных методов в BotX.
@app.post("/notification/callback")
async def callback_handler(request: Request) -> JSONResponse:
    await bot.set_raw_botx_method_result(
        await request.json(),
        verify_request=False,
    )
    return JSONResponse(
        build_command_accepted_response(),
        status_code=HTTPStatus.ACCEPTED,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)
