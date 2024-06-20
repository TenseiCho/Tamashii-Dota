# ERROR:__main__:Dota 2 is not in the bot's Steam library!
import steam.client
from steam.enums import EPersonaState, EChatEntryType
from steam.client import SteamClient
from dota2.client import Dota2Client
from credentials import USERNAME, PASSWORD
import logging
import time
import psutil
import subprocess

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

def check_dota2_license(max_attempts=3):
    for attempt in range(max_attempts):
        if 570 in client.licenses:
            logger.info("Dota 2 license found!")
            return True
        logger.warning(f"Dota 2 license not found. Attempt {attempt + 1}/{max_attempts}")
        client.request_license_info()
        time.sleep(5)
    return False

@client.on('logged_on')
def handle_logged_on():
    """Handle successful login to Steam and launch Dota 2."""
    logger.info('Logged in successfully!')
    
    # Check if Dota 2 is in the library
    if 570 not in client.licenses:
        logger.error("Dota 2 is not in the bot's Steam library!")
        return

    client.games_played([570])  # 570 is the app ID for Dota 2
    client.change_status(persona_state=EPersonaState.Online)

    launch_attempts = 3
    for attempt in range(launch_attempts):
        try:
            logger.info(f'Attempting to launch Dota 2 (Attempt {attempt + 1}/{launch_attempts})...')
            dota.launch()
            logger.info('Dota 2 launch command sent successfully.')
            
            # Wait for the Dota 2 process to start
            timeout = 60  # 60 seconds timeout for process start
            start_time = time.time()
            while time.time() - start_time < timeout:
                if is_dota2_running():
                    logger.info("Dota 2 process detected!")
                    break
                time.sleep(1)
            
            if not is_dota2_running():
                logger.warning("Dota 2 process not detected after launch attempt.")
                continue
            
            # Wait for the Dota 2 game client to be ready
            timeout = 120  # 120 seconds timeout for client ready
            start_time = time.time()
            while not dota.ready:
                if time.time() - start_time > timeout:
                    logger.error('Timed out waiting for Dota 2 game client to be ready')
                    break
                logger.info('Waiting for Dota 2 game client to be ready...')
                logger.info(f'Dota2Client ready state: {dota.ready}')
                logger.info(f'Is Dota 2 process running: {is_dota2_running()}')
                logger.info(f'Steam client state: {client.state}')
                time.sleep(5)

            if dota.ready:
                logger.info('Dota 2 game client is ready')
                join_chat_channel("tamashii")
                return
        except Exception as e:
            logger.error(f'Failed to launch Dota 2: {e}')
    
    logger.error("Failed to launch Dota 2 after multiple attempts.")
    diagnose_dota2_status()

def is_dota2_running():
    """Check if Dota 2 process is running."""
    return "dota2.exe" in (p.name().lower() for p in psutil.process_iter())

def diagnose_dota2_status():
    """Perform diagnostics on Dota 2 status."""
    logger.info("Performing Dota 2 diagnostics...")
    
    logger.info(f"Steam client state: {client.state}")
    logger.info(f"Dota 2 in library: {570 in client.licenses}")
    logger.info(f"Is Dota 2 process running: {is_dota2_running()}")
    
    # List all running processes
    logger.info("Listing all running processes:")
    for proc in psutil.process_iter(['name', 'status']):
        if 'dota' in proc.info['name'].lower() or 'steam' in proc.info['name'].lower():
            logger.info(f"Process: {proc.info['name']}, Status: {proc.info['status']}")
    
    # Check Steam status
    steam_status = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq steam.exe'], capture_output=True, text=True)
    logger.info(f"Steam process status:\n{steam_status.stdout}")

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