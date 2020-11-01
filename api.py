from urllib.request import Request, urlopen
import json
import os
import api
def get_html(link):
  try:
    print(link)
    fp = Request(link,headers={'User-Agent': 'Mozilla/5.0'})
    fp = urlopen(fp).read()
    mybytes = fp
    mystr = mybytes.decode("utf8")
    return mystr
  except Exception as e:
    print(e)
    return "Error"

def getbalance(svid):
  link = f"https://spookvooper.com/api/eco/GetBalance?svid={svid}"
  t = float(get_html(link))
  return t

def get_group_svid_from_name(name):
  svid = get_html("https://spookvooper.com/api/Group/GetSVIDFromName?name="+name.replace(" ","%20"))
  return svid

def get_user_svid_from_discordid(discordid):
  svid = get_html("https://spookvooper.com/api/User/GetSVIDFromDiscord?discordid="+str(discordid))
  return svid