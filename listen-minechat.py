import argparse
import asyncio
from datetime import datetime

import aiofiles


async def tcp_echo_client(host, port, history_file):
    reader, writer = await asyncio.open_connection(host, port)

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

    # print('Close the connection')
    # writer.close()
    # await writer.wait_closed()


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


def main():
    parser = create_parser()
    parser_args = parser.parse_args()
    asyncio.run(tcp_echo_client(parser_args.host, parser_args.port, parser_args.history))


if __name__ == '__main__':
    main()
