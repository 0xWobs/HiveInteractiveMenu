
import sys
import json
import subprocess
from SPLGenericHelperFunctions import *

#start of method definition
def menu():
    options = input(f"""
    ***** Select an Option *****
    1. Claim/Stake GLX
    2. Check Account Balance
    3. Sweep DEC from alt-accounts to main account. Leave 100DEC in each alt-account.

    0. Exit
    
    Selection: 
    """)
    print(options)
    if options.lower() == "1":
        claimStakeGLX()
    elif options.lower() == "2":
        checkAccountBalances()
    elif options.lower() == "3":
        sweepDEC()
    elif options.lower() == "0":
        return #exit the program
    else:
        print("Invalid Option! Returning to main menu!")
    
    menu() #reset back to menu
        
def claimStakeGLX():
    subprocess.Popen([sys.executable, 'GLXStakingScript.py'], creationflags = subprocess.CREATE_NEW_CONSOLE)

def checkAccountBalances():
    printAccountBalances(accMainName)
    printAccountBalances(acc2Name)
    printAccountBalances(acc3Name)
    printAccountBalances(acc4Name)

def sweepDEC():
    sweepTokensToMain(accMainName,acc2Name,acc2ActiveKey,tknDEC, 100)
    sweepTokensToMain(accMainName,acc3Name,acc3ActiveKey,tknDEC, 100)
    sweepTokensToMain(accMainName,acc4Name,acc4ActiveKey,tknDEC, 100)

#tokenTransfer(accMainName,accMainActiveKey,acc3Name,tknDEC[0],10)
#h = Hive(keys=[jsonAccounts['accMainPostingKey'], jsonAccounts['accMainActiveKey']])
#a = Account(jsonAccounts['accMainName'], blockchain_instance=h)
#print(a.get_account_bandwidth())
#a.transfer('wobs', '0.001', 'HIVE', memo= 'memo, Test transaction 2')

def loadAccounts():
    with open('keys.json') as user_file:
        jsonAccounts = json.load(user_file)
    return jsonAccounts

#var definition
_exit = False
jsonAccounts = loadAccounts()
accMainName = jsonAccounts['accMainName']
accMainPostingKey = jsonAccounts['accMainPostingKey']
accMainActiveKey = jsonAccounts['accMainActiveKey']
acc2Name = jsonAccounts['acc2Name']
acc2PostingKey = jsonAccounts['acc2PostingKey']
acc2ActiveKey = jsonAccounts['acc2ActiveKey']
acc3Name = jsonAccounts['acc3Name']
acc3PostingKey = jsonAccounts['acc3PostingKey']
acc3ActiveKey = jsonAccounts['acc3ActiveKey']
acc4Name = jsonAccounts['acc4Name']
acc4PostingKey = jsonAccounts['acc4PostingKey']
acc4ActiveKey = jsonAccounts['acc4ActiveKey']

print(accMainName + ' account keys successfully loaded')
print(acc2Name + ' account keys successfully loaded')
print(acc3Name + ' account keys successfully loaded')
print(acc4Name + ' account keys successfully loaded')

#main code to run
while _exit == False:
    _exit = menu()
    print("\n\n")
