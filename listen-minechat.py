import argparse
import asyncio
from datetime import datetime

import aiofiles

from context_manager import managed_socket


async def tcp_echo_client(reader, history_file):
    async with aiofiles.open(history_file, 'a') as file:
        while True:
            try:
                data = await reader.read(200)
                response = data.decode('utf-8')
                print(f'Received: {response!r}')
                timelog = datetime.strftime(datetime.now(), '[%d.%m.%y %H:%M]')
                await file.write(f'{timelog} {response}')
                await file.flush()
            except UnicodeDecodeError as e:
                print(data)
            except Exception as e:
                print(str(e))


def create_parser():
    parser = argparse.ArgumentParser(
        description='This script is used for serving a microservice'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        type=str,
        help='Set host for connection',
    )
    parser.add_argument(
        '--port',
        default='80',
        type=str,
        help='Set port for connection',
    )
    parser.add_argument(
        '--history',
        default='history.txt',
        type=str,
        help='Set path to history file',
    )
    return parser


async def main():
    parser = create_parser()
    parser_args = parser.parse_args()
    host = parser_args.host
    port = parser_args.port
    history = parser_args.history

    async with managed_socket(host, port) as (reader, writer):
        await tcp_echo_client(reader, history)


if __name__ == '__main__':
    asyncio.run(main())
