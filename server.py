import asyncio
import datetime
import socket


async def handle_client(client):
    client_name = '{}:{}'.format(*client.getpeername())
    while client:
        sig = await loop.sock_recv(client, 6)
        if sig[:4] == b'SEND':
            l = int.from_bytes(sig[4:6], 'big')
            data = await loop.sock_recv(client, l)
            t = datetime.datetime.now().strftime('%H:%M:%S')
            data = data.decode('utf-8')
            blocks = data.split('*')
            for block in blocks:
                if block:
                    changes_list = block.split('|')
                    for change in changes_list:
                        if change:
                            file_path, size, action = change.split(':')
                            print(t, '{}\{}'.format(client_name, file_path), size, action)

async def run_server():
    while True:
        client, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(client))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 8080))
server.listen(8)
server.setblocking(False)

loop = asyncio.get_event_loop()
loop.run_until_complete(run_server())
