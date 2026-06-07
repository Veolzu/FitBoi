import info
import secret
import discord
import datetime


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print("The bot is ready!")



@client.event
async def on_message(message):

    if message.author == client.user:
        return
    
    id = client.get_guild(info.server_id)

    daily = client.get_channel(info.daily_channel)
    tracking = client.get_channel(info.tracking_channel)

    recipe = client.get_channel(info.recipe_channel)
    long_term = client.get_channel(info.long_term_tracking_channel)
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
        total_calories = 2000
        current_calories = total_calories
        exercise_calories = 0
        steps = 0



    
    if message.channel.id != info.daily_channel:
        print("Not the right channel")
        return
    
    if message.content.startswith("!empty"):
        await daily.purge()
        await tracking.purge()
        total_calories = 2000
        current_calories = total_calories
        exercise_calories = 0
        steps = 0
        eaten = []
        await tracking.send(f"{total_calories},{current_calories},{exercise_calories},{steps}," + ",".join(str(x) for x in eaten))
        print("Resetted")
        return
    
    if message.content.startswith("!weight"):
        weight = message.content.split(" ")[1]
        today_str = datetime.datetime.now().strftime("%d.%m.%Y")

        await long_term.send(f"{today_str},{weight}")
        return

    keys = recipes.keys()
    if message.content in keys:
        current_calories -= int(recipes[message.content][0])
        eaten.append((recipes[message.content][1], recipes[message.content][0]))

        await tracking.send(f"{total_calories},{current_calories},{exercise_calories},{steps}," + ",".join(str(x) for x in eaten))

client.run(secret.TOKEN)
