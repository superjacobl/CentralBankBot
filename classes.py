import time,random,string,copy,api,svapi
from cryptography.fernet import Fernet
import os


class bond:
  def id_generator(self):
    text = ""
    chars=string.ascii_lowercase+string.digits
    text += ''.join(random.choice(chars) for _ in range(4))
    return text
  def copy(self):
    return copy.copy(self)
  def __init__(self,maturityday):
    self.base = 1000
    self.interest = 0.05
    self.holdersvid = ""
    self.timeissued = 0
    self.maturityday = maturityday
    self.maturited = False
    self.lastupdated = 0
    self.id = self.id_generator()
    self.bond_class = ""
    self.limit = 0
    self.issued = 0
    self.paid_out = 0
  def buy(self,accounts,holdersvid,takefromaccount=False,user=None):
    self.holdersvid = holdersvid
    self.timeissued = time.time()
    self.lastupdated = time.time()
    self.id = self.id_generator()
    if takefromaccount:
        if self.issued >= self.limit:
          return [False,"due to no more bonds of this type issued!"]
        reponse = svapi.sendtransaction_ouath(self.base,self.holdersvid,os.getenv("Issuer-SVID"),f"Bought%20bond",user.oauthkey)
        print(reponse)
        if reponse["succeeded"]:
          user.bonds[self.id] = self.copy()
          self.issued += 1
          return [True,""]
    return [False,"due to insufficient funds!"]
  def getnextyieldpayment(self):
    day = 60*60*24
    week = day*7
    value = self.lastupdated+(day*7)-time.time()
    value /= 60*60*24
    return round(value,1)
  def timetillmaturity(self):
    day = 60*60*24
    week = day*7
    value = self.timeissued+(day*self.maturityday)-time.time()
    value /= 60*60*24
    return round(value,1)
  def update(self,force=False):
    day = 60*60*24
    week = day*7
    hour = 60*60
    amountpaid = 0
    if self.timeissued+(day*self.maturityday) <= time.time():
      svapi.sendtransaction(self.base,os.getenv("Issuer-SVID"),self.holdersvid)
      self.maturited = True
      self.issued -= 1
      return self.base
    if self.lastupdated+(hour) <= time.time() or force:
        amountpaid += self.base*(self.interest/30/24)
        self.lastupdated = time.time()
        self.paid_out += self.base*(self.interest/30/24)
    return amountpaid
class account:
    def __init__(self):
        self.loans = []
        self.last_updated = 0
        self.svid = ""
        self.last_loan_update = 0
        self.discord_id = 0
        self.oauthkey = ""
        #bond-id: bond object
        self.bonds = {}
    def update(self,force=False,force_loans=False):
      now = time.time()
      day = 60*60*24
      if len(self.loans) == 1:
        if now-self.last_loan_update >= day:
          self.loans[0].days_left -= 1
          self.last_loan_update = now
          if self.loans[0].days_left <= 2:
            server = client.get_guild(698755932838166558)
            print("hio")
            mem = server.get_member(self.discord_id)
            print(mem)
            self.status = ["send dm","You have "+str(self.loans[0].days_left)+" days left to pay back your loan! If you don't, you have have to pay a late fee of ¢"+str(round(self.loans[0].base_amount*self.loans[0].interest*0.05,2))+" per day"]
          if self.loans[0].days_left <= 0 or force_loans:
            self.loans[0].paid_back *= 0.9
    def get_total_loaned(self):
        total = 0
        for item in self.loans:
            total += item.base_amount*item.interest
        return total
    def if_can_get_loan(self,loan):
        total = loan.base_amount*loan.interest
        if self.get_total_loaned()+total <= self.credit_limit:
            return True
        else:
            return False
    def take_out_loan(self,loan):
        if self.if_can_get_loan(loan):
            t = loan.base_amount*loan.interest
            i = loan.interest
            i -= 1
            i *= 100
            i = round(i,2)
            i = str(i)
            to = round(loan.base_amount*loan.interest,2)
            if loan.base_amount*loan.interest >= 10000:
              return "Took out loan for ¢"+str(loan.base_amount)+" with "+i+"%, your total amount to pay back is ¢"+str(to)+", waiting on POT bank's Approval!"
            else:
              return "Took out loan for ¢"+str(loan.base_amount)+" with "+i+"% interest, your total amount to pay back is ¢"+str(to)
        else:
            return "You can not take out this loan, because your credit limit is too low."