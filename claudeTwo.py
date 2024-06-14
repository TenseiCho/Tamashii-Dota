import logging
from steam.client import SteamClient, EMsg
from steam.enums.emsg import EMsg
from credentials import USERNAME, PASSWORD

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dota2_chatbot")

# Create a Steam client
client = SteamClient()

# Function to handle incoming messages
def handle_message(msg):
    if msg.body.startswith("!hello"):
        respond_to_message(msg, "Hello! How can I assist you today?")
    elif msg.body.startswith("!help"):
        respond_to_message(msg, "Here are the available commands:\n!hello - Greet the chatbot\n!help - Show available commands")
    else:
        respond_to_message(msg, "Sorry, I didn't understand your message. Type !help to see the available commands.")

# Function to send a response to a message
def respond_to_message(msg, response):
    chat_channel.send_message(response)

# Event handler for the "connected" event
@client.on("connected")
def handle_connected():
    logger.info("Connected to Steam.")

# Event handler for the "chat_message" event
@client.on("chat_message")
def handle_chat_message(msg):
    if msg.channel_id == channel_id:
        handle_message(msg)

# Event handler for the "disconnected" event
@client.on("disconnected")
def handle_disconnected():
    logger.info("Disconnected from Steam.")

# Event handler for the "error" event
@client.on("error")
def handle_error(err):
    logger.error(f"Error: {repr(err)}")

# Log in to Steam
try:
    client.cli_login(USERNAME, PASSWORD)
    logger.info("Logged in to Steam.")
except Exception as e:
    logger.error(f"Failed to log in to Steam: {repr(e)}")
    exit(1)

# Get the Dota 2 game
try:
    dota2 = client.get_game(570)
    logger.info("Connected to Dota 2.")
except Exception as e:
    logger.error(f"Failed to connect to Dota 2: {repr(e)}")
    exit(1)

# Join the specified chat channel
channel_name = "tamashii"
try:
    chat_channel = dota2.join_chat_channel(channel_name)
    channel_id = chat_channel.id64
    logger.info(f"Joined chat channel: {channel_name}")
except Exception as e:
    logger.error(f"Failed to join chat channel: {repr(e)}")
    exit(1)

# Handle incoming events
try:
    client.run_forever()
except KeyboardInterrupt:
    client.logout()
    logger.info("Chatbot stopped.")