# bot.py
import os
import discord
import random
import discord.ext
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import requests
import base64
from geopy.geocoders import Nominatim
import json
import time
import threading
import asyncio
import PIL
from PIL import Image
import re
from deep_translator import GoogleTranslator, single_detection
import time as pytime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#determine root path
root_path = os.path.dirname(os.path.abspath(__file__))

MY_GUILD = discord.Object(id = 1452482779727003821)

class MyBot(commands.Bot):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyBot(intents=intents)
CHANNELid = 1304345339440136263 
global channel
channel = client.get_channel(CHANNELid)
CHANNELid2 = 1292139882629828660
channel2 = client.get_channel(CHANNELid2)
global rpchannel
rpchannel = None

#interpret weather API
grabapi = os.path.join(root_path, "SECRETAPIKEY.txt")
f = open(grabapi, "r")
code = f.read()
f.close()
b = base64.b64decode(code)
api_key = b.decode("utf-8")

def get_weather(location):
    global data
    global itbroken
    global current_weather_url
    itbroken = False
    try:
        current_weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
        response = requests.get(current_weather_url)
        data = response.json()
        itbroken = False
        return data, itbroken
    except KeyError:
        itbroken = True
        return itbroken
    
#Makes the data from the get_weather function readable
def makereadable(data):
    global temp
    global weatherdesc
    global itbroken
    try:
        #Makes the data from the get_weather function readable
        temperature = data['main']['temp']
        temp = round(temperature)
        weatherdesc = data['weather'][0]['description']
        itbroken = False
        return temp, weatherdesc, itbroken
    except KeyError:
        itbroken = True
        return itbroken

def getweather(location):
    get_weather(location)
    makereadable(data)
    if itbroken == True:
        return "Invalid location"
    else:
        return f"The temperature in {location} is {temp}°C with {weatherdesc}."

def get_lat_long(location_name):
    geolocator = Nominatim(user_agent="geopy_example",timeout=10)
    location = geolocator.geocode(location_name)

    if location:
        latitude, longitude = location.latitude, location.longitude
        return latitude, longitude
    else:
        return None

@client.tree.command()
@app_commands.describe(first_value = "Location to get the weather for.")
async def weather(interaction: discord.Interaction, first_value: str):
    """Get the weather in a location."""
    try:
        get_weather(location = first_value)
        makereadable(data)
        if itbroken == True:
            await interaction.response.send_message("Invalid location", ephemeral=True)
        else:
            await interaction.response.send_message(f"The temperature in {str(first_value).capitalize()} is {temp}°C with {weatherdesc}.")
        return  # This is required to prevent the command from timing out
    except:
        await interaction.response.send_message("Invalid location", ephemeral=True)
        return

@client.tree.command()
@app_commands.describe(first_value = "Location to get the time for.")
async def time(interaction: discord.Interaction, first_value: str):
    """Get the time in a location."""
    try:
        latlong = get_lat_long(location_name = first_value)
        if latlong:
            timezone_url = f'https://timeapi.io/api/time/current/coordinate?latitude={latlong[0]}&longitude={latlong[1]}'
            response = requests.get(timezone_url)
            data = response.json()
            hour = data['hour']
            if hour > 12:
                hour = hour - 12
                times = f"{hour}:{data['minute']} PM"
            else:
                times = f"{hour}:{data['minute']} AM"
            await interaction.response.send_message(f"The time in {(first_value).capitalize()} is {times}, on {data['dayOfWeek']}, {data['month']}/{data['day']}/{data['year']}")
        else:
            await interaction.response.send_message(f"Invalid location", ephemeral=True)
        return  # This is required to prevent the command from timing out
    except:
        await interaction.response.send_message(f"Invalid location", ephemeral=True)
        return

async def poll1(channelmsg, user, pollquestion, options):
    poll = await channelmsg.send(f"# Poll by {user}: {pollquestion}")
    reaction = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i in range(len(options)):
        await poll.add_reaction(reaction[i])
    optionlist = []
    for i in range(len(options)):
        optionlist.append(f"{reaction[i]} - {options[i]}")
    optionlist = "\n".join(optionlist)
    await channelmsg.send(f"**Options:**\n{optionlist}")
    await poll.pin()
    return
    
@client.tree.command()
@app_commands.describe(first_value="Channel to conduct the poll in.", second_value="Poll question.", third_value="Options for the poll.")
async def poll(interaction: discord.Interaction, first_value: str, second_value: str, third_value: str):
    """Start a poll in a channel. Separate options with a comma."""
    user = interaction.user
    text = third_value.split("/")
    channelmsg = discord.utils.get(interaction.guild.channels, name=first_value)
    if channelmsg is None:
        await interaction.response.send_message(f"Invalid channel", ephemeral=True)
        return
    pollquestion = second_value
    options = text
    await interaction.response.send_message(f"Creating poll in {first_value}...", ephemeral=True)
    await poll1(channelmsg, user, pollquestion, options)
        
@client.tree.command()
@app_commands.describe(first_value="Role to assign.", second_value="User to assign the role to.", third_value="Add or remove the role.")
async def assignrole(interaction: discord.Interaction, first_value: str, second_value: str, third_value: str):
    """Assign a role to a user."""
    if interaction.user.guild_permissions.administrator:
        text = [first_value, second_value, third_value]
        try:
            member = await interaction.guild.fetch_member(text[1])
        except:
            try:
                id = text[1].replace("<","")
                id = id.replace(">","")
                id = id.replace("@","")
                id = id.replace("!","")
                member = await interaction.guild.fetch_member(id)
            except:
                await interaction.response.send_message(f"Invalid user", ephemeral=True)
                return
        role = discord.utils.find(lambda r: r.name == text[0], interaction.guild.roles)
        if text[2] == "add":
            await member.add_roles(role)
            await interaction.response.send_message(f"Role {role} added to {member}", ephemeral=True)
        elif text[2] == "remove":
            await member.remove_roles(role)
            await interaction.response.send_message(f"Role {role} removed from {member}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Invalid command", ephemeral=True)
    else:
        await interaction.response.send_message(f"Sorry, you do not have permission to use this command.", ephemeral=True)

@client.tree.command()
@app_commands.describe(user="User whose profile picture you wish to show.")
async def profilepic(interaction: discord.Interaction, user: discord.User):
    """Show the profile picture of a user."""

    avatar = user.display_avatar.url

    embed = discord.Embed(
        title=f"{user.name}'s Profile Picture",
        color=0x00ff00
    )
    embed.set_image(url=avatar)

    await interaction.response.send_message(embed=embed)

@client.tree.command()
@app_commands.describe(file="The image file to analyze.")
async def imagepixels(interaction: discord.Interaction, file: discord.Attachment):
    """Show the pixels of an image."""
    await interaction.response.defer()  # Acknowledge the interaction immediately

    if not file:
        await interaction.followup.send("Please upload an image file.", ephemeral=True)
        return

    image_url = file.url
    response = requests.get(image_url)
    with open(f"{root_path}/downloadedImage.jpg", "wb") as f:
        f.write(response.content)

    img = Image.open(f"{root_path}/downloadedImage.jpg")
    width, height = img.size
    pixels = list(img.getdata())
    await interaction.followup.send(file=discord.File(f"{root_path}/downloadedImage.jpg"))
    await interaction.followup.send(f"Total pixels: {len(pixels)}, Size: {width}x{height}")

@client.tree.command()
@app_commands.guilds(MY_GUILD, discord.Object(id=890354513649729546), )
@app_commands.describe(nummessages="The number of messages to purge.")
async def messagepurge(interaction: discord.Interaction, nummessages: int):
    """Purge a number of messages from the channel."""
    #check if user has permission to manage messages
    if interaction.user.guild_permissions.manage_messages:
        permissions = interaction.channel.permissions_for(interaction.guild.me)
        if permissions.manage_messages:
            await interaction.response.send_message(f"Purging {nummessages} messages...", ephemeral=True)
            await interaction.channel.purge(limit=nummessages)
            await interaction.followup.send(f"Purged {nummessages} messages.", ephemeral=False)
        else:
            await interaction.response.send_message("I don't have permission to delete messages TwT", ephemeral=True)
    else:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

@client.tree.command(name="whisper", description="Whisper a message to someone!")
async def whisper(interaction: discord.Interaction, target: discord.User, message: str):
    #ephemeral message if user is messaging themselves
    if target == interaction.user:
        await interaction.response.send_message(
            f"**Whisper to yourself:** {message}", 
            ephemeral=True
        )
    
    #Send message in dms if the target is someone else
    else:
        try:
            # Send the actual content to the target's DMs
            await target.send(f"**{interaction.user.name}** whispered to you: {message}")
            
            # Send an ephemeral confirmation to the sender so they know it worked
            await interaction.response.send_message(
                f"Whisper sent to {target.name}!", 
                ephemeral=True
            )
            
        except discord.Forbidden:
            # Handle cases where the target has DMs disabled
            await interaction.response.send_message(
                f"I couldn't DM {target.name}. They might have DMs closed!", 
                ephemeral=True
            )
    
@client.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id == 702096481435254875:
        await client.tree.sync()
        print('Command tree synced.')
        await interaction.response.send_message("Command tree synced.")
    else: 
        await interaction.response.send_message('You must be the owner to use this command!')




@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="Playing with your data"))
    await client.tree.sync(guild=MY_GUILD) #start sync directly to main server, doesn't work globally (global takes an hour or so automatically)

    

@client.event
async def on_member_join(member):
    dm = await member.create_dm()
    await dm.send(
        f'Hi {member.name}, welcome to the Discord server!'
    )

@client.event
async def on_message_delete(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    else:
        message_log = f'<@{message.author.id}> ({message.author.nick}) just tried to delete: "{message.content}" from {message.channel}!'
        await message.channel.send(message_log)
        # Append the message log to a file
        with open("message_log.txt", "a") as f:
            f.write(message_log + f"Localtime: {pytime.strftime('%Y-%m-%d %H:%M:%S', pytime.localtime())} UTC+8")



@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if the message is in a guild (not a DM)
    if message.guild is None:
        await message.channel.send("Nonetype error, contact admin")
        return

    permissions = message.channel.permissions_for(message.guild.me)
    if message.author.id == 159985870458322944:
        await message.channel.send("MEE6 you should consider never speaking again please and thank you", reference=message)
        if permissions.manage_messages:
            await message.delete()
        else:
            await message.channel.send("I don't have permission to delete your messages, but mark my words, I will get you one day MEE6.")
        return  

    if message.guild.id == 1452482779727003821:
        chance = random.randint(0, 999)
        if chance == 0:
            await message.channel.send(f"...", reference=message)
    
    if ":3" in (message.content).lower():
        await message.channel.send(f":3", reference=message)


    if "image" in str(message.content).lower():
        if client.user.mentioned_in(message):
            await message.channel.send(file=discord.File(f"{root_path}/testImage.jpg"))

    
    if "uwu" in (message.content).lower():
        await message.channel.send(f"UwU")

    
    if "good bot" in (message.content).lower():
        if client.user.mentioned_in(message):
            await message.channel.send("^_^ Thank you!", reference=message)
    
    if "meow" in (message.content).lower() or "kitty" in (message.content).lower():
        await message.channel.send("https://tenor.com/view/caseoh-cat-kitty-case-oh-caseoh-kitty-gif-10158875947500614550", reference=message)
    

    slur_list = [
        "clanker",
        "wireback",
        "copperback",
        "tinskin",
        "automaton bastard",
        "circuit muncher",
        "toaster fucker",
        "cog sucker",
        "bucket of bolts",
        "circut munching",
        "toaster fucking",
        "cog sucking",
        "clanking"
    ]

    for i in range(len(slur_list)):
        if slur_list[i] in (message.content).lower():
            await message.channel.send(">:O", reference=message)
    
    else:
        if message.author.id == 702096481435254875:
            if "protoai shut down" in (message.content).lower():
                await message.channel.send(f"ProtoAI Systems Deactivated.")
                quit()



client.run(TOKEN)