import discord
import sys
import asyncio
import os

# Function to read a value from a file with basic error handling
def Read_from_file(FILE: str):
    try:
        with open(FILE, 'r', encoding='utf-8') as file:
            line = file.readline().strip()
        return line
    except FileNotFoundError:
        print(f"Critical error: File not found '{FILE}'.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file '{FILE}': {e}")
        return None
######################################################
if len(sys.argv) < 3:
    print("Usage: python3 Download.py <filename>")
    sys.exit(1)

WantedFile = sys.argv[1]  # first argument after the script name
# print("Plik wynikowy:", WantedFile)
OutputFile = sys.argv[2]

##########################################################


# Load the bot token and channel ID from files
BOT_TOKEN = Read_from_file("token.txt")
if BOT_TOKEN is None: sys.exit(1)

channel_id_str = Read_from_file("channel_id.txt")
if channel_id_str is None: sys.exit(1)
try:
    CHANNEL_ID = int(channel_id_str)
except ValueError:
    print(f"Error: The value in 'channel_id.txt' ('{channel_id_str}') is not a valid integer.")
    sys.exit(1)

# Initialize the Discord client
intents = discord.Intents.default()

cloud = discord.Client(intents=intents)
#


import aiohttp
import discord

async def merge_reply_chain_files(channel: discord.TextChannel, last_msg_id: int, output_file: str):
    # """
    # Merge all files from the reply-chain starting from 'last_msg_id',
    # from the top (head) message to the last one.
    # """

    # # 1️⃣ Go back through the reply-chain, collecting all message IDs
    msg_ids = []
    current_msg = await channel.fetch_message(last_msg_id)

    while True:
        msg_ids.append(current_msg.id)
        if current_msg.reference and current_msg.reference.message_id:
            try:
                current_msg = await channel.fetch_message(current_msg.reference.message_id)
            except discord.NotFound:
                print(f"Message {current_msg.reference.message_id} does not exist.")
                break
        else:
            break

    # 2️⃣ Reverse the order to start from the head
    msg_ids.reverse()

    # 3️⃣ Download and merge all files
    async with aiohttp.ClientSession() as session:
        with open(output_file, "wb") as out:
            for msg_id in msg_ids:
                msg = await channel.fetch_message(msg_id)

                if not msg.attachments:
                    raise RuntimeError(f"Wiadomość {msg_id} nie ma załącznika")

                attachment = msg.attachments[0]

                async with session.get(attachment.url) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Nie mogę pobrać {attachment.url}")

                    data = await resp.read()
                    out.write(data)

    print(f"✔ File merged into: {output_file}")
    

@cloud.event
async def on_ready():
    print(f'Logged in as {cloud.user}.')
    try:
        channel = cloud.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Error: Channel with ID not found: {CHANNEL_ID}. Check if the ID is correct and the bot has access to the channel.")
            await cloud.close()
            return
        X = int(Read_from_file("LAST_MSG.txt"))
        msg = await channel.fetch_message(X)
        found = -1
        while(True):
            text = msg.content          # "123 ABA"
            parts = text.split(maxsplit=1) 
            number = int(parts[0]) #123
            string = parts[1] #ABA



            if string == WantedFile:
                found = number
                break
            if(msg.reference is not None):
                X = msg.reference.message_id
                msg = await channel.fetch_message(X)
            else:
                break
        print("found = ", found)
        if found == -1:
            print("There is no such file :((")
            exit(1)
        channel = cloud.get_channel(CHANNEL_ID)  
        msg = await channel.fetch_message(found)
        await merge_reply_chain_files(channel, found, OutputFile)
    except discord.errors.Forbidden:
        print(f"Error: The bot does not have permissions to send messages/files to the channel {CHANNEL_ID}.")
    except Exception as e:
        print(f"An unexpected error occurred while sending the file: {e}")
    finally:
        print("Closing the bot connection.")
        await cloud.close()

async def main():
    try:
        await cloud.start(BOT_TOKEN)
    except discord.LoginFailure:
        print("[ERROR] Invalid token. Make sure you have pasted the correct bot token.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while starting the bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())