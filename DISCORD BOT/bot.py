import discord
import asyncio
import requests
import os
import discord.utils
import configparser
import subprocess
from discord.ext import commands
from discord.utils import get
from discord.ext.commands import Bot

config = configparser.ConfigParser()
config.read('botdatabase.ini')
intents = discord.Intents.default()
intents.members = True
bot = Bot(command_prefix = '!', intents=intents)


def fetchurlcorectly():
    domainnormalized = domain
    domainwithoutslash = domainnormalized[:-1]
    if domain.endswith('/'):
        return domainwithoutslash
    else:
        return domainnormalized

#ignore this 
token = str(config['botinfo']['bottoken'])
memberrole = config['botinfo']['memberrole']
clientid = config['botinfo']['client_id']
therestorekey = config['botinfo']['therestorekey']
domain = config['botinfo']['domain']
exchangepass = config['botinfo']['exchangepass']
tempkey = config['botinfo']['tempkey']
url = f'https://discord.com/oauth2/authorize?response_type=code&client_id={clientid}&scope=identify+guilds.join&state=15773059ghq9183habn&redirect_uri={fetchurlcorectly()}/discordauth'

        

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

@bot.event
async def on_ready():
    cls()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='Verification')) # you can change this if you want
    print('Bot is ready.')
    print(f'Logged in as {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    print('------')

@bot.event
async def on_guild_join(guild):
    await guild.owner.send("To restore Please enter the old server ID with the command !restore <your restore key> <serverid> , here is the new server ID: " + str(guild.id))

@bot.event
async def on_member_join(member):
    server = bot.get_guild(int(member.guild.id))
    if checkifverifydone(member.id, member.guild.id) == 'true':
        print('Verified')
        role = discord.utils.get(server.roles, name=memberrole)
        await member.add_roles(role)
        embed3=discord.Embed(title=f"Welcome back to {server}", description=f"You are verified.", color=0xfbff00)
        embed3.set_footer(text="Made with love :)")
        embed3.set_thumbnail(url=member.avatar_url)
        await member.send(embed=embed3)

    else:
        embed=discord.Embed(title="Verification", description=f"Welcome, to proceed in the server, follow the link below to verify.\n[https://discord.com/verify/961874227532189194]({url})", color=0xfbff00)
        embed.set_footer(text="Once you click on the 'Authorize' button, use `!verify` in this DM.")
        embed.set_thumbnail(url=member.avatar_url)
        await member.send(embed=embed)
        sendrequestforpending(member.id, member.guild.id)
        
@bot.event
async def on_message(message):
    print("New message: " + message.content + " - " + message.author.name)
    if message.author == bot.user:
        pass
    await bot.process_commands(message)


@bot.command()
async def restore(ctx, key, guildid):
    await ctx.message.delete()
    if key == therestorekey:
        if restoremember(guildid, ctx.message.guild.id) == 'succsess':
            await ctx.send('Restored.', delete_after=3)
        else:
            await ctx.send('Not restored.', delete_after=3)
    else:
        await ctx.send('Nice try bozo.', delete_after=3)

@bot.command()
async def verify(ctx):
    server = bot.get_guild(int(config['memberids'][str(ctx.author.id)]))
    role = discord.utils.get(server.roles, name=memberrole)
    member = server.get_member(ctx.message.author.id)
    if checkifverifydone(ctx.author.id, config['memberids'][str(ctx.author.id)]) == 'true':
        #role user as verified
        await member.add_roles(role)
        await member.send(f'Your verified. have fun!')
    elif checkifverifydone(ctx.author.id, config['memberids'][str(ctx.author.id)]) == 'error':
        await ctx.send(f'Error verifying. Please contact a moderator.', delete_after=3)
    else:
        await ctx.send(f'Your not verified. Please contact a administrator.', delete_after=3)


@bot.command()
async def test(ctx):
    await ctx.send('test')

def sendrequestforpending(idofuser, guildid):
    config['memberids'][str(idofuser)] = str(guildid)
    with open('botdatabase.ini', 'w') as configfile:
        config.write(configfile)
    try:
        r1 = requests.post(f'{domain}/requestid', json={'key': exchangepass, 'id': idofuser})
        print(r1.text)
        return r1.text
    except:
        return 'error sending'

def checkifverifydone(idofuser, theguildid):
    try:
        r3 = requests.post(f'{domain}/checkifverifydone', json={'key': exchangepass, 'id': idofuser,'guildid': theguildid})
        print(r3.text)
        return r3.text
    except:
        return 'error'

def restoremember(guildid, newguildid):
    r2 = requests.post(f'{domain}/restore', json={'code': exchangepass, 'guildid': guildid, 'newguildid': newguildid})
    print(r2.text)
    return r2.text


def start():
    if config['setup']['setup'] == 'no':
        setup()
    else:
        r = requests.post(f'{domain}/working')
        if r.text == 'true':
            bot.run(token)
        else:
            print('Server is not running correctly. Please check your Flask web server.')


def setup():
    cls()
    print("Welcome to the bot setup be sure to setup first teh flask server")
    print("If you have not setup the flask server yet, please do so now.")
    print("")
    print("If you have setup the flask server, please enter the following information.")
    print("")
    print("Enter the domain/ip of the flask server: ")
    domain = input()
    r = requests.post(f'{domain}/working')
    if r.text == 'true':
        pass
    else:
        print('Server is not running correctly. Please check your Flask web server.')
        waitformesweety = input()
    r2 = requests.post(f'{domain}/data', json={'key': 'test', 'dataset': 'pass'})
    config['botinfo']['tempkey'] = r2.text
    with open('botdatabase.ini', 'w') as configfile:
        config.write(configfile)
    r1 = requests.post(f'{domain}/data', json={'key': tempkey, 'dataset': 'CLIENT_ID'})
    r3 = requests.post(f'{domain}/data', json={'key': tempkey, 'dataset': 'bottoken'})
    r5 = requests.post(f'{domain}/data', json={'key': tempkey, 'dataset': 'exchangepass'})
    r7 = requests.post(f'{domain}/data', json={'key': tempkey, 'dataset': 'verifiedrole'})
    r8 = requests.post(f'{domain}/data', json={'key': tempkey, 'dataset': 'restorekey'})
    config['botinfo']['bottoken'] = r3.text
    config['botinfo']['memberrole'] = r7.text
    config['botinfo']['therestorekey'] = r8.text
    config['botinfo']['exchangepass'] = r5.text
    config['botinfo']['domain'] = domain
    config['botinfo']['client_id'] = r1.text
    config['setup']['setup'] = 'yes'
    with open('botdatabase.ini', 'w') as configfile:
        config.write(configfile)
    print('Setup complete. Please press any button to start the bot')
    waitformesweety = input()
    try:
        subprocess.call('py bot.py', shell=True)
    except:
        try:
            subprocess.call('python bot.py', shell=True)
        except:
            try:
                subprocess.call('python3 bot.py', shell=True)
            except:
                print('Could not start bot. Please check your python installation.')

start()
