import asyncio, struct, time

PKT = struct.Struct(">I")
MAX_RETRY = 3
TIMEOUT = 0.5


class ClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, message: bytes):
        self.message = message
        self.seq = 1
        self.transport = None
        self.ack_event = asyncio.Event()

    def connection_made(self, transport):
        self.transport = transport
        asyncio.create_task(self.send_with_retry())

    def datagram_received(self, data, addr):
        ack, = PKT.unpack(data)
        if ack == self.seq:
            self.ack_event.set()

    async def send_with_retry(self):
        for attempt in range(1, MAX_RETRY + 1):
            pkt = PKT.pack(self.seq) + self.message
            self.transport.sendto(pkt)
            try:
                await asyncio.wait_for(self.ack_event.wait(), TIMEOUT)
                print("ACK ok")
                break
            except asyncio.TimeoutError:
                print(f"retry {attempt}")
        self.transport.close()


async def main():
    loop = asyncio.get_running_loop()
    message = b"sensor=27.3"
    await loop.create_datagram_endpoint(
        lambda: ClientProtocol(message),
        remote_addr=("127.0.0.1", 9001))

if __name__ == "__main__":
    asyncio.run(main())
