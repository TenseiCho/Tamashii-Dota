# Stops at Logged in successfully from ChatGPT
import steam.client
from steam.enums import EPersonaState
from steam.client import SteamClient
from dota2.client import Dota2Client
from credentials import USERNAME, PASSWORD
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Steam and Dota 2 client instances
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

    # Launch Dota 2 client
    dota.launch()

@dota.on('ready')
def dota_ready():
    logger.info('Dota 2 client is ready.')

    # Join the "tamashii" chat channel
    channel_name = "tamashii"
    try:
        dota.join_chat(channel_name)
        logger.info(f'Joined the "{channel_name}" chat channel')
    except Exception as e:
        logger.error(f'Failed to join the "{channel_name}" chat channel: {str(e)}')

@dota.on('not_ready')
def dota_not_ready():
    logger.error('Dota 2 client is not ready.')

# Handle chat messages
@dota.on('chat_message')
def handle_chat_message(channel, sender, message):
    logger.info(f'Received message from {sender}: {message}')
    if message.startswith('!hello'):
        dota.send_channel_message(channel, f'Hello, {sender}!')
    elif message.startswith('!help'):
        dota.send_channel_message(channel, 'Available commands: !hello, !help')
    # Add more commands and bot functionality here

# Connect to Steam
logger.info('Connecting to Steam...')
client.connect()

# Run the client
logger.info('Running the bot...')
client.run_forever()