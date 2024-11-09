# bot.py
import os
import discord
from dotenv import load_dotenv
import requests
import base64
from geopy.geocoders import Nominatim

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(intents=intents)
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
                    await channel.send(f"Hello {member.nick}")
                    loop1break = True
                    break
        
        if "image" in str(message.content).lower():
            await channel.send(file=discord.File("testImage.jpg"))

        if "protoai assign role" in (message.content).lower():
            if message.author.guild_permissions.administrator:
                text = message.content.split(" ")
                try:
                    member = await message.guild.fetch_member(text[3])
                except:
                    try:
                        id = text[3].replace("<","")
                        id = id.replace(">","")
                        id = id.replace("@","")
                        id = id.replace("!","")
                        member = await message.guild.fetch_member(id)
                    except:
                        await channel.send(f"Invalid user")
                        return


                role = discord.utils.get(message.guild.roles,name=text[4])
                if text[5] == "add":
                    await member.add_roles(role)
                    await channel.send(f"Role {role} added to {member}")
                elif text[5] == "remove":
                    await member.remove_roles(role)
                    await channel.send(f"Role {role} removed from {member}")
                else:
                    await channel.send(f"Invalid command")
            else:
                await channel.send(f"Sorry, you do not have permission to use this command.")
                

        
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
                        await channel.send(f"Goodbye {member.nick}~", reference=message)
                        loop2break = True
                        break
        
        if "protoai commands" in (message.content).lower():
            await channel.send("# COMMANDS:")
            await channel.send("1. Hello and Goodbye (AUTO)")
            await channel.send("2. Greeting new members (AUTO)")
            await channel.send("3. Dr House Image ('Image')")
            await channel.send("4. Weather in [location] ('What is the weather in [location]')")
            await channel.send("5. 'Back' and 'Bored' responses (Kinda obvious)")
            await channel.send("6. Smash (Don't use this please)")
            await channel.send("7. Time in [location] ('What is the time in [location]')")
            await channel.send("8. ProtoAI Assign Role (Admin only: 'Protoai Assign Role [role] [user] [add/remove]')")
            await channel.send("9. ProtoAI Shutdown Protocol (Owner only)")

#Absolute fucking tortue DO NOT ATTEMPT TO FIX

        if "what is the time in" in (message.content).lower():
            requestedtimeloc = message.content.split("in ")
            requestedtimeloc = requestedtimeloc[1]
            latlong = get_lat_long(requestedtimeloc)
            if latlong:
                timezone_url = f'https://timeapi.io/api/time/current/coordinate?latitude={latlong[0]}&longitude={latlong[1]}'
                response = requests.get(timezone_url)
                data = response.json()
                hour = data['hour']
                if hour > 12:
                    hour = hour - 12
                    time = f"{hour}:{data['minute']} PM"
                else:
                    time = f"{hour}:{data['minute']} AM"
                await channel.send(f"The time in {(requestedtimeloc).capitalize()} is {time}, on {data['dayOfWeek']}, {data['month']}/{data['day']}/{data['year']}")
            else:
                await channel.send(f"Invalid location")


        if "what is the weather in" in (message.content).lower():
            splitmessage = message.content.split(" in ")
            await channel.send(getweather(splitmessage[1]))
        
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
        
client.run(TOKEN)