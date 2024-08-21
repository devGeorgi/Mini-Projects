import discord
import asyncio

# Bot's Token, User's ID, Server's ID, Channel's ID
TOKEN = '' # Bot's tocken here
USER_ID = 0 # User's ID here
SERVER_ID = 0 # Server's ID here
CHANNEL_ID = 0 # Channel's ID here

# Define the intents your bot will use
intents = discord.Intents.default()
intents.message_content = True

# Create an instance of a client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has logged in')
    server = client.get_guild(SERVER_ID)
    channel = server.get_channel(CHANNEL_ID)
    
    if channel:
        for _ in range(10):  # Loop to send 10 pings
            await channel.send(f'<@{USER_ID}>')  # Sends a mention in the channel
            print(f'Message sent to {channel.name} in {server.name}')
            await asyncio.sleep(1)  # Waits for 1 second before sending the next ping

client.run(TOKEN)
