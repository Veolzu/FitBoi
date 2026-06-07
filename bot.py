import info
import secret
import datetime
import discord

from discord.ext import commands



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


TOTAL_CALORIES = 2000

@bot.event
async def on_ready():
    print("The bot is ready!")


@bot.command()
async def empty(ctx):
    print("Emptying channels")
    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)
    await daily.purge()
    await tracking.purge()

    total_calories = TOTAL_CALORIES
    current_calories = total_calories
    exercise_calories = 0
    steps = 0
    eaten = []

    await tracking.send(f"{total_calories},{current_calories},{exercise_calories},{steps}," + ",".join(str(x) for x in eaten))
    print("Resetted")
    return


@bot.command()
async def weight(ctx, weight):
    today_str = datetime.datetime.now().strftime("%d.%m.%Y")

    long_term = bot.get_channel(info.long_term_tracking_channel)
    await long_term.send(f"{today_str}, {weight}")
    return


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)
    recipe = bot.get_channel(info.recipe_channel)
    long_term = bot.get_channel(info.long_term_tracking_channel)

    if message.channel.id != info.daily_channel:
        print("Not the right channel")
        return

    recipes = {}
    async for recipe_msg in recipe.history(limit=None):
        cont = recipe_msg.content.split(",")
        recipes[cont[0]] = (cont[1], cont[2])    

    msgs = []
    async for tracking_msg in tracking.history(limit=None):
        msgs.append(tracking_msg.content)

    if len(msgs) != 0:
        last_msg = msgs[0]
        total_calories = int(last_msg.split(",")[0])
        current_calories = int(last_msg.split(",")[1])
        exercise_calories = int(last_msg.split(",")[2])
        steps = int(last_msg.split(",")[3])
        eaten = last_msg.split(",")[4:]
    else:
        eaten = []
        total_calories = TOTAL_CALORIES
        current_calories = total_calories
        exercise_calories = 0
        steps = 0
    

    keys = recipes.keys()
    if message.content in keys:
        current_calories -= int(recipes[message.content][0])
        eaten.append((recipes[message.content][1], recipes[message.content][0]))

        await tracking.send(f"{total_calories},{current_calories},{exercise_calories},{steps}," + ",".join(str(x) for x in eaten))

bot.run(secret.TOKEN)
