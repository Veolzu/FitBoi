import info
import secret
import datetime
import discord

from discord.ext import commands



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


TOTAL_CALORIES = 2000

class Stats:
    def __init__(self, total_calories, current_calories, exercise_calories, steps, exercise, eaten):
        self.total_calories = total_calories
        self.current_calories = current_calories
        self.exercise_calories = exercise_calories
        self.steps = steps
        self.exercise = exercise
        self.eaten = eaten
    
    def reset(self):
        self.total_calories = TOTAL_CALORIES
        self.current_calories = TOTAL_CALORIES
        self.exercise_calories = 0
        self.steps = 0
        self.exercise = []
        self.eaten = []

    def get_latest(self, msg):
        if msg is None:
            self.reset()
            return
        
        last_msg = msg.content
        separator = "; "

        self.total_calories = int(last_msg.split(separator)[0])
        self.current_calories = int(last_msg.split(separator)[1])
        self.exercise_calories = int(last_msg.split(separator)[2])
        self.steps = int(last_msg.split(separator)[3])

        eaten = last_msg.split(separator)[5].split(":", 1)
        if len(eaten) > 1:
            self.eaten = [item.strip() for item in eaten[1].split(",") if item.strip()]
        else:
            self.eaten = []

        exercise = last_msg.split(separator)[4].split(":", 1)
        if len(exercise) > 1:
            self.exercise = [item.strip() for item in exercise[1].split(",") if item.strip()]
        else:
            self.exercise = []

    async def update_tracking(self, tracking_channel):
        await tracking_channel.send(f"{self.total_calories}; {self.current_calories}; {self.exercise_calories}; {self.steps};  exercise: "+ ",".join(str(x) for x in self.exercise) + "; eaten: " + ",".join(str(x) for x in self.eaten))


@bot.event
async def on_ready():
    print("The bot is ready!")

@bot.command()
async def ate(ctx, *, arg):
    try:
        calories, food = arg.split(" ", 1)
    except ValueError:
        await ctx.send("Please provide both food name and calories.")
        return

    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])
    msg = await tracking.fetch_message(tracking.last_message_id)
    stats.get_latest(msg)

    stats.current_calories -= int(calories)
    stats.eaten.append((food, calories))
    await stats.update_tracking(tracking)


@bot.command()
async def empty(ctx):
    print("Emptying channels")
    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])
    last_msg = await tracking.fetch_message(tracking.last_message_id)
    stats.get_latest(last_msg)


    long_term = bot.get_channel(info.long_term_tracking_channel)
    try:
        last_msg = await long_term.fetch_message(long_term.last_message_id)
    except:
        last_msg = None

    if last_msg and last_msg.embeds:
        embed = last_msg.embeds[0]
        title = embed.title
        description = embed.description
        
        if len(description) < 30:
            print("Updating long term tracking")
            new_description = f"{description}\n {TOTAL_CALORIES - stats.current_calories+stats.exercise_calories}/{TOTAL_CALORIES+stats.exercise_calories}\n{stats.exercise_calories} calories burned\n{stats.steps} steps\nExcercise: " + "\n".join(str(x) for x in stats.exercise) + "\nEaten: " + "\n".join(str(x) for x in stats.eaten)
            new_embed = discord.Embed(title=title, description=new_description)
            await last_msg.edit(embed=new_embed)

    await daily.purge()
    await tracking.purge()

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])

    await stats.update_tracking(tracking)
    print("Resetted")
    return


@bot.command()
async def weight(ctx, weight):
    today_str = datetime.datetime.now().strftime("%d.%m.%Y")

    long_term = bot.get_channel(info.long_term_tracking_channel)
    embed = discord.Embed(title=f"{today_str}", description=f"weight: {weight}")
    await long_term.send(embed=embed)
    return

@bot.command()
async def move(ctx, *, arg):
    try:
        calories, type_ = arg.split(" ", 1)
    except ValueError:
        await ctx.send("Please provide both exercise type and calories burned.")
        return
    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])
    msg = await tracking.fetch_message(tracking.last_message_id)
    stats.get_latest(msg)

    stats.current_calories += int(calories)
    stats.exercise_calories += int(calories)
    stats.exercise.append((type_, calories))
    await stats.update_tracking(tracking)

@bot.command()
async def steps(ctx, steps):
    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])
    msg = await tracking.fetch_message(tracking.last_message_id)
    stats.get_latest(msg)

    stats.steps = int(steps)

    await stats.update_tracking(tracking)


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if message.channel.id != info.daily_channel:
        print("Not the right channel")
        return

    daily = bot.get_channel(info.daily_channel)
    tracking = bot.get_channel(info.tracking_channel)
    recipe = bot.get_channel(info.recipe_channel)

    recipes = {}
    async for recipe_msg in recipe.history(limit=None):
        cont = recipe_msg.content.split(",")
        recipes[cont[0]] = (cont[1], cont[2])    

    stats = Stats(TOTAL_CALORIES, TOTAL_CALORIES, 0, 0, [], [])

    msg = await tracking.fetch_message(tracking.last_message_id)
    stats.get_latest(msg)

    keys = recipes.keys()
    if message.content in keys:
        stats.current_calories -= int(recipes[message.content][0])
        stats.eaten.append((recipes[message.content][1], recipes[message.content][0]))

        await stats.update_tracking(tracking)

bot.run(secret.TOKEN)
