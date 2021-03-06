from fastapi import FastAPI
from fastapi.testclient import TestClient

import asyncio
import aiormq
from schemas import RabbitBody

import os

app = FastAPI()

exchange_name = os.environ.get("EXCHANGE_NAME")
rabbitmq_host = os.environ.get("RABBITMQ_HOST")
rabbitmq_user = os.environ.get("RABBITMQ_USER")
rabbitmq_password = os.environ.get("RABBITMQ_PASSWORD")

async def push_to_rabbit(number: int):
    request = RabbitBody(number)

    connection = await aiormq.connect("amqp://{}:{}@{}/".format(rabbitmq_user, rabbitmq_password, rabbitmq_host))
    channel = await connection.channel()

    await channel.exchange_declare(
        exchange=exchange_name, exchange_type='direct'
    )

    await channel.basic_publish(
        request.encode(), 
        routing_key='fibonacci', 
        exchange=exchange_name,
        properties=aiormq.spec.Basic.Properties(
            delivery_mode=2
        )
    )

async def fibonacci(delay: int):
    a, b = 0, 1
    while True:
        await asyncio.sleep(delay)
        await push_to_rabbit(a)
        yield a
        a, b = b, a + b

fibo = fibonacci(1)

@app.get("/fibonacci/")
async def get_fibonacci_number():
    return await fibo.__anext__()