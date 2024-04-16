import asyncio


async def tcp_echo_client(host, port, token):
    reader, writer = await asyncio.open_connection(host, port)
    reply = await reader.read(200)

    writer.write((token + '\n').encode())
    await writer.drain()

    reply = await reader.read(200)

    message = 'Hello, minechat!'
    writer.write((message + '\n\n').encode())
    await writer.drain()


def main():
    host = 'minechat.dvmn.org'
    port = 5050
    token = '41a5fac8-fc13-11ee-aae7-0242ac110002'
    asyncio.run(tcp_echo_client(host, port, token))


if __name__ == '__main__':
    main()
