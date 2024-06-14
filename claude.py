# Issues with launching dota client from claude
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

# Login to the Steam account
@client.on('connected')
def handle_connected():
    logger.info('Connected to Steam')
    client.login(username=USERNAME, password=PASSWORD)

# Handle successful login
@client.on('logged_on')
def handle_logged_on():
    logger.info('Logged in successfully!')
    client.games_played([570])  # 570 is the app ID for Dota 2
    client.change_status(persona_state=EPersonaState.Online)  # Set the bot's status to online

    # Wait for the Dota 2 game client to be ready with a timeout
    timeout = 60  # Timeout in seconds
    start_time = time.time()
    while not dota.ready:
        if time.time() - start_time > timeout:
            logger.error('Timed out waiting for Dota 2 game client to be ready')
            break
        logger.info('Waiting for Dota 2 game client to be ready...')
        time.sleep(5)  # Wait for 5 seconds before checking again

    if dota.ready:
        logger.info('Dota 2 game client is ready')

        # Join the "tamashii" chat channel
        channel_name = "tamashii"
        try:
            channel = dota.channels.join_channel(channel_name)
            logger.info(f'Joined the "{channel_name}" chat channel')
        except Exception as e:
            logger.error(f'Failed to join the "{channel_name}" chat channel: {str(e)}')
    else:
        logger.error('Dota 2 game client is not ready')

# Handle chat messages
@dota.on('chat_message')
def handle_chat_message(channel, msg):
    logger.info(f'Received message: {msg}')
    if msg.startswith('!hello'):
        dota.channels.send_message(channel, f'Hello, {msg.split(" ", 1)[1]}!')
    elif msg.startswith('!help'):
        dota.channels.send_message(channel, 'Available commands: !hello, !help')
    # Add more commands and bot functionality here

# Connect to Steam
logger.info('Connecting to Steam...')
client.connect()

# Run the client
logger.info('Running the bot...')
client.run_forever()