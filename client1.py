import asyncio
import random
from datetime import datetime

log_file = open("client_log.txt", "a")
client_number = 0

async def send_request(reader,writer):
    global client_number
    request_number = 0
    while True:
        await asyncio.sleep(random.uniform(0.3, 3))
        request = f"[{request_number}] PING"
        writer.write((request + "\n").encode())
        await writer.drain()
        print(f"Client {client_number + 1}: Sending request [{request_number}]")


        try:
            response = await asyncio.wait_for(reader.readline(), timeout=5)
            response = response.decode().strip()
            print(f"Client {client_number + 1}: Received response '{response}'")

            if response.startswith("[") and response.endswith("] keepalive"):
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d  ;')[:-3]};")
                log_file.write(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]};{response}\n")
            else:
                log_file.write(f"{datetime.now().strftime('%Y-%m-%d;%H:%M:%S.%f')[:-3]};{request};")
                log_file.write(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]};{response}\n")
        except asyncio.TimeoutError:
            print(f"Client {client_number + 1}: Request [{request_number}] timed out")
            log_file.write(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]};(таймаут)\n")

        request_number += 1

async def main(host, port):
    global client_number
    reader, writer = await asyncio.open_connection(host, port)
    print(f"Client {client_number + 1} connected")
    client_number += 1

    try:
        await send_request(reader,writer)
    finally:
        print(f"Client {client_number} disconnected")
        writer.close()

if __name__ == "__main__":
    asyncio.run(main("localhost", 8888))