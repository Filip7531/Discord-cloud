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
# Section for handling the command line argument (path to the file to be sent)
if len(sys.argv) < 2:
    print("Error: No file name provided for sending.")
    print(f"Correct usage: python {sys.argv[0]} <file_path>")
    sys.exit(1)

PATH = sys.argv[1]

if not os.path.exists(PATH):
    print(f"Error: File '{PATH}' not found.")
    sys.exit(1)
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

MAX_SIZE = 10 * 1024 * 1024  # 10 MB

async def send_large_file(channel, path):
    try:
        with open("LAST_MSG.txt", "rb") as f:
            LAST_MSG_id = int(f.read().strip())
    except FileNotFoundError:
        LAST_MSG_id = None  # no file
    except ValueError:
        print("Error: Invalid value in LAST_MSG.txt")
        LAST_MSG_id = None

    if LAST_MSG_id != -1:
        LAST_MSG = await channel.fetch_message(LAST_MSG_id)

    # print("LAST_MSG = ", LAST_MSG)
    filename = os.path.basename(path)
    last_msg = None
    base, ext = os.path.splitext(os.path.basename(path))  # in, .txt


    with open(path, "rb") as f:
        part = 0
        while True:
            data = f.read(MAX_SIZE)
            if not data:
                if(LAST_MSG_id != -1):
                    LAST_MSG = await LAST_MSG.reply(str(last_msg.id) + " " + base + ext)
                else:
                    LAST_MSG = await channel.send(str(last_msg.id) + " " + base + ext)
                print("LAST_MSG.id = ", LAST_MSG.id)
                text = str(LAST_MSG.id)
                with open("LAST_MSG.txt", "wb") as F:
                    F.write(text.encode("utf-8"))
                break

            part_name = f"{base}_{part}{ext}"
            with open(part_name, "wb") as tmp:
                tmp.write(data)

            if part == 0:
                
                # first part -> normally to the channel
                last_msg = await channel.send(
                    file=discord.File(part_name)
                )
            else:
                # subsequent parts -> reply to the previously sent part
                last_msg = await last_msg.reply(
                    file=discord.File(part_name)
                )

            os.remove(part_name)
            part += 1
@cloud.event
async def on_ready():
    print(f'Logged in as {cloud.user}.')
    print(f"Attempting to send file: {PATH}")
    try:
        channel = cloud.get_channel(CHANNEL_ID)
        if not channel:
            print(f"Error: Channel with ID not found: {CHANNEL_ID}. Check if the ID is correct and the bot has access to the channel.")
            await cloud.close()
            return
        
        # nazwa_pliku_na_discordzie = os.path.basename(PATH)
        # await channel.send(file=discord.File(PATH))
        # print(f"Plik '{PATH}' został pomyślnie wysłany na kanał '{channel.name}'.")
        await send_large_file(channel, PATH)
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