import asyncio
from datetime import datetime

import aiofiles


async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)

    async with aiofiles.open('history.txt', 'a') as file:
        while True:
            try:
                data = await reader.read(100)
                response = data.decode()
                print(f'Received: {response!r}')
                timelog = datetime.strftime(datetime.now(), '[%d.%m.%y %H:%M]')
                await file.write(f'{timelog} {response}')
                await file.flush()
            except Exception as e:
                print(str(e))

    # print('Close the connection')
    # writer.close()
    # await writer.wait_closed()

asyncio.run(tcp_echo_client())
