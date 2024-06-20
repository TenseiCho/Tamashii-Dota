# It gets to the end of the terminal and quote on quote launches Dota but it doesn't show the GUI.

import steam.client
from steam.enums import EPersonaState, EChatEntryType
from steam.client import SteamClient
from dota2.client import Dota2Client
from credentials import USERNAME, PASSWORD
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Steam client instance
client = SteamClient()
dota = Dota2Client(client)

@client.on('connected')
def handle_connected():
    """Handle successful connection to Steam."""
    logger.info('Connected to Steam')
    try:
        client.login(username=USERNAME, password=PASSWORD)
    except steam.client.LoginError as e:
        logger.error(f'Failed to log in: {e}')
        client.disconnect()

@client.on('logged_on')
def handle_logged_on():
    """Handle successful login to Steam and launch Dota 2."""
    logger.info('Logged in successfully!')
    client.games_played([570])  # 570 is the app ID for Dota 2
    client.change_status(persona_state=EPersonaState.Online)

    try:
        dota.launch()
        logger.info('Launching Dota 2...')
    except Exception as e:
        logger.error(f'Failed to launch Dota 2: {e}')
        return

    # Wait for the Dota 2 game client to be ready with a timeout
    timeout = 60  # Timeout in seconds
    start_time = time.time()
    while not dota.ready:
        if time.time() - start_time > timeout:
            logger.error('Timed out waiting for Dota 2 game client to be ready')
            return
        logger.info('Waiting for Dota 2 game client to be ready...')
        time.sleep(5)  # Wait for 5 seconds before checking again

    logger.info('Dota 2 game client is ready')
    join_chat_channel("tamashii")

def join_chat_channel(channel_name):
    """Join a specified Dota 2 chat channel."""
    try:
        channel = dota.channels.join_channel(channel_name)
        logger.info(f'Joined the "{channel_name}" chat channel')
    except Exception as e:
        logger.error(f'Failed to join the "{channel_name}" chat channel: {e}')

@dota.on('chat_message')
def handle_chat_message(channel, msg):
    """Handle incoming chat messages and respond to commands."""
    logger.info(f'Received message: {msg}')
    if msg.startswith('!hello'):
        dota.channels.send_message(channel, f'Hello, {msg.split(" ", 1)[1]}!')
    elif msg.startswith('!help'):
        dota.channels.send_message(channel, 'Available commands: !hello, !help')
    # Add more commands and bot functionality here

if __name__ == "__main__":
    logger.info('Connecting to Steam...')
    try:
        client.connect()
        logger.info('Running the bot...')
        client.run_forever()
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    finally:
        client.disconnect()