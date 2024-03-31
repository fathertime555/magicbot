import os
import serverconnection
from discord import Intents as ints
from discord.ext import commands
from dotenv import load_dotenv
from mysql.connector import Error
from datetime import datetime
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = ints.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '/', intents = intents)
connection = serverconnection.create_server_connection(os.getenv('MYSQL_HOSTNAME'), os.getenv('MYSQL_USERNAME'), os.getenv('MYSQL_PASSWORD'))

def extract_name(args):
    print(args)
    extracted = ""
    if (len(args) == 1 and (len(args[0]) == 0 or len(args[0]) == 1)) or len(args) == 0:
        return (2, args)
    for x in range(len(args)):
        if x == 0:
            if args[0][0] != "(":
                return (1, args)
            extracted = args.pop(0)[1:]
            if extracted[-1] == ")":
                extracted = extracted[:-1]
                break
        elif args[0][0] == "(":
            print(args)
            return (2, args)
        elif args[0][-1] == ")":
            extracted = extracted + " " + args.pop(0)[:-1]
            break
        elif len(args) == 1 and args[0][-1] != ")":
            print(args)
            return (2, args)
        else:
            extracted = extracted + " " + args.pop(0)
    return (extracted, args)

def standardize_color(color):
    color = "".join(sorted(color.upper()))
    if color == "c":
        return "Colorless"    
    if color == "W":
        return "White"
    if color == "U":
        return "Blue"
    if color == "B":
        return "Black"
    if color == "R":
        return "Red"
    if color == "G":
        return "Green"
    if color == "UW":
        return "Azorius"
    if color == "BU":
        return "Dimir"
    if color == "BR":
        return "Rakdos"
    if color == "GR":
        return "Gruul"
    if color == "GW":
        return "Selesnya"
    if color == "BW":
        return "Orzhov"
    if color == "RU":
        return "Izzet"
    if color == "BG":
        return "Golgari"
    if color == "RW":
        return "Boros"
    if color == "GU":
        return "Simic"
    if color == "GUW":
        return "Bant"
    if color == "BUW":
        return "Esper"
    if color == "BRU":
        return "Grixis"
    if color == "BGR":
        return "Jund"
    if color == "GRW":
        return "Naya"
    if color == "BGW":
        return "Abzan"
    if color == "RUW":
        return "Jeskai"
    if color == "BGU":
        return "Sultai"
    if color == "BRW":
        return "Mardu"
    if color == "GRU":
        return "Temur"
    if color == "BRUW":
        return "Yore-Tiller"
    if color == "BGRU":
        return "Glint-Eye"
    if color == "BGRW":
        return "Dune-Brood" 
    if color == "GRUW":
        return "Ink-Treader"
    if color == "BGUW":
        return "Witch-Maw"  
    if color == "BGRUW":
        return "WUBRG"
    return 0

def standardize_strategies(strategies):
    #Add in standard for multiple word strategies, capitalize after hyphens, do not capitalize the words that shouldn't be capitalized
    standardized = []
    tempstrategy = ""
    multiplewords = False
    for strategy in strategies:
        strategy.lower()
        if strategy == 0 or (strategy == len(strategies)) - 1 or strategy != ("and" and "a" and "as" and "at" and "but" and "by" and "down" and "for" and "from" and "if" and "in" and "into" and "like" and "near" and "nor" and "of" and "off" and "on" and "once" and "onto" and "or" and "over" and "past" and "so" and "than" and "that" and "to" and "upon" and "when" and "with" and "yet"):
            strategy = strategy.capitalize()
        if strategy[-1] == ',':
            strategy = strategy[:-1]
        for letter in range(len(strategy)):
            if strategy[letter] == "-" and letter < len(strategy):
                strategy[letter + 1] == strategy[letter + 1].upper()
        for letter in range(len(strategy)):
            if strategy[-letter] == "\"" or strategy[-letter] == "\'":
                strategy = strategy[:-letter] + "\\" + strategy[-letter:]
        if strategy[0] == "{":
            multiplewords = True
            strategy = strategy[1:]
            strategy = strategy.capitalize()
            tempstrategy = strategy
        elif multiplewords == False:
            standardized.append(strategy)
        elif multiplewords == True:
            tempstrategy = tempstrategy + " " + strategy
            if strategy[-1] == "}":
                multiplewords = False
                standardized.append(tempstrategy[:-1])
    if multiplewords == True:
        return 0
    return standardized

def execute_query(query):
    cursor = connection.cursor()
    cursor.execute("USE " + os.getenv('DATABASE_NAME'))
    try:
        print(query)
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(query):
    cursor = connection.cursor()
    cursor.execute("USE " + os.getenv('DATABASE_NAME'))
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

@bot.command(name='newchallenger')
async def new_player(ctx, *args):
    if len(args) != 0:
        nickname = args[0]
        for x in args[1:]:
            nickname += " " + x
        playerid = ctx.author.id
        existingname = read_query("SELECT nickname FROM players WHERE player_id = " + str(ctx.author.id))
        if existingname:
            await ctx.send("Player has already joined the field of battle with the nickname " + existingname[0][0])
        else:
            now = datetime.now()
            query = "INSERT INTO players VALUES (\'" + str(playerid) + "\', \'" + nickname + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0)"
            execute_query(query)
            await ctx.send(nickname + " has joined the field of battle!")
    else:
        await ctx.send("Please enter your name so that you might be attributed the glory of your victories.") 

@bot.command(name='removeself')
async def delete_player(ctx):
    playerid = str(ctx.author.id)
    existingplayer = read_query("SELECT nickname FROM players WHERE player_id = " + str(ctx.author.id))[0][0]
    if not existingplayer:
        await ctx.send("You have not been registered as a contender on the field of battle. Use /newchallenger to enlist now.")
    else: 
        query = "DELETE FROM players WHERE player_id = \'" + playerid + "\'"
        execute_query(query)
        await ctx.send(existingplayer + " has fled the field of battle.")

@bot.command(name='changenickname')
async def change_name(ctx, *args):
    if len(args) != 0:
        newname = args[0]
        for x in args[1:]:
            newname += " " + x
        playerid = str(ctx.author.id)
        currentname = read_query("SELECT nickname FROM players WHERE player_id = " + str(ctx.author.id))[0][0]
        if not currentname:
            await ctx.send("You have not been registered as a contender on the field of battle. Use /newchallenger to enlist now.")
        else: 
            query = "UPDATE players SET nickname = \'" + newname + "\' WHERE player_id = \'" + playerid + "\'"
            execute_query(query)
            await ctx.send(currentname + " has changed there title in the field of battle to " + newname + ".")
    else:
       await ctx.send("Please enter your new name so that you might be attributed the glory of your victories.")   

@bot.command(name='newdeck')
async def new_deck(ctx, *args):
    args = list(args)
    commander = ""
    deckname = ""
    color = ""
    strategies = []
    strategy = ""
    partners = 0
    apiurl = "https://api.scryfall.com/cards/named?exact="
    now = datetime.now()
    playerid = str(ctx.author.id)

    if not read_query("SELECT player_id FROM players WHERE player_id = \'" + playerid + "\'"):
        await ctx.send("Please register yourself as a contender in the field of battle.")
        return
    
    if len(args) == 0:
        await ctx.send("Please enter at least the commander of your deck and its name.")
        return
    
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the name of your commander in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the name of your commander.")
        return
    else:
        commander = extracted[0]
        args = extracted[1]
    if commander[0] == '{':
        partners = 1
        commandertwo = ""
        commanderlist = list(commander)
        commanderlist.pop(0)
        commander = ""
        limit = len(commanderlist)
        for letter in range(limit):
            if letter == limit:
                await ctx.send("Please close the curly braces around the name of your first partner commander.")
                return
            part = commanderlist.pop(0)
            if part != '}':
                commander = commander + part
            else:
                break 
        if not commanderlist:
            await ctx.send("Please put in your second partner commander or remove your commander from the curly braces.")
            return
        letter = commanderlist.pop(0)
        if letter != "{":
            await ctx.send("Please put your second partner commander in curly braces or remove your commander from the curly braces.")
            return
        limit = len(commanderlist)
        for letter in range(limit):
            part = commanderlist.pop(0)
            if letter == limit and part != '}':
                await ctx.send("Please close the curly braces around the name of your second partner commander.")
                return
            if part != '}':
                commandertwo = commandertwo + part
            else:
                break
        apiurlone = apiurl + commander
        apiurltwo = apiurl + commandertwo
        responseone = requests.get(apiurlone)
        responseone = responseone.json()
        responsetwo = requests.get(apiurltwo)
        responsetwo = responsetwo.json()
        if responseone["object"] == "error":
            if responseone["code"] == "not_found":
                await ctx.send("Please enter in the name of a valid magic card for your first partner commander.")
                return
            else:
                await ctx.send("i'm sorry, the Scryfall server I am using to verify cards is returning an error they describe as: " + responseone["details"] + ". Please wait for the server to be back up or contact my creator for a fix to the issue.")
                return
        if responseone["legalities"]["commander"] != "legal":
            await ctx.send("Please choose a legal first partner commander for your deck.")
            return 
        
        if responsetwo["object"] == "error":
            if responsetwo["code"] == "not_found":
                await ctx.send("Please enter in the name of a valid magic card for your first partner commander.")
                return
            else:
                await ctx.send("i'm sorry, the Scryfall server I am using to verify cards is returning an error they describe as: " + responsetwo["details"] + ". Please wait for the server to be back up or contact my creator for a fix to the issue.")
                return
        if responsetwo["legalities"]["commander"] != "legal":
            await ctx.send("Please choose a legal first partner commander for your deck.")
            return
        
        commander = responseone["name"]
        for i in range(len(commander)):
            if commander[-i] == "\"" or commander[-i] == "\'":
                commander = commander[:-i] + "\\" + commander[-i:]
        commandertwo = responsetwo["name"]
        for i in range(len(commandertwo)):
            if commandertwo[-i] == "\"" or commandertwo[-i] == "\'":
                commandertwo = commandertwo[:-i] + "\\" + commandertwo[-i:]

        if ("Legendary" and "Creature") not in responseone["type_line"] and "Background" not in responseone["type_line"] and ("Legendary Planeswalker" not in responseone["type_line"] or "can be your commander" not in responseone["oracle_text"]):
            await ctx.send("Please choose a legal commander for your first partner.")
            return
        
        if ("Legendary" and  "Creature") not in responsetwo["type_line"] and "Background" not in responsetwo["type_line"] and ("Legendary Planeswalker" not in responsetwo["type_line"] or "can be your commander" not in responsetwo["oracle_text"]):
            await ctx.send("Please choose a legal commander for your second partner.")
            return
        
        if (("Legendary" and "Creature") in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"]) and "Choose a Background" not in responseone["oracle_text"]) or ("Legendary Planeswalker" in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"])):
            await ctx.send("Please choose a legal partner for your first partner.")
            return

        if (("Legendary" and "Creature") in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"]) and "Choose a Background" not in responsetwo["oracle_text"]) or ("Legendary Planeswalker" in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"])):
            await ctx.send("Please choose a legal partner for your second partner.")
            return

        if "Partner with" in responseone["keywords"] and "Partner with" in responsetwo["keywords"]:
            if commander not in responsetwo["oracle_text"] or commandertwo not in responseone["oracle_text"]:
                await ctx.send("Unfortunately the partners you chose do not partner with each other.")
                return
        if ("Partner with" in responseone["keywords"] and "Partner with" not in responsetwo["keywords"]) or ("Partner with" not in responseone["keywords"] and "Partner with" in responsetwo["keywords"]): 
            await ctx.send("Unfortunately the partners you chose do not partner with each other.")
            return
        
        if ("Background" in responseone["type_line"] and "Choose a Background" not in responsetwo["oracle_text"]) or ("Background" in responsetwo["type_line"] and "Choose a Background" not in responseone["oracle_text"]) or ("Choose a Background" in responseone["oracle_text"] and "Background" not in responsetwo["type_line"]) or ("Choose a Background" in responsetwo["oracle_text"] and "Background" not in responseone["type_line"]):
            await ctx.send("A creature with the \"Choose a Background\" text must be paired with a Legendary Background Enchantment and vice versa.")
            return
        
        for i in responseone["color_identity"]:
            color = color + i
        for i in responsetwo["color_identity"]:
            if i not in color:
                color = color + i
        color = standardize_color(color)

    else:
        apiurl = apiurl + commander
        response = requests.get(apiurl)
        response = response.json()
        if response["object"] == "error":
            if response["code"] == "not_found":
                await ctx.send("Please enter in the name of a valid magic card for your commander.")
                return
            else:
                await ctx.send("i'm sorry, the Scryfall server I am using to verify cards is returning an error they describe as: " + response["details"] + ". Please wait for the server to be back up or contact my creator for a fix to the issue.")
                return
        if response["legalities"]["commander"] != "legal":
            await ctx.send("Please choose a legal commander for your deck.")
            return     
        if ("Legendary" and "Creature") not in response["type_line"] and ("Legendary Planeswalker" not in response["type_line"] or "can be your commander" not in response["oracle_text"]):
            await ctx.send("Please choose a legal commander for your deck.")
            return
        commander = response["name"] 
        for i in range(len(commander)):
            if commander[-i] == "\"" or commander[-i] == "\'":
                commander = commander[:-i] + "\\" + commander[-i:]
        for i in response["color_identity"]:
            color = color + i
        color = standardize_color(color)

    if len(args) == 0:
        await ctx.send("Please enter at least the name of your deck.")
        return
    
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the name of your deck in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the name of your deck.")
        return
    else:
        deckname = extracted[0]
        for i in range(len(deckname)):
            if deckname[-i] == "\"" or deckname[-i] == "\'":
                deckname = deckname[:-i] + "\\" + deckname[-i:]
        args = extracted[1]
    player = read_query("SELECT player FROM decks WHERE deck_name = \'" + deckname + "\'")
    if player:
        await ctx.send(deckname + " already exists (Created by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + player[0][0] + "\'")[0][0] + "). Please enter a unique name for your deck or kill your competition to take the rights for yourself!") 
        return
    if len(args) == 0:
        inputs = 2
    else:
        extracted = extract_name(args)
        if extracted[0] == 1:
            await ctx.send("Please put the strategy(s) of your deck in parentheses.")
            return
        elif extracted[0] == 2:
            await ctx.send("Please close the parentheses around the strategy(s) of your deck.")
            return
        else:
            strategies = extracted[0].split()
        strategies = standardize_strategies(strategies)
        if strategies == 0:
            await ctx.send("Please close the curly braces inside of the strategy(s) of your deck.")
            return
        strategy = strategy + strategies[0]
        for strategynum in range(1,len(strategies)):
            strategy = strategy + ", " + strategies[strategynum]
        inputs = 3
    
    if partners == 0:
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + "\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + "\'"
        else:
            query = "INSERT INTO commanders VALUES (\'" + commander + "\', 0, 0, 1)"
        execute_query(query)
    else:
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " (Partner)\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + " (Partner)\'"
        else:
            query = "INSERT INTO commanders VALUES (\'" + commander + " (Partner)\', 0, 0, 1)"
        execute_query(query)
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commandertwo + " (Partner)\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commandertwo + " (Partner)\'"
        else:
            query = "INSERT INTO commanders VALUES (\'" + commandertwo + " (Partner)\', 0, 0, 1)"
        execute_query(query)
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " and " + commandertwo + "\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + " and " + commandertwo + "\'"
        else:
            query = "INSERT INTO commanders VALUES (\'" + commander + " and " + commandertwo + "\', 0, 0, 1)"
        execute_query(query)

    decksamount = read_query("SELECT deck_numbers FROM colors WHERE color = \'" + color + "\'")
    query = "UPDATE colors SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE color = \'" + color + "\'"
    execute_query(query)

    for strat in strategies:
        decksamount = read_query("SELECT deck_numbers FROM strategies WHERE strategy = \'" + strat + "\'")
        if decksamount:
            query = "UPDATE strategies SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE strategy = \'" + strat + "\'"
        else:
            query = "INSERT INTO strategies VALUES (\'" + strat + "\', 0, 0, 1)"
        execute_query(query)
    if partners == 0:
        if inputs == 2:
            query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', \'" + color + "\', NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        if inputs == 3:
            query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', \'" + color + "\', \'" + strategy + "\', \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
    else:
        if inputs == 2:
            query = "INSERT INTO decks VALUES (\'" + commander + " and " + commandertwo + "\', \'" + deckname + "\', \'" + color + "\', NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        if inputs == 3:
            query = "INSERT INTO decks VALUES (\'" + commander + " and " + commandertwo + "\', \'" + deckname + "\', \'" + color + "\', \'" + strategy + "\', \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
    execute_query(query)
    if partners == 0:
        await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")
    else: 
        await ctx.send(deckname + " helmed by " + commander + " and " + commandertwo + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")

@bot.command(name='changedeck')
async def change_deck(ctx, *args):
    return

@bot.command(name='deletedeck')
async def delete_deck(ctx, *args):
    return

@bot.command(name='startgame')
async def game_start(ctx, *args):
    return

@bot.command(name='cancelgame')
async def game_cancel(ctx, *args):
    return

@bot.command(name='gameend')
async def game_end(ctx, *args):
    return

bot.run(TOKEN)