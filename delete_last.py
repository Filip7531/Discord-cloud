import discord
import asyncio

# Load token and channel ID from files
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

with open("channel_id.txt", "r") as f:
    CHANNEL_ID = int(f.read().strip())

intents = discord.Intents.default()
# intents.message_content = True  # musi być włączone w panelu Discorda
# intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found!")
        return

    try:
        # Fetch the last 2 messages as a list
        messages = [msg async for msg in channel.history(limit=2)]
        if len(messages) > 1:
            last_message = messages[0]  # last message
            await last_message.delete()
            print("Deleted the last message!")
        else:
            print("No messages to delete.")
    except Exception as e:
        print("Error:", e)

    await client.close()  # stops the bot after execution

client.run(TOKEN)
