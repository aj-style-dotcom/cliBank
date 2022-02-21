import sqlite3, sys, json, os
from datetime import datetime
from colorama import init, Style, Fore, Back


# database connection with sqlite3
conn=sqlite3.connect("bank.db")
cur=conn.cursor()


# create new transection file
def createTrans(name, data=[]):
  file=open(f"trans/{name}.json", "w")

  json.dump(data, file)
  file.close()


# update transections
def updateTrans(prieor, type, amount, name):
  test=datetime.now()
  currTime=test.strftime("%B %d, %Y %H:%M:%S")
  trans={
    "prieor":prieor,
    "type":type,
    "amount":amount,
    "date":str(currTime)
  }

  file=open(f"trans/{name}.json", "r")
  ledger=json.loads(file.read())
  ledger.append(trans)
  file.close()
  createTrans(name, ledger)
  

# create new user
def create():
  name=input(Style.BRIGHT+Fore.CYAN+"name : ")
  email=input("email : ")
  balance=input("opening balance : ")
  
  cur.execute("insert into users values (?, ?, ?, ?);",(None, name, email, balance))
  createTrans(name)
  conn.commit()
  print(Style.BRIGHT+Fore.GREEN+"\n\tuser created")
  prompt()
  
  
# update user
def update():
  inp=input("Enter account no : ")
  data=cur.execute("select * from users where accountNo=?", (inp,))
  if data.fetchone() is None:
    print(Style.BRIGHT+Fore.RED+"\n\tuser does not exists")
    prompt()
  name=input(Style.BRIGHT+Fore.CYAN+"name : ")
  email=input(Style.BRIGHT+Fore.CYAN+"email : ")
  cur.execute("update users set name=?, email=? where accountNo=?", (name, email, inp,))
  conn.commit()
  print(Style.BRIGHT+Fore.GREEN+"\n\tuser updated")
  prompt()
  

# delete user
def delete():
  inp=input(Style.BRIGHT+Fore.BLUE+"Enter account no : ")
  conf=input(Style.BRIGHT+Fore.RED+"are u sure to remove user ? (y/N)")
  if conf=="y" or conf=="yes":
    data=cur.execute("select name from users where accountNo=?", (inp,)).fetchone()
    if data is None:
      print(Style.BRIGHT+Fore.RED+"\n\tuser does not exists")
      prompt()
        
    os.remove(f"trans/{data[0]}.json")
    cur.execute("delete from users where accountNo=?", (inp, ))
    conn.commit()
    print(Style.BRIGHT+Fore.RED+"\nuser removed")
    prompt()
  print(Style.BRIGHT+Fore.RED+"\noperation cancled")
  prompt()
  
  
#get all users
def fetchAll():
  cur.execute("select * from users")
  datas=cur.fetchall()
  print(Style.BRIGHT+Fore.GREEN+f"""
    displaying {str(len(datas))} users
    """)
  for data in datas:
    print(Style.BRIGHT+Fore.WHITE+f"""
  account no. : {data[0]}
  name : {data[1]}
  email : {data[2]}
  balance : {data[3]}
  """)
  prompt()
  
  
# get one user by account no.
def fetchOne():
  inp=input(Style.BRIGHT+Fore.BLUE+"Enter account no : ")
  cur.execute("select * from users where accountNo=?", (inp,))
  data=cur.fetchone()
  if data is None:
    print(Style.BRIGHT+Fore.RED+"\n\tuser does not exists")
    prompt()
  print(Style.BRIGHT+Fore.WHITE+f"""
  account no. : {data[0]}
  name : {data[1]}
  email : {data[2]}
  balance : {data[3]}
  """)
  prompt()
  

# get user balance
def getBalance():
  inp=input(Style.BRIGHT+Fore.BLUE+"Enter account no : ")
  data=cur.execute("select balance, name from users where accountNo=?", (inp,)).fetchone()
  
  if data is None:
    print(Style.BRIGHT+Fore.RED+"\nuser does not exists")
    prompt()
  print(Style.BRIGHT+Fore.WHITE+f"\n\tcurrent balance of {data[1]} is Rs. {data[0]}")
  prompt()
  

# deposit amount
def deposit():
  inp=input(Style.BRIGHT+Fore.BLUE+"Enter account no : ")
  data=cur.execute("select balance, name from users where accountNo=?", (inp,)).fetchone()
  if data is None:
    print(Style.BRIGHT+Fore.RED+"\nuser does not exists")
    prompt()
  amount=int(input(Style.BRIGHT+Fore.CYAN+"enter amount (integer only) : "))
  newBal=data[0]+amount
  cur.execute("update users set balance=? where accountNo=?",(newBal, inp, ))
  conn.commit()
  updateTrans("bank", "credit", amount, data[1])
  print(Style.BRIGHT+Fore.BLUE+"\n\tamount deposited")
  prompt()


# withdraw amount
def withdraw():
  inp=input(Style.BRIGHT+Fore.BLUE+"Enter account no : ")
  data=cur.execute("select balance, name from users where accountNo=?", (inp,)).fetchone()
  if data is None:
    print("\n\tuser does not exists")
    prompt()
  amount=int(input(Style.BRIGHT+Fore.CYAN+"enter amount (integer only) : "))
  balance=data[0]
  if amount>balance:
    print(Style.BRIGHT+Fore.RED+"\n\tnot enough amount")
    conf=input(Style.BRIGHT+Fore.CYAN+"edit amount ? (y/N)")
    if conf=="y" or conf=="yes":
      withdraw()
    print(Style.BRIGHT+Fore.RED+"\n\toperation cancled")
    prompt()
  else:
    newBal=balance-amount
    cur.execute("update users set balance=? where accountNo=?",(newBal, inp, ))
    conn.commit()
    updateTrans("bank", "debit", amount, data[1])
    print(Style.BRIGHT+Fore.GREEN+"\n\tamount withdrawed")
    prompt()

# transfer route
def transfer():
  inp1=int(input(Style.BRIGHT+Fore.BLUE+"Enter sender Account no : "))
  data1=cur.execute("select balance, name from users where accountNo=?", (inp1,)).fetchone()
  inp2=int(input(Style.BRIGHT+Fore.BLUE+"Enter recever Account no : "))
  data2=cur.execute("select balance, name from users where accountNo=?", (inp2,)).fetchone()
  if data1 is None or data2 is None:
    print(Style.BRIGHT+Fore.RED+"\nsomeone usere does not exists")
    prompt()
  amount=int(input(Style.BRIGHT+Fore.CYAN+"enter amount (integer only) : "))
  balance1=data1[0]
  balance2=data2[0]

  if amount>balance1:
    print(Style.BRIGHT+Fore.RED+"\n\tnot enough amount")
    prompt()
  else:
    newBal1=balance1-amount
    newBal2=balance2+amount
    cur.execute("update users set balance=? where accountNo=?",(newBal1, inp1, ))
    cur.execute("update users set balance=? where accountNo=?",(newBal2, inp2, ))
    conn.commit()
  
    updateTrans(data2[1], "debit", amount, data1[1])
    updateTrans(data1[1], "credit", amount, data2[1])
    print(Style.BRIGHT+Fore.GREEN+"\n\tamount transfered")
    prompt()


# get all transections
def transection():
  inp=int(input(Style.BRIGHT+Fore.BLUE+"Enter Account no : "))
  data=cur.execute("select name from users where accountNo=?", (inp,)).fetchone()
  if data is None:
    print(Style.BRIGHT+Fore.RED+"\n\tuser does not exists")
    prompt()
  file=open(f"trans/{data[0]}.json", "r")
  trans=json.loads(file.read())
  print(Style.BRIGHT+Fore.GREEN+f"""
  displaying {str(len(trans))} transections
  """)
  for tr in trans:
    print(Style.BRIGHT+Fore.WHITE+f"""
    prieor:{tr["prieor"]},
    type:{tr["type"]},
    amount:{tr["amount"]},
    date:{tr["date"]}
    """)
  prompt()

  
# main function 
def prompt():
  promptStr=Style.BRIGHT+Fore.YELLOW+"""
  0. fetch all
  1. fetch one
  2. create
  3. update
  4. delete
  5. check balance
  6. deposit
  7. withdraw
  8. transfer
  9. transections
  """
  inp = input(promptStr+Style.BRIGHT+Fore.CYAN+"\n select option (qq to exit) : ")
  if inp=="0":
    fetchAll()
  elif inp=="1":
    fetchOne()
  elif inp == "2" :
    create()
  elif inp=="3":
    update()
  elif inp=="4":
    delete()
  elif inp=="5":
    getBalance()
  elif inp=="6":
    deposit()
  elif inp=="7":
    withdraw()
  elif inp=="8":
    transfer()
  elif inp=="9":
    transection()
  elif inp=="qq":
    print("\n\tExiting.....")
    sys.exit()
  else:
    print("enter options from above")
    prompt()
    
    
if __name__=="__main__":
  print(Style.BRIGHT+Fore.GREEN+"""
  Hello, Welcome To Code Lancer Bank
  """)
  prompt()
  #cur.execute("create table users (accountNo INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, balance INTEGER)")
  
  #cur.execute("alter table users drop column ledgerId")
  #conn.commit()
  



#temp="CREATE TABLE `nssje` (`id` INTEGER PRIMARY KEY AUTOINCREMENT,`dhdh` INTEGER,`jxjd` INTEGER);"
