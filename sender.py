import argparse
import asyncio
import json
import logging

from context_manager import managed_socket

BUFFER_SIZE = 200  # ensures that the message is read completely

logger = logging.getLogger('writer')


def configure_logger():
    log_format = "%(levelname)s:%(name)s:%(message)s"
    formatter = logging.Formatter(log_format)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


async def register(reader, writer, nickname):
    nickname = nickname.replace('\n', '/n')

    reply = await reader.read(BUFFER_SIZE)

    logger.debug(reply.decode())

    writer.write('\n'.encode())
    await writer.drain()

    reply = await reader.read(BUFFER_SIZE)
    reply = reply.decode()
    logger.debug(reply)

    writer.write((nickname + '\n').encode())
    await writer.drain()

    reply = await reader.read(BUFFER_SIZE)
    reply = reply.decode()
    logger.debug(reply)

    registration_response = json.loads(reply.split('\n')[0])
    token = registration_response['account_hash']

    return token


async def authorize(reader, writer, token):
    reply = await reader.read(BUFFER_SIZE)

    logger.debug(reply.decode())

    writer.write((token + '\n').encode())
    await writer.drain()

    reply = await reader.read(BUFFER_SIZE)
    reply = reply.decode()
    logger.debug(reply)
    auth_response = json.loads(reply.split('\n')[0])
    if not auth_response:
        logger.error('Authorization failed')
        print('Неизвестный токен. Проверьте его или зарегистрируйте заново.')
        return False
    return True


async def submit_message(writer, message):
    message = message.replace('\n', '/n')

    writer.write((message + '\n\n').encode())
    await writer.drain()
    logger.debug(f'Message sent: {message}')

    writer.close()
    await writer.wait_closed()


def create_parser():
    parser = argparse.ArgumentParser(
        description='This script is used for serving a microservice'
    )
    parser.add_argument(
        '--token',
        default='',
        type=str,
        help='Set token for authorization',
    )
    parser.add_argument(
        '--host',
        default='minechat.dvmn.org',
        type=str,
        help='Set host for connection',
    )
    parser.add_argument(
        '--port',
        default='5050',
        type=str,
        help='Set port for connection',
    )
    parser.add_argument(
        '--name',
        default='user',
        type=str,
        help='Set nickname for registration',
    )
    parser.add_argument(
        '--message',
        type=str,
        help='Set message for sending',
        required=True,
    )
    return parser


async def main():
    configure_logger()

    parser = create_parser()
    parser_args = parser.parse_args()

    host = parser_args.host
    port = parser_args.port
    nickname = parser_args.name
    message = parser_args.message
    token = parser_args.token

    if not token:
        with open('token.txt', 'r') as file:
            token = file.readline().strip()
    if not token:
        async with managed_socket(host, port) as (reader, writer):
            token = await register(reader, writer, nickname)
        with open('token.txt', 'w') as file:
            file.write(token)
    async with managed_socket(host, port) as (reader, writer):
        authorized = await authorize(reader, writer, token)
        if not authorized:
            raise ConnectionError('Authorization failed')
        await submit_message(writer, message)


if __name__ == '__main__':
    asyncio.run(main())
