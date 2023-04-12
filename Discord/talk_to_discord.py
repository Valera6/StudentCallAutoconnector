import json
import discord

def wait_for_the_call():
    intents = discord.Intents.default()
    intents.voice_states = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if message.content.startswith('!join'):
            channel = message.author.voice.channel
            await channel.connect()

    with open('bearer_token.json', 'r') as f:
        bearer = json.load(f)
    client.run(bearer)
