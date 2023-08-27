import discord
import os
from twilio.rest import Client
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
MONITORED_CHANNEL_ID = int(os.getenv('MONITORED_CHANNEL_ID'))

# Initialize Discord
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Initialize Twilio
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Static data storage
user_data = {}  # A dictionary to hold Discord ID: Phone number

def save_data():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)

def load_data():
    global user_data
    try:
        with open("user_data.json", "r") as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    load_data()

@client.event
async def on_message(message):
    if message.channel.id == MONITORED_CHANNEL_ID:
        for discord_id, phone_number in user_data.items():
            message_body = f'New message from {message.author}: {message.content}'
            message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        return

    if message.content.startswith('!register'):
        _, phone_number = message.content.split()
        user_data[str(message.author.id)] = phone_number
        save_data()
        await message.channel.send(f"Registered {message.author}'s phone number.")
        
    if message.content.startswith('!unregister'):
        if str(message.author.id) in user_data:
            del user_data[str(message.author.id)]
            save_data()
            await message.channel.send(f"Unregistered {message.author}'s phone number.")

client.run(DISCORD_BOT_TOKEN)
