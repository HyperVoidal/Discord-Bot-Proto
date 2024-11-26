# bot.py
import os
import discord
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

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MY_GUILD = discord.Object(id = 1292139882143027311)

class MyClient(discord.Client):
    def __init__(self, *, intents:discord.Intents):
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyClient(intents=intents)
CHANNELid = 1304345339440136263
global channel
channel = client.get_channel(CHANNELid)
CHANNELid2 = 1292139882629828660
channel2 = client.get_channel(CHANNELid2)

#interpret weather API

f = open("SECRETAPIKEY.txt", "r")
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
@app_commands.describe(first_value="User whose profile picture you wish to show.")
async def profilepic(interaction: discord.Interaction, first_value: str):
    """Show the profile picture of a user."""
    try:
        member = client.get_user(int(first_value))
    except ValueError:
        try:
            id = first_value.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
            member = client.get_user(int(id))
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Invalid user", ephemeral=True)
            return
    
    if member is None:
        await interaction.response.send_message(f"User not found", ephemeral=True)
        return
    
    avatar_url = member.avatar.url
    embed = discord.Embed(title=f"{member.name}'s Profile Picture", color=0x00ff00)
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

@client.tree.command()
@app_commands.describe(file="The image file to analyze.")
async def imagepixels(interaction: discord.Interaction, file: discord.Attachment):
    channel = interaction.channel
    """Show the pixels of an image."""
    if not file:
        await interaction.response.send_message("Please upload an image file.", ephemeral=True)
        return

    image_url = file.url
    response = requests.get(image_url)
    with open("downloadedImage.jpg", "wb") as f:
        f.write(response.content)
    
    img = Image.open("downloadedImage.jpg")
    width, height = img.size
    pixels = list(img.getdata())
    imagereturn = await interaction.response.send_message(file=discord.File("downloadedImage.jpg"))
    await channel.send(f"Total pixels: {len(pixels)}, Size: {width}x{height}")


@client.event
async def on_ready():

    CHANNELid = 1304345339440136263
    global channel
    channel = client.get_channel(CHANNELid)
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="with your data"))
    await channel.send(f"ProtoAI Systems Initialised.") #  Sends message to channel

    

@client.event
async def on_member_join(member):
    CHANNELid = 1304345339440136263
    global channel
    channel = client.get_channel(CHANNELid)
    dm = await member.create_dm()
    await dm.send(
        f'Hi {member.name}, welcome to the Discord server!'
    )



@client.event
async def on_message(message):
    CHANNELid = 1304345339440136263
    CHANNELid2 = 1292139882629828660
    global channel
    channel = client.get_channel(CHANNELid)
    channel2 = client.get_channel(CHANNELid2)
    
    greetings = ["hi", "hello", "hey", "sup", "yo", "greetings"]
    goodbyes = ["bye", "goodbye", "see ya", "later", "cya", "goodnight", "gn", "good night", "going to bed"]

    if message.channel.id != CHANNELid:
        if message.channel.id == CHANNELid2:
            if "bored" in message.content.lower():
                if message.author.id == 1031295377946726581:
                    await channel2.send(f"{message.author.mention} is bored. Big surprise. Have you tried not doing that maybe?")
                    return
                else:
                    return
            else:
                return
        else:
            return
    
    if message.author == client.user:
        return

    else:
        loop1break = False
        loop2break = False
        messages = message.content.split(" ")

        for x in range(len(messages)):
            if loop1break == True:
                break
            for i in range(len(greetings)):
                if greetings[i] == str(messages[x]).lower():
                    member = await message.guild.fetch_member(message.author.id)
                    if member.nick == None:
                        await channel.send(f"Hello {member.name}")
                    else:
                        await channel.send(f"Hello {member.nick}")
                    loop1break = True
                    break
        
        if "image" in str(message.content).lower():
            await channel.send(file=discord.File("testImage.jpg"))
                

        
        for x in range(len(messages)):
            if loop1break == True:
                break
            for i in range(len(greetings)):
                role = discord.utils.find(lambda r: r.name == 'Minor', message.guild.roles)
                if role not in message.author.roles:
                    if (greetings[i] + "~") == str(messages[x]).lower():
                        await channel.send(f"Well hello there cutie~", reference=message)
                        loop1break = True
                        break

        for x in range(len(messages)):
            if loop2break == True:
                break
            for i in range(len(goodbyes)):
                if goodbyes[i] == str(messages[x]).lower():
                    member = await message.guild.fetch_member(message.author.id)
                    if member.nick == None:
                        await channel.send(f"Goodbye {member.name}")
                    else:
                        await channel.send(f"Goodbye {member.nick}")
                    loop2break = True
                    break
        
        for x in range(len(messages)):
            if loop2break == True:
                break
            for i in range(len(goodbyes)):
                role = discord.utils.find(lambda r: r.name == 'Minor', message.guild.roles)
                if role not in message.author.roles:
                    if (goodbyes[i] + "~") == str(messages[x]).lower():
                        member = await message.guild.fetch_member(message.author.id)
                        if member.nick == None:
                            await channel.send(f"Goodbye {member.name}~", reference=message)
                        else:
                            await channel.send(f"Goodbye {member.nick}~", reference=message)
                        loop2break = True
                        break
        
        if "protoai commands" in (message.content).lower():
            await channel.send("# COMMANDS:")
            await channel.send("1. Hello and Goodbye (AUTO)\n" +
                               "2. Greeting new members (AUTO)\n" +
                               "3. Dr House Image ('Image')\n" +
                               "4. Weather in [location] ('What is the weather in [location] ('/' Command)')\n" +
                               "5. 'Back' and 'Bored' responses (Kinda obvious)\n" +
                               "6. Smash (Don't use this please)\n" +
                               "7. Time in [location] ('What is the time in [location]'), ('/' Command)\n" +
                               "8. ProtoAI Assign Role (Admin only: 'Protoai Assign Role: [role], [user], [add/remove]'), ('/' Command)\n" +
                               "9. ProtoAI Conduct Poll ('Protoai Conduct Poll: [channel], [poll question], [option 1/option 2/option 3/etc] (up to 10 options)'), ('/' Command)\n" +
                               "10. ProtoAI Return Name ('Protoai Return Name: [user id]'), ('/' Command)\n" +
                               "11. Profile Picture Return (WIP)\n" +
                               "12. ProtoAI Shutdown Protocol (Owner only)")
        
        if "im back" in (message.content).lower() or "i'm back" in (message.content).lower():
            await channel.send(f"Hi back, I'm ProtoAI")
        
        
        if "im bored" in (message.content).lower() or "i'm bored" in (message.content).lower():
            await channel.send(f"Hi bored, I'm ProtoAI")
        
        if message.author.id == 702096481435254875:
            if "protoai shut down" in (message.content).lower():
                await channel.send(f"ProtoAI Systems Deactivated.")
                quit()

        #Literally never use this stuff please
        if "smash" in (message.content).lower():
            role = discord.utils.find(lambda r: r.name == 'Minor', message.guild.roles)
            if role not in message.author.roles:
                theirdm = await message.author.create_dm()
                smashcounter = 0
                text = message.content.split(" ")
                for i in range(len(text)):
                    if text[i].lower() == "smash" or text[i].lower() == "smash~":
                        smashcounter += 1
                if smashcounter > 5:
                    for i in range(smashcounter):
                        await theirdm.send(f"*Smashes {message.author} roughly* 'You've been naughty~'")
                else:
                    for i in range(smashcounter):
                        await theirdm.send(f"*Smashes {message.author} cutely~*")
            else:
                await channel.send(f"Sorry {message.author.mention}, you're too young for that.")
            
        if ":3" in (message.content).lower():
            await channel.send(f":3")
        
        if "uwu" in (message.content).lower():
            await channel.send(f"UwU")
        
        if (message.content).lower() == "super":
            await channel.send(f"MACHO")
            await channel.send(f"-# *messgae from owner: fuck you for making me add this bar*")
        
        if "protoai return name" in (message.content).lower():
            text = message.content.split(" ")
            text = text[3]
            await message.channel.send(f"<@{text}> is the requested user. ")
        
        if "good bot" in (message.content).lower():
            if client.user.mentioned_in(message):
                await message.channel.send("^_^ Thank you!", reference=message)

client.run(TOKEN)