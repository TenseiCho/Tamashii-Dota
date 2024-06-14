# Where it all began
import steam.client
from steam.enums import EPersonaState
from dota2.client import Dota2Client
from credentials import USERNAME, PASSWORD

# Create a Steam client instance
client = steam.client.SteamClient()

# Create a Dota 2 client instance
dota = Dota2Client(client)

# Login to the Steam account
@client.on('connected')
def handle_connected():
    client.login(username=USERNAME, password=PASSWORD)

# Handle successful login
@client.on('logged_on')
def handle_logged_on():
    print('Logged in successfully!')
    client.games_played([570])  # 570 is the app ID for Dota 2
    client.change_status(persona_state=EPersonaState.Online)  # Set the bot's status to online

# Handle chat messages
@dota.on('chat_message')
def handle_chat_message(channel, sender_id, message):
    if message.startswith('!hello'):
        dota.send_message(channel, f'Hello, {sender_id}!')
    elif message.startswith('!help'):
        dota.send_message(channel, 'Available commands: !hello, !help')
    # Add more commands and bot functionality here

# Connect to Steam
client.connect()

# Run the client
client.run_forever()