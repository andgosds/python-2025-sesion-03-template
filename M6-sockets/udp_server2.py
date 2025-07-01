import asyncio, struct, random

PKT = struct.Struct(">I")       # sequence number header


class EchoServer(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        seq, = PKT.unpack_from(data)
        payload = data[PKT.size:]
        print(f"recv {seq} from {addr} -> {payload!r}")
        # optional loss simulation
        if random.random() < 0.1:   # 10 % drop
            print("simulated drop")
            return
        # ACK = same seq, empty payload
        self.transport.sendto(PKT.pack(seq), addr)


async def main():
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        EchoServer, local_addr=("0.0.0.0", 9001))
    try:
        await asyncio.Future()      # run forever
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())
