import json
from urllib.request import Request, urlopen
from classes import *
import requests,svapi,os,pickle
from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()
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
def save(accounts):
  pp = {}
  for item in accounts:
    prev = item
    item = accounts[item]
    t = {}
    t['svid'] = item.svid
    t['oauthkey'] = item.oauthkey
    bo = {}
    for b in item.bonds:
      bond_id = b
      b = item.bonds[b]
      tem = {}
      tem['base'] = b.base
      tem['interest'] = b.interest
      tem['holdersvid'] = b.holdersvid
      tem['timeissued'] = b.timeissued
      tem['maturityday'] = b.maturityday
      tem['maturited'] = b.maturited
      tem['lastupdated'] = b.lastupdated
      tem['id'] = b.id
      tem['bond_class'] = b.bond_class
      tem['issued'] = b.issued
      bo[bond_id] = tem
    t['bonds'] = bo
    pp[prev] = t
  file = open('accounts.txt', 'wb') 
  pickle.dump(pp, file)
  file.close()
def load():
  accounts = {}
  try:
    filehandler = open('accounts.txt', 'rb') 
    data = pickle.load(filehandler)
  except:
    return {}
  for item in data:
    prev = int(item)
    item = data[item]
    u = account()
    u.svid = item['svid']
    if "oauthkey" in item:
      u.oauthkey = item['oauthkey']
    for b in item['bonds']:
      b = item['bonds'][b]
      bo = bond(b['maturityday'])
      bo.base = b['base']
      bo.interest = b['interest']
      bo.holdersvid = b['holdersvid']
      bo.timeissued = b['timeissued']
      bo.maturityday = b['maturityday']
      bo.maturited = b['maturited']
      bo.lastupdated = b['lastupdated']
      if "bond_class" in b:
        bo.bond_class = b['bond_class']
      if "issued" in b:
        bo.issued = b['issued']
      bo.id = b['id']
      u.bonds[bo.id] = bo
    accounts[prev] = u
  print(accounts)
  return accounts