import asyncio, json, struct

HEADER = struct.Struct(">I")           # 4-byte length prefix (big-endian)


async def read_msg(reader: asyncio.StreamReader) -> dict:
    raw_len = await reader.readexactly(HEADER.size)
    (length,) = HEADER.unpack(raw_len)
    data = await reader.readexactly(length)
    return json.loads(data)


async def write_msg(writer: asyncio.StreamWriter, obj: dict) -> None:
    data = json.dumps(obj).encode()
    writer.write(HEADER.pack(len(data)) + data)
    await writer.drain()


async def handle_client(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter) -> None:
    addr = writer.get_extra_info("peername")
    try:
        while True:
            req = await read_msg(reader)
            resp = {"received": req, "server": "ok"}
            await write_msg(writer, resp)
    except (asyncio.IncompleteReadError, ConnectionResetError):
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"closed {addr}")


async def main() -> None:
    server = await asyncio.start_server(handle_client, "0.0.0.0", 9000)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
