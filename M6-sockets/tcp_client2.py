import asyncio, json, struct, sys

HEADER = struct.Struct(">I")


async def write_msg(writer, obj):
    data = json.dumps(obj).encode()
    writer.write(HEADER.pack(len(data)) + data)
    await writer.drain()


async def read_msg(reader):
    raw_len = await reader.readexactly(HEADER.size)
    length, = HEADER.unpack(raw_len)
    data = await reader.readexactly(length)
    return json.loads(data)


async def main():
    reader, writer = await asyncio.open_connection("127.0.0.1", 9000)
    await write_msg(writer, {"msg": "hello", "n": 1})
    reply = await read_msg(reader)
    print("reply:", reply)
    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
