import asyncio
import json
import logging

log_format = "%(levelname)s:%(name)s:%(message)s"
formatter = logging.Formatter(log_format)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger = logging.getLogger('writer')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


async def register(host, port, nickname):
    reader, writer = await asyncio.open_connection(host, port)
    reply = await reader.read(200)

    logger.debug(reply.decode())

    writer.write('\n'.encode())
    await writer.drain()

    reply = await reader.read(200)
    reply = reply.decode()
    logger.debug(reply)

    writer.write((nickname + '\n').encode())
    await writer.drain()

    reply = await reader.read(200)
    reply = reply.decode()
    logger.debug(reply)

    registration_response = json.loads(reply.split('\n')[0])
    token = registration_response['account_hash']
    return token


async def authorize(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    reply = await reader.read(200)

    logger.debug(reply.decode())

    writer.write((token + '\n').encode())
    await writer.drain()

    reply = await reader.read(200)
    reply = reply.decode()
    logger.debug(reply)
    auth_response = json.loads(reply.split('\n')[0])
    if not auth_response:
        logger.error('Authorization failed')
        print('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return
    return writer


async def submit_message(writer, message):
    writer.write((message + '\n\n').encode())
    await writer.drain()


def main():
    host = 'minechat.dvmn.org'
    port = 5050
    nickname = 'idk'
    message = 'Hello, world!'

    with open('token.txt', 'r') as file:
        token = file.readline().strip()
    if not token:
        token = asyncio.run(register(host, port, nickname))
        with open('token.txt', 'w') as file:
            file.write(token)
    else:
        writer = asyncio.run(authorize(host, port, token))
        if not writer:
            raise ConnectionError('Authorization failed')
    asyncio.run(submit_message(writer, message))


if __name__ == '__main__':
    main()
