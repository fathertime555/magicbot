import os
import serverconnection
from discord import Intents as ints
from discord.ext import commands
from dotenv import load_dotenv
from mysql.connector import Error
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = ints.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '/', intents = intents)
connection = serverconnection.create_server_connection(os.getenv('MYSQL_HOSTNAME'), os.getenv('MYSQL_USERNAME'), os.getenv('MYSQL_PASSWORD'))

def extract_name(args):
    extracted = ""
    for x in range(len(args)):
        if x == 0:
            if args[0][0] != "(":
                return (1, args)
            extracted = args.pop(0)[1:]
            if extracted[-1] == ")":
                extracted = extracted[:-1]
                break
        elif args[0][0] == "(":
            print("Started another parentheses before closing")
            return (2, args)
        elif args[0][-1] == ")":
            extracted = extracted + " " + args.pop(0)[:-1]
            break
        elif x == len(args) and args[0][-1] != ")":
            print(x)
            print(args[0])
            print("Didn't properly close the commander name")
            return (2, args)
        else:
            extracted = extracted + " " + args.pop(0)
    return (extracted, args)

def standardize_color(color):
    color = "".join(sorted(color.upper()))
    if color == "c" or color == "ENNO" or color == "CELLOORSS":
        return "Colorless"    
    if color == "W" or color == "EHITW" or color == "EHIMNOOTW":
        return "White"
    if color == "U" or color == "BELU" or color == "BELMNOOU":
        return "Blue"
    if color == "B" or color == "ABCKL" or color == "ABCKLMNOO":
        return "Black"
    if color == "R" or color == "DER" or color == "DEMNOOR":
        return "Red"
    if color == "G" or color == "EEGNR" or color == "EEGMNNOOR":
        return "Green"
    if color == "UW" or color == "BEEHILTUW" or color == "AIORSUZ":
        return "Azorius"
    if color == "BU" or color == "ABBCEKLLU" or color == "DIIMR":
        return "Dimir"
    if color == "BR" or color == "ABCDEKLR" or color == "ADKORS":
        return "Rakdos"
    if color == "GR" or color == "DEEEGNRR" or color == "GLRUU":
        return "Gruul"
    if color == "GW" or color == "EEEGHINRTW" or color == "AEELNSSY":
        return "Selesnya"
    if color == "BW" or color == "ABCEHIKLTW" or color == "HOORVZ" or color == "EIILLLQRSUV":
        return "Orzhov"
    if color == "RU" or color == "BDEELRU" or color == "EITZZ" or color == "AIIMPRRS":
        return "Izzet"
    if color == "BG" or color == "ABCEEGKLNR" or color == "AGGILOR" or color == "BEHILMOORTW":
        return "Golgari"
    if color == "RW" or color == "DEEHIRTW" or color == "BOORS" or color == "DEHLLOOR":
        return "Boros"
    if color == "GU" or color == "BEEEGLNRU" or color == "CIIMS" or color == "ADINQRUX":
        return "Simic"
    if color == "GUW" or color == "BEEEEGHILNRTUW" or color == "ABNT" or color == "BEKORRS":
        return "Bant"
    if color == "BUW" or color == "ABBCEEHIKLLTUW" or color == "EEPRS" or color == "ABCORSU":
        return "Esper"
    if color == "BRU" or color == "ABBCDEEKLLRU" or color == "GIIRSX" or color == "AEMORSST":
        return "Grixis"
    if color == "BGR" or color == "ABCDEEEGKLNRR" or color == "DJNU" or color == "EEEIRRSTV":
        return "Jund"
    if color == "GRW" or color == "DEEEEGHINRRTW" or color == "AANY" or color == "AABCEIRTT":
        return "Naya"
    if color == "BGW" or color == "ABCEEEGHIKLNRTW" or color == "AABNZ" or color == "AADHINT":
        return "Abzan"
    if color == "RUW" or color == "BDEEEHILRTUW" or color == "AEIJKS" or color == "AGINRRU":
        return "Jeskai"
    if color == "BGU" or color == "ABBCEEEGKLLNRU" or color == "AILSTU" or color == "AGHOTZ":
        return "Sultai"
    if color == "BRW" or color == "ABCDEEHIKLRTW" or color == "ADMRU" or color == "AAISV":
        return "Mardu"
    if color == "GRU" or color == "BDEEEEGLNRRU" or color == "EMRTU" or color == "AEIKRT":
        return "Temur"
    if color == "BRUW" or color == "ACEFIIRT" or color == "ABBCDEEEHIKLLRTUW" or color == "-EEILLORRTY" or color == "EEILLORRTY":
        return "Yore-Tiller"
    if color == "BGRU" or color == "ACHOS" or color == "ABBCDEEEEGKLLNRRU" or color == "-EEGILNTY" or color == "EEGILNTY":
        return "Glint-Eye"
    if color == "BGRW" or color == "AEGGINORSS" or color == "ABCDEEEEGHIKLNRRTW" or color == "-BDDENOORU" or color == "BDDENOORU":
        return "Dune-Brood" 
    if color == "GRUW" or color == "AILMRSTU" or color == "BDEEEEEGHILNRRTUW" or color == "-ADEEIKNRRT" or color == "ADEEIKNRRT":
        return "Ink-Treader"
    if color == "BGUW" or color == "GHORTW" or color == "ABBCEEEEGHIKLLNRTUW" or color == "-ACHIMTWW" or color == "ACHIMTWW":
        return "Witch-Maw"  
    if color == "BGRUW" or color == "ABINORW" or color == "-5CLOOR" or color == "5CLOOR" or color == "CEFILOORV":
        return "WUBRG"
    return 0

def standardize_strategies(strategies):
    for strategy in range(len(strategies)):
        strategies[strategy] = strategies[strategy].capitalize()
        if strategies[strategy][-1] == ',':
            strategies[strategy] = strategies[strategy][:-1]
    return strategies

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
async def newplayer(ctx, *args):
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
async def deleteplayer(ctx):
    playerid = str(ctx.author.id)
    existingplayer = read_query("SELECT nickname FROM players WHERE player_id = " + str(ctx.author.id))[0][0]
    if not existingplayer:
        await ctx.send("You have not been registered as a contender on the field of battle. Use /newchallenger to enlist now.")
    else: 
        query = "DELETE FROM players WHERE player_id = \'" + playerid + "\'"
        execute_query(query)
        await ctx.send(existingplayer + " has fled the field of battle.")

@bot.command(name='changenickname')
async def changename(ctx, *args):
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
async def newdeck(ctx, *args):
    args = list(args)
    commander = ""
    deckname = ""
    color = ""
    strategies = []
    strategy = ""
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
    decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + "\'")
    if decksamount:
        query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + "\'"
    else:
        query = "INSERT INTO commanders VALUES (\'" + commander + "\', 0, 0, 1)"
    execute_query(query)

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
        args = extracted[1]
    player = read_query("SELECT player FROM decks WHERE deck_name = \'" + deckname + "\'")
    if player:
        await ctx.send(deckname + " already exists (Created by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + player[0][0] + "\'")[0][0] + "). Please enter a unique name for your deck or kill your competition to take the rights for yourself!") 
        return
    if len(args) == 0:
        query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', NULL, NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        execute_query(query)
        await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")     
        return
      
    extracted = extract_name(args)
    if extracted[0] == 1:
        await ctx.send("Please put the color of your deck in parentheses.")
        return
    elif extracted[0] == 2:
        await ctx.send("Please close the parentheses around the color of your deck.")
        return
    else:
        color = extracted[0]
        args = extracted[1]
    color = standardize_color(color)
    if color == 0:
        await ctx.send("Please choose a valid color for your deck.")
        return
    decksamount = read_query("SELECT deck_numbers FROM colors WHERE color = \'" + color + "\'")
    query = "UPDATE colors SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE color = \'" + color + "\'"
    execute_query(query)
    if len(args) == 0:
        query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', \'" + color + "\', NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        execute_query(query)
        await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")     
        return

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
    for strat in strategies:
        decksamount = read_query("SELECT deck_numbers FROM strategies WHERE strategy = \'" + strat + "\'")
        if decksamount:
            query = "UPDATE strategies SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE strategy = \'" + strat + "\'"
        else:
            query = "INSERT INTO strategies VALUES (\'" + strat + "\', 0, 0, 1)"
        execute_query(query)
    strategy = strategy + strategies[0]
    for strategynum in range(1,len(strategies)):
        strategy = strategy + ", " + strategies[strategynum]
    query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', \'" + color + "\', \'" + strategy + "\', \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
    execute_query(query)
    await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")     

bot.run(TOKEN)