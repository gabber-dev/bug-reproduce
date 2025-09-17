import asyncio
import os
from livekit import rtc, api
from dotenv import load_dotenv

load_dotenv()


def create_token(part: str):
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity(part)
        .with_name("Python Bot")
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room="test-room",
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
    )
    return token


async def sender():
    print("[SENDER] Starting sender")
    token = create_token("sender")
    url = os.getenv("LIVEKIT_URL")
    if url is None:
        raise Exception("LIVEKIT_URL environment variable not set")
    room = rtc.Room()
    await room.connect(url, token.to_jwt())
    print("[SENDER] Connected to room")
    while True:
        await asyncio.sleep(1)
        await room.local_participant.publish_data(
            b"hello from sender", reliable=True, destination_identities=["receiver"]
        )


async def receiver():
    print("[RECEIVER] Starting receiver")
    token = create_token("receiver")
    url = os.getenv("LIVEKIT_URL")
    if url is None:
        raise Exception("LIVEKIT_URL environment variable not set")
    room = rtc.Room()

    def on_data(packet: rtc.DataPacket):
        print(f"Received data: {packet}")

    room.on("data_received", on_data)

    await room.connect(url, token.to_jwt())

    print("[RECEIVER] Connected to room")

    while True:
        await asyncio.sleep(1)


async def main():
    await asyncio.gather(sender(), receiver())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Main loop error: {e}")
