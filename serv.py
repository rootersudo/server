import asyncio
import random
import time
from datetime import datetime

clients = []
log_file = open("server_log.txt", "a")
sequence_number = 0

async def handle_client(reader, writer):
    global sequence_number
    client_number = len(clients) + 1
    clients.append((reader, writer))
    print(f"Client {client_number} connected")

    try:
        while True:
            data = await reader.readline()
            data = data.decode().strip()

            log_entry = f"{datetime.now().strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{data};"

            if not data:
                break

            request_number = int(data.split("[")[1].split("]")[0])

            if random.random() < 0.1:
                print(f"Ignoring request [{request_number}] from client {client_number}")
                log_entry += "(проигнорировано)"
            else:
                async with asyncio.lock:
                    response_number = sequence_number
                    sequence_number += 1
                await asyncio.sleep(random.uniform(0.1, 1))
                response = f"[{response_number}.{request_number}] PONG ({client_number})"
                writer.write((response + "\n").encode())
                await writer.drain()
                print(f"Sending response [{response_number}.{request_number}] to client {client_number}")
                log_entry += f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]};{response}"

            log_file.write(log_entry + "\n")
            log_file.flush()

    finally:
        print(f"Client {client_number} disconnected")
        clients.remove((reader, writer))
        writer.close()

async def send_keepalive():
    global sequence_number
    while True:
        await asyncio.sleep(5)
        async with asyncio.lock:
            response_number = sequence_number
            sequence_number += 1
        response = f"[{response_number}] keepalive"
        for client in clients:
            client[1].write((response + "\n").encode())
        print("Sending keepalive to all clients")
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{datetime.now().strftime('%H:%M:%S.%f')[:-3]};{response}\n")
        log_file.flush()

asyncio.lock = asyncio.Lock()

async def main():
    server = await asyncio.start_server(handle_client, "localhost", 8888)
    async with server:
        await asyncio.gather(send_keepalive(), server.serve_forever())

if __name__ == "__main__":
    asyncio.run(main())
