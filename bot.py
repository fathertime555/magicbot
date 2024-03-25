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
    strategies = ()
    playerid = str(ctx.author.id)

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

    if len(args) == 0:
        player = read_query("SELECT player FROM decks WHERE deck_name = \'" + deckname + "\'")
        if player:
            await ctx.send(deckname + " already exists (Created by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + player[0][0] + "\'")[0][0] + "). Please enter a unique name for your deck or kill your competition to take the rights for yourself!") 
            return
        now = datetime.now()
        decksamount = read_query("SELECT deck_numbers FROM commanders WHERE commander = \'" + commander + "\'")
        if decksamount:
            query = "UPDATE commanders SET deck_numbers = " + str(decksamount[0][0] + 1) + " WHERE commander = \'" + commander + "\'"
            execute_query(query)
        else:
            query = "INSERT INTO commanders VALUES (\'" + commander + "\', 0, 0, 1)"
            execute_query(query)
        query = "INSERT INTO decks VALUES (\'" + commander + "\', \'" + deckname + "\', NULL, NULL, \'" + str(playerid) + "\', \'" + now.strftime("%Y-%m-%d") + "\', 0, 0, 0)"
        execute_query(query)
        await ctx.send(deckname + " helmed by " + commander + " has been deployed to the field of battle by " + read_query("SELECT nickname FROM players WHERE player_id = \'" + playerid + "\'")[0][0] + "!")     
        return  

    await ctx.send(commander + " is the name of the commander.") 
    await ctx.send(deckname + " is the name of the deck.") 

bot.run(TOKEN)