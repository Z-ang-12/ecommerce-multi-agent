import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws/chat"
    async with websockets.connect(uri) as websocket:
        # 发送一个问题
        await websocket.send("我想退货，怎么操作？")
        reply = await websocket.recv()
        print(f"🤖 客服回复：{reply}\n")
        
        # 再发一个问题（同一个连接，不需要重新建立）
        await websocket.send("物流怎么查？")
        reply = await websocket.recv()
        print(f"🤖 客服回复：{reply}\n")

asyncio.run(test())