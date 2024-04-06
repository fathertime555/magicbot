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
                strategy = strategy[:(letter + 1)] + strategy[letter + 1].upper() + strategy[(letter + 2):]
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
        print(query)
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
    #Only thing left to add is validator, use validator to allow people to use non-legendary cards as commanders?
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
        await ctx.send("Please register yourself as a contender in the field of battle using /newchallenger.")
        return
    
    if len(args) == 0:
        await ctx.send("Please enter at least the commander(s) of your deck and its name.")
        return
    
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the name of your commander(s) in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the name of your commander(s).")
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

        if ("Legendary" and "Creature") not in responseone["type_line"] and "Background" not in responseone["type_line"] and ("Legendary Planeswalker" not in responseone["type_line"] or "can be your commander" not in responseone["oracle_text"]) and "Grist, the Hunger Tide" not in responseone["name"]:
            await ctx.send("Please choose a legal commander for your first partner.")
            return
        
        if ("Legendary" and  "Creature") not in responsetwo["type_line"] and "Background" not in responsetwo["type_line"] and ("Legendary Planeswalker" not in responsetwo["type_line"] or "can be your commander" not in responsetwo["oracle_text"]) and "Grist, the Hunger Tide" not in responsetwo["name"]:
            await ctx.send("Please choose a legal commander for your second partner.")
            return
        
        if (("Legendary" and "Creature") in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"]) and "Choose a Background" not in responseone["oracle_text"] and "Friends forever" not in responseone["keywords"]) or ("Legendary Planeswalker" in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"])):
            await ctx.send("Please choose a legal partner for your first partner.")
            return

        if (("Legendary" and "Creature") in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"]) and "Choose a Background" not in responsetwo["oracle_text"] and "Friends forever" not in responsetwo["keywords"]) or ("Legendary Planeswalker" in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"])):
            await ctx.send("Please choose a legal partner for your second partner.")
            return
        
        if ("Friends forever" in responseone["keywords"] and "Friends forever" not in responsetwo["keywords"]) or ("Friends forever" not in responseone["keywords"] and "Friends forever" in responsetwo["keywords"]): 
            await ctx.send("Unfortunately the partners you chose do not partner with each other.")
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
        if ("Legendary" and "Creature") not in response["type_line"] and ("Legendary Planeswalker" not in response["type_line"] or "can be your commander" not in response["oracle_text"]) and "Grist, the Hunger Tide" not in response["name"]:
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
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'"
        else:
            query = "INSERT INTO commanders VALUES (\'" + commander + " and " + commandertwo + " (Partners)\', 0, 0, 1)"
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
            query = "INSERT INTO decks VALUES (\'" + commander + " and " + commandertwo + " (Partners)\', \'" + deckname + "\', \'" + color + "\', NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        if inputs == 3:
            query = "INSERT INTO decks VALUES (\'" + commander + " and " + commandertwo + " (Partners)\', \'" + deckname + "\', \'" + color + "\', \'" + strategy + "\', \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
    execute_query(query)
    if partners == 0:
        await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")
    else: 
        await ctx.send(deckname + " helmed by " + commander + " and " + commandertwo + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")

@bot.command(name='changedeck')
async def change_deck(ctx, *args):
    
    playerid = str(ctx.author.id)
    queries = []
    now = datetime.now()
    args = list(args)
    namechange = False
    newname = ""

    if not read_query("SELECT player_id FROM players WHERE player_id = \'" + playerid + "\'"):
        await ctx.send("Please register yourself as a contender in the field of battle using /newchallenger.")
        return

    if len(args) == 0:
        await ctx.send("Please enter the name of your deck, what part of the deck you would like to edit, and what you would like to edit it to.")
        return
    
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the name of the deck you are changing in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the name of the deck you are changing.")
        return
    else:
        deck = extracted[0]
        args = extracted[1]

    check = read_query("SELECT player FROM decks WHERE deck_name = \'" + deck + "\'")
    if not check:
        await ctx.send("I cannot find a deck of that name in the registry of battle.")
        return
    if check[0][0] != playerid:
        await ctx.send("You are trying to edit a deck you do not command. If I might suggest, a knife to the throat is an easy way to convince " + read_query("SELECT nickname FROM players WHERE player_id = " + str(check[0][0]))[0][0] + " to make those changes for you.")
        return
    
    message = read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + " has changed their deck " + deck + "."

    if len(args) == 0:
        await ctx.send("Please enter what part of the deck you would like to edit and what you would like to edit it to.")
        return
    
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the part of the deck you are changing in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the part of the deck you are changing.")
        return
    else:
        change = extracted[0]
        args = extracted[1]
    change = change.lower()
    change = change.split()

    for tochange in change:
        if tochange[-1] == ",":
            tochange = tochange[:-1]
        if tochange == "commander":
            if len(args) == 0:
                await ctx.send("Please enter at least the commander that will be replacing the current commander of your deck.")
                return
            extracted = extract_name(args)
            if extracted[0] == 1:
                await ctx.send("Please put the name of your new commander(s) in parentheses.")
                return
            elif extracted[0] == 2:
                await ctx.send("Please close the parentheses around the name of your new commander(s).")
                return
            else:
                commander = extracted[0]
                args = extracted[1]
            color = ""
            partners = 0
            apiurl = "https://api.scryfall.com/cards/named?exact="
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

                if ("Legendary" and "Creature") not in responseone["type_line"] and "Background" not in responseone["type_line"] and ("Legendary Planeswalker" not in responseone["type_line"] or "can be your commander" not in responseone["oracle_text"]) and "Grist, the Hunger Tide" not in responseone["name"]:
                    await ctx.send("Please choose a legal commander for your first partner.")
                    return
        
                if ("Legendary" and  "Creature") not in responsetwo["type_line"] and "Background" not in responsetwo["type_line"] and ("Legendary Planeswalker" not in responsetwo["type_line"] or "can be your commander" not in responsetwo["oracle_text"]) and "Grist, the Hunger Tide" not in responsetwo["name"]:
                    await ctx.send("Please choose a legal commander for your second partner.")
                    return
        
                if (("Legendary" and "Creature") in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"]) and "Choose a Background" not in responseone["oracle_text"] and "Friends forever" not in responseone["keywords"]) or ("Legendary Planeswalker" in responseone["type_line"] and ("Partner with" not in responseone["keywords"] and "Partner" not in responseone["keywords"])):
                    await ctx.send("Please choose a legal partner for your first partner.")
                    return

                if (("Legendary" and "Creature") in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"]) and "Choose a Background" not in responsetwo["oracle_text"] and "Friends forever" not in responsetwo["keywords"]) or ("Legendary Planeswalker" in responsetwo["type_line"] and ("Partner with" not in responsetwo["keywords"] and "Partner" not in responsetwo["keywords"])):
                    await ctx.send("Please choose a legal partner for your second partner.")
                    return

                if ("Friends forever" in responseone["keywords"] and "Friends forever" not in responsetwo["keywords"]) or ("Friends forever" not in responseone["keywords"] and "Friends forever" in responsetwo["keywords"]): 
                    await ctx.send("Unfortunately the partners you chose do not partner with each other.")
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
                if ("Legendary" and "Creature") not in response["type_line"] and ("Legendary Planeswalker" not in response["type_line"] or "can be your commander" not in response["oracle_text"]) and "Grist, the Hunger Tide" not in response["name"]:
                    await ctx.send("Please choose a legal commander for your deck.")
                    return
                commander = response["name"] 
                for i in range(len(commander)):
                    if commander[-i] == "\"" or commander[-i] == "\'":
                        commander = commander[:-i] + "\\" + commander[-i:]
                for i in response["color_identity"]:
                    color = color + i
                color = standardize_color(color)
            oldcommander = read_query("SELECT commander FROM decks WHERE deck_name = \'" + deck + "\'")[0][0]
            oldcolor = read_query("SELECT color FROM decks WHERE deck_name = \'" + deck + "\'")[0][0]
            if partners == 0:
                checkpartner = oldcommander.split()
                if checkpartner[-1] == "(Partners)":
                    oldcommanderone = checkpartner[0]
                    oldcommandertwo = ""
                    secondcommander = False
                    for word in range(1,len(checkpartner)):              
                        if checkpartner[word] == "and":
                            secondcommander = True
                        elif checkpartner[word] == "(Partners)":
                            break
                        elif not secondcommander:
                            oldcommanderone = oldcommanderone + " " + checkpartner[word]
                        elif secondcommander:
                            oldcommandertwo = oldcommandertwo + " " + checkpartner[word]
                    oldcommandertwo = oldcommandertwo[1:]

                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommanderone + " (Partner)\'")[0][0]
                    if deckcheck == 1:
                        queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommanderone + " (Partner)\'")
                    else:
                        deckcheck = deckcheck - 1
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommanderone + " (Partner)\'")  
                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommandertwo + " (Partner)\'")[0][0]
                    if deckcheck == 1:
                        queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommandertwo + " (Partner)\'")
                    else:
                        deckcheck = deckcheck - 1
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommandertwo + " (Partner)\'") 
                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommander + "\'")[0][0]
                    if deckcheck == 1:
                        queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommander + "\'")
                    else:
                        deckcheck = deckcheck - 1
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommander + "\'")

                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + "\'")
                    if deckcheck:
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + "\'")
                    else:
                        queries.append("INSERT INTO commanders VALUES (\'" + commander + "\', 0, 0, 1)")
                    queries.append("UPDATE decks SET commander = \'" + commander + "\' WHERE deck_name = \'" + deck + "\'")
                else:
                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommander + "\'")[0][0]
                    if deckcheck == 1:
                        queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommander + "\'")
                    else:
                        deckcheck = deckcheck - 1
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommander + "\'")  

                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + "\'")
                    if deckcheck:
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + "\'")
                    else:
                        queries.append("INSERT INTO commanders VALUES (\'" + commander + "\', 0, 0, 1)")
                    queries.append("UPDATE decks SET commander = \'" + commander + "\' WHERE deck_name = \'" + deck + "\'")

            else:
                checkpartner = oldcommander.split()
                if checkpartner[-1] == "(Partners)":
                    oldcommanderone = checkpartner[0]
                    oldcommandertwo = ""
                    secondcommander = False
                    for word in range(1,len(checkpartner)):              
                        if checkpartner[word] == "and":
                            secondcommander = True
                        elif checkpartner[word] == "(Partners)":
                            break
                        elif not secondcommander:
                            oldcommanderone = oldcommanderone + " " + checkpartner[word]
                        elif secondcommander:
                            oldcommandertwo = oldcommandertwo + " " + checkpartner[word]
                    oldcommandertwo = oldcommandertwo[1:]
                    
                    if oldcommanderone != commander and oldcommanderone != commandertwo:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommanderone + " (Partner)\'")[0][0]
                        if deckcheck == 1:
                            queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommanderone + " (Partner)\'")
                        else:
                            deckcheck = deckcheck - 1
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommanderone + " (Partner)\'")
                    if oldcommandertwo != commander and oldcommandertwo != commandertwo:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommandertwo + " (Partner)\'")[0][0]
                        if deckcheck == 1:
                            queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommandertwo + " (Partner)\'")
                        else:
                            deckcheck = deckcheck - 1
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommandertwo + " (Partner)\'")
                    if (oldcommandertwo != commander and oldcommandertwo != commandertwo) or (oldcommanderone != commander and oldcommanderone != commandertwo):
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommander + "\'")[0][0]
                        if deckcheck == 1:
                            queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommander + "\'")
                        else:
                            deckcheck = deckcheck - 1
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommander + "\'")
                    
                    if commander != oldcommanderone and commander != oldcommandertwo:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " (Partner)\'")
                        if deckcheck:
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + " (Partner)\'")
                        else:
                            queries.append("INSERT INTO commanders VALUES (\'" + commander + " (Partner)\', 0, 0, 1)")
                    if commandertwo != oldcommanderone and commandertwo != oldcommandertwo:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commandertwo + " (Partner)\'")
                        if deckcheck:
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commandertwo + " (Partner)\'")
                        else:
                            queries.append("INSERT INTO commanders VALUES (\'" + commandertwo + " (Partner)\', 0, 0, 1)")
                    if (commandertwo != oldcommanderone and commandertwo != oldcommandertwo) or (commander != oldcommanderone and commander != oldcommandertwo):
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'")
                        if deckcheck:
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'")
                        else:
                            queries.append("INSERT INTO commanders VALUES (\'" + commander + " and " + commandertwo + " (Partners)\', 0, 0, 1)")
                    queries.append("UPDATE decks SET commander = \'" + commander + " and " + commandertwo + " (Partners)\' WHERE deck_name = \'" + deck + "\'")
                
                else:
                    if oldcommander != commander and oldcommander != commandertwo:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + oldcommander + "\'")[0][0]
                        if deckcheck == 1:
                            queries.append("DELETE FROM commanders WHERE commander = \'" + oldcommander + "\'")
                        else:
                            deckcheck = deckcheck - 1
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck) + " WHERE commander = \'" + oldcommander + "\'")

                    if commander != oldcommander:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " (Partner)\'")
                        if deckcheck:
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + " (Partner)\'")
                        else:
                            queries.append("INSERT INTO commanders VALUES (\'" + commander + " (Partner)\', 0, 0, 1)")
                    if commandertwo != oldcommander:
                        deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commandertwo + " (Partner)\'")
                        if deckcheck:
                            queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commandertwo + " (Partner)\'")
                        else:
                            queries.append("INSERT INTO commanders VALUES (\'" + commandertwo + " (Partner)\', 0, 0, 1)")
                    deckcheck = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'")
                    if deckcheck:
                        queries.append("UPDATE commanders SET deck_numbers = " + str(deckcheck[0][0] + 1) + " WHERE commander = \'" + commander + " and " + commandertwo + " (Partners)\'")
                    else:
                        queries.append("INSERT INTO commanders VALUES (\'" + commander + " and " + commandertwo + " (Partners)\', 0, 0, 1)")
                    queries.append("UPDATE decks SET commander = \'" + commander + " and " + commandertwo + " (Partners)\' WHERE deck_name = \'" + deck + "\'")
                commander = commander + " and " + commandertwo + " (Partners)"

            if oldcolor != color:
                deckcheck = read_query("SELECT deck_numbers FROM colors WHERE color = \'" + oldcolor + "\'")[0][0]
                queries.append("UPDATE colors SET deck_numbers = " + str(deckcheck - 1) + " WHERE color = \'" + oldcolor + "\'")
                deckcheck = read_query("SELECT deck_numbers FROM colors WHERE color = \'" + color + "\'")[0][0]
                queries.append("UPDATE colors SET deck_numbers = " + str(deckcheck + 1) + " WHERE color = \'" + color + "\'")
                queries.append("UPDATE decks SET color = \'" + color + "\' WHERE deck_name = \'" + deck + "\'")

            message = message + " They have changed their commander(s) from " + oldcommander + " to " + commander + "."

        elif tochange == "deckname":
            if len(args) == 0:
                await ctx.send("Please enter at least the name that will be replacing the current name of your deck.")
                return
            extracted = extract_name(args)
            if extracted[0] == 1:
                await ctx.send("Please put the new name of your deck in parentheses.")
                return
            elif extracted[0] == 2:
                await ctx.send("Please close the parentheses around the new name of your deck.")
                return
            else:
                newname = extracted[0]
                args = extracted[1]
            for i in range(len(newname)):
                if newname[-i] == "\"" or newname[-i] == "\'":
                    newname = newname[:-i] + "\\" + newname[-i:]
            queries.append("UPDATE decks SET deck_name = \'" + newname + "\' WHERE deck_name =  \'" + deck + "\'")
            message = message + " They have changed the name of the deck to " + newname + "."
            namechange = True

        elif tochange == "strategies":
            strategy = ""
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
            
            oldstrategiesstring = read_query("SELECT strategy FROM decks WHERE deck_name = \'" + deck + "\'")[0][0]
            oldstrategiestemp = oldstrategiesstring.split()
            oldstrategies = []
            for item in oldstrategiestemp:
                if item[-1] == ",":
                    item = item[:-1]
                    oldstrategies.append(item)
                else: 
                    oldstrategies.append(item)
                if item not in strategies:
                    itemnum = read_query("SELECT deck_numbers FROM strategies WHERE strategy = \'" + item + "\'")[0][0]
                    if itemnum == 1:
                        queries.append("DELETE FROM strategies WHERE strategy = \'" + item + "\'")
                    else:
                        queries.append("UPDATE strategies SET deck_numbers = " + str(itemnum - 1) + " WHERE strategy = \'" + item + "\'")
            
            for item in strategies:
                if item not in oldstrategies:
                    itemnum = read_query("SELECT deck_numbers FROM strategies WHERE strategy = \'" + item + "\'")
                    if itemnum:
                        queries.append("UPDATE strategies SET deck_numbers = " + str(itemnum[0][0] + 1) + " WHERE strategy = \'" + item + "\'")
                    else:
                        if namechange:
                            queries.append("INSERT INTO strategies VALUES (\'" + item + "\', " + str(read_query("SELECT wins FROM decks WHERE deck_name = \'" + newname + "\'")[0][0]) + ", " + str(read_query("SELECT losses FROM decks WHERE deck_name = \'" + newname + "\'")[0][0]) + ", 1)")

                        else:
                            queries.append("INSERT INTO strategies VALUES (\'" + item + "\', " + str(read_query("SELECT wins FROM decks WHERE deck_name = \'" + deck + "\'")[0][0]) + ", " + str(read_query("SELECT losses FROM decks WHERE deck_name = \'" + deck + "\'")[0][0]) + ", 1)")

            strategy = strategy + strategies[0]
            for strategynum in range(1,len(strategies)):
                strategy = strategy + ", " + strategies[strategynum]
            if namechange:
                queries.append("UPDATE decks SET strategy = \'" + strategy + "\' WHERE deck_name = \'" + newname + "\'")
            else:
                queries.append("UPDATE decks SET strategy = \'" + strategy + "\' WHERE deck_name = \'" + deck + "\'")
            message = message + " They have changed the strategy(s) of the deck from " + oldstrategiesstring + " to " + strategy + "."

        else:
            await ctx.send("Please enter some combination of commander, deckname, or strategies as what you want to edit in the deck.")

    if namechange:
        queries.append("UPDATE decks SET last_edited = \'" + str(now) + "\' WHERE deck_name = \'" + newname + "\'")
    else:
        queries.append("UPDATE decks SET last_edited = \'" + str(now) + "\' WHERE deck_name = \'" + deck + "\'")
    for query in queries:
        execute_query(query)
    await ctx.send(message)

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