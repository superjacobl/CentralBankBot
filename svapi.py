from urllib.request import Request, urlopen
import json
import os
import api
from cryptography.fernet import Fernet

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
def get_avatar(svid):
  html = get_html("https://spookvooper.com/Group/View?groupid="+svid)
  soup = BeautifulSoup(html)
  temp = soup.findAll("img",{"class": "govpfp"})[0]
  temp = str(temp)
  print(temp)
  temp = temp.replace('<img class="govpfp"',"")
  temp = temp.replace('style="max-width:90%; max-height:90%;"',"")
  temp = temp.replace('<img class="govpfp m-2"',"")
  temp = temp.replace('box-shadow: 0px 0px 0px 7px rgb(255, 255, 255);',"")
  temp = temp.replace(' src="',"")
  temp = temp.replace('"/>',"")
  temp = temp.replace('style="max-width:90%; max-height:90%;',"")
  temp = temp.replace('" />',"")
  print(temp)
  return temp
def get_group_svid_from_name(name):
  svid = get_html("https://spookvooper.com/api/Group/GetSVIDFromName?name="+name.replace(" ","%20"))
  return svid
def get_user_svid_from_discordid(discordid):
  svid = get_html("https://spookvooper.com/api/User/GetSVIDFromDiscord?discordid="+str(discordid))
  return svid
def get_user_info(svid):
  html = get_html("https://spookvooper.com/api/User/GetUser?svid="+svid)
  return json.loads(html)
def sendtransaction_ouath(amount,fromsvid,to,detail=None,key=None):
  if detail == None: 
    detail = f"Bond%20yield%20payment"
  auth = os.getenv("auth")
  sercet = os.getenv("OAUTH2_CLIENT_SECRET")
  cipher_suite = Fernet(os.getenv("encrypt_key").encode())
  print(key)
  key = cipher_suite.decrypt(key.encode()).decode("utf-8")
  url = f"https://spookvooper.com/api/eco/SendTransactionByIDs?from={fromsvid}&to={to}&amount={amount}&auth={key}|{sercet}&detail={detail}"
  try: 
    return json.loads(get_html(url))
  except:
    return {"succeeded": False}

import threading
def get_html_fast(link):
    print(link)
    fp = Request(link,headers={'User-Agent': 'Mozilla/5.0'})
    fp = urlopen(fp).read()

def sendtransaction(amount,fromsvid,to,detail=None):
  if detail == None: 
    detail = f"Bond%20payment"
  auth = os.getenv("auth")
  url = f"https://spookvooper.com/api/eco/SendTransactionByIDs?from={fromsvid}&to={to}&amount={amount}&auth={auth}&detail={detail}"
  threading.Thread(target=get_html_fast, args=(url,)).start()