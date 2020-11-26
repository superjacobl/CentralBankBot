import discord
from dotenv import load_dotenv
load_dotenv()
import requests
import json,logging
from urllib.request import Request, urlopen
import api,svapi
import os
import json
import time
import string,random
import asyncio
import classes
import save_load
from cryptography.fernet import Fernet


global total_bond_worth_issued
global bond__worth_limit

bond__worth_limit = 10000000
total_bond_worth_issued = 0

#bond class: parent bond object
bond_types = {}

#The "30" means the days until maturity
b = classes.bond(30)
#Yield/Interest Rate
#Yield of 4% would be 0.04
#Yield / 100
b.interest = 0.04
#Max number of this type of bond users/groups can buy
b.limit = 50
#Bond Class name
b.bond_class = "Short"
bond_types[b.bond_class] = b

b = classes.bond(60)
b.interest = 0.055
b.bond_class = "Medium"
b.limit = 150
bond_types[b.bond_class] = b

b = classes.bond(90)
b.interest = 0.07
b.bond_class = "Long"
b.limit = 450
bond_types[b.bond_class] = b

logging.basicConfig(level=logging.ERROR)
async def log(string="",embed=False):
  if not embed:
    await logging_channel.send(string)
  else:
    await logging_channel.send(embed=embed)
async def send_dm(member, content):
    channel = await member.create_dm()
    await channel.send(content)
async def send_dm_embed(member, content):
    channel = await member.create_dm()
    await channel.send(embed=content)
TOKEN = os.getenv("token")
client = discord.Client()

global accounts
accounts = {}

accounts = save_load.load()

for item in accounts:
  item = accounts[item]
  for b in item.bonds:
    b = item.bonds[b]
    total_bond_worth_issued += b.base
    if not b.bond_class == "":
      bond_types[b.bond_class].issued += 1

@client.event
async def on_ready():
  server = client.get_guild(int(os.getenv("discord_server_id")))
  global logging_channel
  logging_channel = client.get_channel(int(os.getenv("logging_channel_id")))
  await log("I love money!!")
@client.event
async def on_message(message):
    global total_bond_worth_issued
    content = message.content
    command = content.split(" ")[0].replace("/","")
    line = content.split(" ")
    author = message.author
    if len(content) == 0:
      return None
    if content[0] == "/":
        user_id = message.author.id
        server = message.guild
        employee_role = discord.utils.get(server.roles, name=os.getenv("rolenametouseadmincommands"))
        member = message.author
        employee = False
        employee_commands = ["force_yield_update","nullaccount","test","admingive"]
        if employee_role in member.roles:
          employee = True
          if employee:
            args = message.content.split(" ")
            if command == "admingive":
              if len(args) < 4:
                await message.channel.send("Please do /admingive [type] [amount] or /bond give [type] [amount] [group]")
                return None
              bonds = accounts[author.id].bonds.copy()
              bond_type = args[1]
              if len(message.mentions) == 0:
                s = " "
                name = s.join(args[3:len(args)])
                svid = svapi.get_group_svid_from_name(name)
                if svid == "Error":
                  await message.channel.send("Could not find group!")
                  return None
                if svid in accounts:
                  touser = accounts[svid]
                else:
                  accounts[svid] = classes.account()
                  accounts[svid].svid = svid
                  touser = accounts[svid]
              else:
                touser = accounts[message.mentions[0].id]
                name = message.mentions[0].name
              amount = int(args[2])
              #Bond Class Name: Int: Count of Bonds
              total = 0
              for i in range(0,amount):
                bond = bond_types[bond_type]
                b = bond.buy(accounts,touser.svid,False,touser)
              await message.channel.send(f"Gave {amount} bonds to {name}")
            if command == "nullaccount":
              del accounts[message.mentions[0].id]
              await message.channel.send("Nulled the account for "+str(message.mentions[0]))
            if command == "force_yield_update":
              for item in accounts:
                item = accounts[item]
                for b in item.bonds:
                  b = item.bonds[b]
                  b.update(True)
            if command == "test":
                await message.channel.send("Test")
        else:
          if command in employee_commands:
            await message.channel.send(f"You have to be a {os.getenv('rolenametouseadmincommands')} to use /{command}!")
            return None
        if command == "help":
          #someone make a help comand
          return None
        if command == "ping":
            await message.channel.send("Pong!")
        if command == "createaccount":
          accounts[author.id] = classes.account()
          await message.channel.send("Created Account")
        if command == "bond":
          subcommand = message.content.split(" ")[1]
          args = message.content.split(" ")
          if not author.id in accounts:
            await message.channel.send("Create a Account with /createaccount")
            return None
          if accounts[author.id].svid == "":
            accounts[author.id].svid = svapi.get_user_svid_from_discordid(author.id)
          if accounts[author.id].oauthkey == "":
            await send_dm(author,f"{os.getenv('baseurl')}/login")
            await message.channel.send("Please click the link i just send you")
            return None
          if subcommand == "test":
            await send_dm(author,f"{os.getenv('baseurl')}/login")
            await message.channel.send("Please click the link i just send you")
          if subcommand == "buy":
            if len(args) < 3:
              await message.channel.send("Should be /bond buy [bond type] [amount to buy]!")
              return None
            bondtype = args[2]
            if bondtype not in bond_types:
              types = ""
              for item in bond_types:
                types += f"{item}, "
              types = types[0:len(types)-2]
              types += "!"
              await message.channel.send(f"Bond Type must be {types}")
              return None
            amount = int(args[3])
            if amount < 1:
              await message.channel.send("Amount of bonds to buy must be 1 or above!")
              return None
            ii = 0
            for i in range(0,amount):
              print(f"Total Issued: {total_bond_worth_issued}")
              if total_bond_worth_issued >= bond__worth_limit:
                await message.channel.send(f"Reached Bond Issue Limit!")
                return None
              bond = bond_types[bondtype]
              total_bond_worth_issued += bond.base
              out,reason = bond.buy(accounts,accounts[author.id].svid,True,accounts[author.id])
              if not out:
                await message.channel.send(f"Could only buy {ii} bonds, {reason}")
                return None
              ii += 1
            await message.channel.send(f"Bought {amount} bonds at {round(bond.interest*100,2)}% yield per month for {int(bond.maturityday/30)} months!")
          
          if subcommand == "info":
            embed = discord.Embed(title="Bonds",description="", color=0x00ee00)
            worth = 0
            payment = 0
            maturity = 0
            if len(args) > 2:
              s = " "
              name = s.join(args[2:len(args)])
              svid = svapi.get_group_svid_from_name(name)
              if svid == "Error":
                await message.channel.send("Could not find group!")
                return None
              if svid in accounts:
                account = accounts[svid]
              else:
                await message.channel.send("Group does not have a Account!")
                return None
            else:
              account = accounts[author.id]
            for b in account.bonds:
              b = account.bonds[b]
              worth += b.base+(b.base*b.interest*(b.timetillmaturity()/30))
              payment += b.base*b.interest
              if b.timetillmaturity() <= 14:
                maturity += 1
            info = f"Total worth: ¢{round(worth,2)}"+"\n"
            info += f"Yield payments this week: ¢{round(payment/4,2)}"+"\n"
            info += f"Bonds that will reach maturity in the next 14 days: {maturity}"+"\n"
            embed.add_field(name=f"bond info", value=info, inline=False)
            await message.channel.send(embed=embed)
          if subcommand == "types":
            embed = discord.Embed(title="Bonds Types",description="", color=0x00ee00)
            for item in bond_types:
              item = bond_types[item]
              info = f"Principal: {item.base}"+"\n"
              info += f"Maturity: {int(item.maturityday/30)} months"+"\n"
              info += f"Yield Per Month: {round(item.interest*100,1)}%"+"\n"
              info += f"Bonds bought/ Limit: {item.issued}/{item.limit}"+"\n"
              embed.add_field(name=f"{item.bond_class}", value=info, inline=False)
            await message.channel.send(embed=embed)

          if subcommand == "give":
            if len(args) < 5:
               await message.channel.send("Please do /bond give [type] [amount] @user or /bond give [type] [amount] [group]")
               return None
            bonds = accounts[author.id].bonds.copy()
            bond_type = args[2]
            if len(message.mentions) == 0:
              s = " "
              name = s.join(args[4:len(args)])
              svid = svapi.get_group_svid_from_name(name)
              if svid == "Error":
                await message.channel.send("Could not find group!")
                return None
              if svid in accounts:
                touser = accounts[svid]
              else:
                accounts[svid] = classes.account()
                accounts[svid].svid = svid
                touser = accounts[svid]
            else:
              touser = accounts[message.mentions[0].id]
              name = message.mentions[0].name
            amount = int(args[3])
            #Bond Class Name: Int: Count of Bonds
            types = {}
            for item in bonds:
              item = bonds[item]
              if item.bond_class in types:
                types[item.bond_class] += 1
              else:
                types[item.bond_class] = 1
            if not bond_type in types:
              await message.channel.send(f"You do not own enough bonds to give {amount} bonds to {name}!")
              return None
            if types[bond_type] >= amount:
              total = 0
              for item in bonds:
                bondid = item
                b = bonds[item]
                if b.bond_class == bond_type:
                  touser.bonds[bondid] = b
                  del accounts[author.id].bonds[bondid]
                  total += 1
                  if total >= amount:
                    break
            else:
              await message.channel.send(f"You do not own enough bonds to give {amount} bonds to {name}!")
              return None
            await message.channel.send(f"Gave {amount} bonds to {name}")
          if subcommand == "list":
            embed = discord.Embed(title=f"List of Bonds you own",description="", color=0x00ee00)
            if len(args) < 3:
              page = 0
            else:
              page = int(args[2])
            i = 0
            for b in accounts[author.id].bonds:
              if i >= 10+(page*10):
                break
              if i >= (page*10):
                b = accounts[author.id].bonds[b]
                info = f"Principal: {b.base}"+", "
                info += f"Maturity: {int(b.maturityday/30)} months"+", "
                info += f"Yield Per Month: {round(b.interest*100,1)}%"
                embed.add_field(name=f"{b.id}", value=info, inline=False)
              i += 1
            await message.channel.send(embed=embed)
        if command == "account":
            discordid = author.id
            if discordid in accounts:
                await message.channel.send("Account Found!")
            else:
                await message.channel.send("Create a Account with /createaccount")
from flask import Flask, redirect, request, session
from threading import Thread

app = Flask('')
@app.route('/')
def main():
    return "<center><h1>You may close this page!</h1></center>"

OAUTH2_CLIENT_ID = os.getenv("OAUTH2_CLIENT_ID")
OAUTH2_CLIENT_SECRET = os.getenv("OAUTH2_CLIENT_SECRET")
OAUTH2_REDIRECT_URI = os.getenv("baseurl")+"/callback"

API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.getenv("secret_key")

login_oauth = f"https://spookvooper.com/oauth2/authorize?response_type=code&client_id={OAUTH2_CLIENT_ID}&redirect_uri={OAUTH2_REDIRECT_URI}&scope=view,eco"

@app.route("/login/")
def login():
    return redirect(login_oauth)
@app.route('/callback')
def callback():
    code = request.args.get("code")
    link_1 = f"https://spookvooper.com/oauth2/RequestToken?grant_type=authorization_code&code={code}&redirect_uri={OAUTH2_REDIRECT_URI}&client_id={OAUTH2_CLIENT_ID}&client_secret={OAUTH2_CLIENT_SECRET}"
    print(link_1)
    request_1 = requests.get(link_1).text
    request_data = json.loads(request_1)
    session["access_token"] = request_data["access_token"]
    session["expires_in"] = request_data["expires_in"]
    session["svid"] = request_data["svid"]
    
    svid = session["svid"]
    user_link = f"https://api.spookvooper.com/User/GetUser?svid={svid}"
    user_request = requests.get(user_link).text
    user_load = json.loads(user_request)
    session["discord id"] = int(user_load["discord_id"])
    session['logged in'] = True
    if not session['discord id'] in accounts:
      accounts[session["discord id"]] = classes.account()
      accounts[session["discord id"]].svid = svid
      accounts[session["discord id"]].discord_id = session["discord id"]
    accounts[session["discord id"]].oauthkey = session["access_token"]
    cipher_suite = Fernet(os.getenv("encrypt_key").encode())
    accounts[session["discord id"]].oauthkey = cipher_suite.encrypt(accounts[session["discord id"]].oauthkey.encode()).decode()
    return redirect('/')
import functions
def run():
    app.run(host="0.0.0.0", port=8080)
def updatebonds(accounts):
  global total_bond_worth_issued
  save_load.save(accounts)
  try:
    for item in accounts:
      item = accounts[item]
      total = 0
      todelete = []
      for bond in item.bonds:
        i = bond
        bond = item.bonds[bond]
        a,didpayout = bond.update()
        total += a
        if didpayout:
          todelete.append(i)
      for i in item.bonds.copy():
        if i in todelete:
          print(f"deleted bond {i} from account {item.svid}")
          del item.bonds[i]
      if not total == 0:
        svapi.sendtransaction(total,os.getenv("Issuer-SVID"),item.svid)
  except:
    pass
functions.RepeatedTimer(5,updatebonds,accounts)
server = Thread(target=run)
server.start()
client.run(TOKEN)
