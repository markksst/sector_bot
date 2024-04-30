import discord
import json
import urllib.parse
import difflib
import asyncio

# Dictionary mapping Pokémon names to their corresponding links
with open('guides.json', 'r', encoding='utf-8') as f:
    pokemon_links = json.loads(f.read())


# Define global variables to store member counts for both squads
sector_count = 0
sector_b_count = 0

# Response for the !squad command
squad_info = """
Hi there! Here is information about our squads. We currently have two.

:small_orange_diamond: Squad name: **Sector**
    :small_orange_diamond: Squad ID: **#Y7Q2NH5Q**
    :small_orange_diamond: Leader: **Cyber**
    :small_orange_diamond: Members: **{}/30** ({:.0f}%)

    :small_orange_diamond: Squad Name: **Sector・B**
    :small_orange_diamond: Squad ID: **#NK1EE0P6**
    :small_orange_diamond: Leader: **Hikari**
    :small_orange_diamond: Members: **{}/30** ({:.0f}%)

Please send a request & message the squad leader to join.
"""

# Response for the !status command
status = """
**:red_square: Not started yet  |  :orange_square: In development |  :white_check_mark: Finished**

:orange_square: `!quiz`: Questions related to Pokémon UNITE, encouraging users to chat regularly and engage with the bot. Each week a person with most "quizpoints" gets the "Quizmaster" role.
:red_square: Event Notifications: Notifications for community events, updates and giveaways.
:red_square: Tournament Management:  Tools for organizing and managing Pokémon UNITE tournaments.
:red_square: Replacing other bots functions so we can use this bot instead: StickyBot functionality, Giveaways, etc.
:red_square: Slash commands: You know what they are.
:red_square: Generating Voice Channels: Make your own VC.
:red_square: Custom image for head/tail coin: Instead of showing text it shows an image.
:white_check_mark: Number of squad members: Include the number of members of each squad in the !squad command.
:white_check_mark: `!coinflip`: You know what it does.
:white_check_mark: Name matching: The bot will bring up correct pokemon even if you misspell it's name.
:white_check_mark: `!meta <pokemon_name>`: Brings up this link: https://uniteapi.dev/meta for the specified pokemon.
:white_check_mark: `!random`: The bot will generate a random pokemon for you to play.
:white_check_mark: `!guide <pokemon_name>`: Brings up this link: https://unite-guide.com/pokemon for the specified pokemon.
:white_check_mark: Fun commands: `!cat`, `!dog`, `!hamster`; generates a random GIF.
:white_check_mark: `!squad`: Brings up info about our squads.
"""

# Response for the !hephe command
hephe = """
Don't forget to claim your squad points!
"""

# Define your intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize Discord client with intents
client = discord.Client(intents=intents)

_COMMANDS = {}
_CMD_INFO = {}

# Function to find the closest match for a given input string
def find_closest_match(input_str):
    closest_match = difflib.get_close_matches(input_str, pokemon_links.keys(), n=1, cutoff=0.6)
    if closest_match:
        return closest_match[0]
    else:
        return None

def bot_command(cmd_name, description = ""):
    def cmd_wrapper(f):
        _cmd = cmd_name.lower()
        _COMMANDS[_cmd] = f
        # TODO: get params for generating usage
        usage = ""
        if f.__code__.co_argcount > 1:
            usage = ' '.join(f"<{_}>" for _ in f.__code__.co_varnames[1:f.__code__.co_argcount] if _)
            usage = f"`!{_cmd} {usage}`"
        else:
            usage = f"`!{_cmd}`"
        _CMD_INFO[_cmd] = (description, usage)
        return f

    return cmd_wrapper


@bot_command("help", "General info about the bot and commands.")
async def cmd_help(message, *args):
    embed = discord.Embed(title="Helpful Information", color=0xBA8EBF)
    embed.description = "Hi there! See the list of bot commands you can use:"

    for cmd, info in _CMD_INFO.items():
        desc = f'**Usage**: {info[1]}'
        if info[0]:
            desc += '\n' + info[0]
        embed.add_field(name=f'!{cmd}', value=desc, inline=False)

    embed.set_footer(text = "More commands coming soon!")
    await message.channel.send(embed=embed)
    return True


@bot_command("guide", "I will bring up a guide for a Pokémon you want.")
async def cmd_guide(message, pokemon_name=None):
    if pokemon_name:
        pokemon_name = pokemon_name.lower()
        # Find the closest match to the input Pokémon name
        closest_match = find_closest_match(pokemon_name)
        if closest_match:
            # Send the corresponding link along with a message
            _ = pokemon_links[closest_match]
            await message.channel.send(f"Here is a guide for {_['name']}. I hope you find it helpful!\n{_['url']}")
        else:
            # If no match is found, send a message indicating so
            await message.channel.send("Sorry, I couldn't find a guide for that Pokémon.")
        return True
    return False

# Load the meta URLs from meta.json
with open('meta.json', 'r', encoding='utf-8') as f:
    meta_links = json.load(f)

# Function to handle the !meta command
@bot_command("meta", "I will bring up meta information for a Pokémon you want.")
async def cmd_meta(message, pokemon_name=None):
    if pokemon_name:
        pokemon_name = pokemon_name.lower()
        # Find the closest match to the input Pokémon name
        closest_match = find_closest_match(pokemon_name)
        if closest_match:
            # Check if the closest match has meta information
            if closest_match in meta_links:
                meta_url = meta_links[closest_match]['metaurl']
                # Send the message with the meta URL
                await message.channel.send(f"Here is Pokémon Unite Meta for {pokemon_links[closest_match]['name']}. I hope you find it helpful!\n{meta_url}")
            else:
                # If no meta information is available, send a message indicating so
                await message.channel.send("Sorry, there is no meta information available for that Pokémon.")
        else:
            # If no match is found, send a message indicating so
            await message.channel.send("Sorry, I couldn't find meta information for that Pokémon.")
        return True
    return False


# Response for the !squad command
@bot_command("squad", "Information & squad IDs for our squads.")
async def cmd_squad(message, *args):
    # Calculate percentage of members for both squads
    sector_percentage = (sector_count / 30) * 100
    sector_b_percentage = (sector_b_count / 30) * 100

    # Format the squad info string with the member counts
    squad_info_updated = squad_info.format(sector_count, sector_percentage, sector_b_count, sector_b_percentage)

    # Style the embed
    embed = discord.Embed(title="Squad Information", color=0xBA8EBF)
    embed.set_author(name="Chansey", icon_url="https://media.tenor.com/GiMY-MkX-38AAAAM/chansey-egg.gif")
    embed.set_thumbnail(url="https://pa1.aminoapps.com/6220/0ae1ed8cbe84a6f783eee7a40c10b097304fb9e0_128.gif")
    embed.description = squad_info_updated
    embed.set_footer(text="Feel free to join our squads!")

    # Send the styled embed
    await message.channel.send(embed=embed)
    return True

# Response for the !squadmembers command
@bot_command("squadmembers", "Updates the number of squad members. (Available to Leader, Head-Coordinator, Coordinator)")
async def cmd_squadmembers(message, *args):
    global sector_count, sector_b_count

    # Check if the user has the required roles
    allowed_roles = ["Leader", "Head-Coordinator", "Coordinator"]
    user_roles = [role.name for role in message.author.roles]
    if not any(role in allowed_roles for role in user_roles):
        await message.channel.send("You don't have permission to use this command. It is available for Leader, Head-Coordinator and Coordinator roles.")
        return False

    # Check if both member counts are provided
    if len(args) != 1:
        await message.channel.send("Please provide member counts for both squads.")
        return False

    # Extract member counts from args
    member_counts = args[0].split()

    # Check if exactly two member counts are provided
    if len(member_counts) != 2:
        await message.channel.send("Please provide member counts for both squads.")
        return False

    # Extract member counts for each squad
    member_count_sector, member_count_sector_b = member_counts

    # Convert member counts to integers and update global variables
    try:
        sector_count = int(member_count_sector)
        sector_b_count = int(member_count_sector_b)
    except ValueError:
        await message.channel.send("Member counts must be numbers.")
        return False

    await message.channel.send("Member counts updated successfully!")
    return True



@bot_command("status", "See the bot development status.")
async def cmd_status(message, *args):
    embed = discord.Embed(title="Status Information", description=status, color=0xBA8EBF)
    await message.channel.send(embed=embed)
    return True

@bot_command("hephe", "Hephe once said...")
async def cmd_hephe(message, *args):
    embed = discord.Embed(title="Hephe once said...", description=hephe, color=0xBA8EBF)
    imageurl = 'https://media.discordapp.net/attachments/1007740505616035921/1207084987849904158/IMG_1628.png?ex=662e1f3f&is=662ccdbf&hm=4dfa76977f203b52954e29c7bd3f1dd4c87a1c86c1de523ac013792a3a001d1b&=&format=webp&quality=lossless&width=2110&height=956'
    embed.set_image(url=imageurl)
    await message.channel.send(embed=embed)
    return True


@bot_command("api", "I will bring up information for any Player you want.")
async def cmd_api(message, player_name=None):
    if player_name and len(player_name) <= 16:
        p = urllib.parse.quote(player_name)
        await message.channel.send(f"https://uniteapi.dev/p/{p}")
        return True
    return False

import requests
import random

# Function to handle the !cat command
@bot_command("cat", "Sends a random cat GIF.")
async def cat_command(message):
    gif_url = get_cat_gif()
    await message.channel.send(gif_url) if gif_url else await message.channel.send("Sorry, I couldn't find a cat gif.")
    return True

# Function to fetch a random cat gif
def get_cat_gif():
    response = requests.get("https://discord.com/api/v9/gifs/search?q=cat&media_format=mp4&provider=tenor")
    if response.status_code == 200:
        data = response.json()
        gifs = data if isinstance(data, list) else []
        if gifs:
            return random.choice(gifs)["url"]
    return None

# Function to handle the !cat command
@bot_command("dog", "Sends a random dog GIF.")
async def dog_command(message):
    gif_url = get_dog_gif()
    await message.channel.send(gif_url) if gif_url else await message.channel.send("Sorry, I couldn't find a dog gif.")
    return True

# Function to fetch a random cat gif
def get_dog_gif():
    response = requests.get("https://discord.com/api/v9/gifs/search?q=dog&media_format=mp4&provider=tenor")
    if response.status_code == 200:
        data = response.json()
        gifs = data if isinstance(data, list) else []
        if gifs:
            return random.choice(gifs)["url"]
    return None

# Function to handle the !cat command
@bot_command("hamster", "Sends a random hamster GIF.")
async def hamster_command(message):
    gif_url = get_hamster_gif()
    await message.channel.send(gif_url) if gif_url else await message.channel.send("Sorry, I couldn't find a hamster gif.")
    return True

# Function to fetch a random cat gif
def get_hamster_gif():
    response = requests.get("https://discord.com/api/v9/gifs/search?q=hamster&media_format=mp4&provider=tenor")
    if response.status_code == 200:
        data = response.json()
        gifs = data if isinstance(data, list) else []
        if gifs:
            return random.choice(gifs)["url"]
    return None

# Function to simulate flipping a coin
def flip_coin():
    return random.choice(["Heads", "Tails"])

# Define the command handler with the bot_command decorator
@bot_command("coinflip", "Flip a coin.")
async def cmd_flip(message):
    # Flip the coin
    result = flip_coin()
    # Send the result to the channel
    embed = discord.Embed(title="🪙 Coin Flip Result 🪙", color=0xBA8EBF)
    embed.add_field(name="", value=result, inline=False)
    await message.channel.send(embed=embed)
    return True

@bot_command("random", "Picks a random Pokémon for you to play.")
async def cmd_random(message):
    # Pick a random Pokémon from the guides.json file
    random_pokemon = random.choice(list(pokemon_links.keys()))
    pokemon_name = pokemon_links[random_pokemon]['name']
    pokemon_url = pokemon_links[random_pokemon]['url']
    response = f"You should play **{pokemon_name}**!"
    await message.channel.send(response)
    return True
#NEXT FUNCTION

# Define the list of questions and answers
questions = [
    {"question": "What is the skill described here? {skill description}", "answer": "HELP"},
    {"question": "What is the skill shown here? {skill image}", "answer": "HELP"},
    {"question": "What level does {pokemon name} evolve at?", "answer": "HELP"}
]

# Define the active_quiz variable globally
active_quiz = None

# Define the command handler for !quiz
@bot_command("quiz", "Starts a quiz with a random question.")
async def cmd_quiz(message):
    global active_quiz
    if active_quiz:
        await message.channel.send("A quiz is already active. Please wait for it to finish.")
        return False

    # Select a random question
    question = random.choice(questions)
    await message.channel.send(question['question'])

    active_quiz = {"question": question, "author": message.author}

# Define the message event handler
@client.event
async def on_message(message):
    global active_quiz

    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Check if there's an active quiz
    if active_quiz:
        # Check if the message author is the same as the quiz author
        if message.author == active_quiz['author']:
            # Check if the message content matches the answer
            if message.content.lower() == active_quiz['question']['answer'].lower():
                await message.channel.send(f":tada: Congratulations {message.author.mention}! You got it right!")
            else:
                await message.channel.send("Oops! That's not correct. :pensive: Try again.")

            # Reset the active quiz
            active_quiz = None
            return


# Process quiz answers
    await client.process_commands(message)

#NEXT FUNCTION
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    # Get the #bot-testing channel
    bot_testing_channel = discord.utils.get(client.get_all_channels(), name='bot-testing')
    if bot_testing_channel:
        await bot_testing_channel.send(":arrows_counterclockwise: Updates complete... I am back online!")
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name=" !help"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('!'):
        return

    cmd, *cont = message.content.split(' ', 1)
    cmd = cmd[1:].lower()
    if cmd in _COMMANDS:
        succ = await _COMMANDS[cmd](message, *cont)
        if not succ:
            info = _CMD_INFO[cmd]
            await message.channel.send(f"Usage: {info[1]}")



# Run the bot with its token
client.run('TOKEN')
