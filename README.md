# Discord Cloud Bot
A Discord bot that works as a "cloud" on a selected channel, allowing you to store and manage messages directly in a Discord channel.

## Requirements
- Python 3.x
- A Discord bot account and token
- The ID of the channel where the bot will operate

## Installation
1. Create a virtual environment:
python3 -m venv venv

2. Activate the virtual environment:
- On Linux / macOS:
source venv/bin/activate
- On Windows (Command Prompt):
venv\Scripts\activate.bat
- On Windows (PowerShell):
venv\Scripts\Activate.ps1

3. Install required packages:
pip install -r requirements.txt

4. Configure the bot:
- Paste your **bot token** into `token.txt`.
- Paste the **channel ID** you want to use as the "cloud" into `channel_id.txt`.

Make sure the bot is added to the server where this channel exists.

## Running the Bot
python3 app.py

The bot should start and connect to the selected channel.

## Notes
- Ensure the bot has permission to read and send messages in the channel.
- Use this channel exclusively for bot operations to avoid conflicts.
- To stop the bot, press `Ctrl+C` in the terminal.
- **Adding a file with the same name will overwrite the existing file**, so the old file will no longer be accessible.

## Special Script: delete_last.py
- The `delete_last.py` script deletes the last message sent by the bot.  
- **Use it only when necessary.**  
- After running `delete_last.py`, you must **reset all settings** and set `LAST_MSG.txt` back to `-1` to avoid issues.
