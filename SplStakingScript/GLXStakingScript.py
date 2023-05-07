
# code mostly from https://github.com/BitcoinJake09/GLX-AutoCompunder/blob/main/glx-compunder.py
# tweaked after reading his code above

import os
import json
import requests
#from requests_html import AsyncHTMLSession  this line throwing error, not found?
import asyncio
import datetime
from datetime import timedelta
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Custom_json
from SPLGenericHelperFunctions import *

'''
def timeNow(): #gets current time function
    #thank https://peakd.com/@zimos for time suggestion
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time
'''

def timeNow(minutesToAdd): #adds minutes to the time now and returns the string
    t = (datetime.datetime.now()+timedelta(minutes=minutesToAdd)).time()
    h = str(t.hour)
    m = str(t.minute)
    s = str(t.second)
    if len(h) == 1:
        h = "0"+h
    if len(m) == 1:
        m = "0"+m
    if len(s) == 1:
        s = "0"+s  
    return h+":"+m+":"+s

def getGLXPStakedBalance(): #staked GLX balance
    try:
        r = requests.get('https://validator.genesisleaguesports.com/players/'+hiveName+'/balances/GLXP')
        jsonData = json.loads(r.text)
        d=jsonData["balance"]
        return d
    except:
        print("ERROR occured getting GLXP staking balance.")
        return 0

def getGLXLiqduidBalance(): #get liquid balance/stakable
    try:
        r = requests.get('https://validator.genesisleaguesports.com/players/'+hiveName+'/balances/GLX')
        jsonData = json.loads(r.text)
        d=jsonData["balance"]
        return d
    except:
        print("ERROR occured getting GLX staking balance.")
        return 0

def loadAccounts(): # reads the keys.json file to load the account name and keys
    with open('keys.json') as user_file:
        jsonAccounts = json.load(user_file)
    return jsonAccounts

def loadSettings(): # reads the settings.json file to load the settings
    with open('settings.json') as user_file:
        settings = json.load(user_file)
    return settings

def refreshScreen():
    os.system('cls')
    print("Auto GLX Claim and Stake Active")
    print("Active HIVE account: " + hiveName)
    print("Setting: Claim All Rewards every " + str(claimTime / sleepTime) + " minutes.")
    print("Setting: Stake All liquid GLX every " + str(stakeTime / sleepTime) + " minutes.")
    print("Current time: " + timeNow(0))
    print(str(timeNow(0)) + ": CanStake: " + str(getGLXLiqduidBalance()))
    print(str(timeNow(0)) + ": totalBalance: " + str(getGLXPStakedBalance()))

async def claimNow():
    while True:
        global spsStakeCounter

        #print("In Claim")
        preClaimBalance = getGLXLiqduidBalance()
        #print("previous claim balance = " + str(preClaimBalance))

        ops = [] # collect  the operations and broadcast together

        if autoGLXClaimStakedRewards: # check setting in the config file
            #Claim GLX staking rewards Operation
            payload = {"token":"GLX","qty":0,"n":nString(),"memo":"auto GLX claim"} 
            new_json = { 
                  "required_auths": [],
                  "required_posting_auths": [hiveName],
                  "id": "gls-plat-stake_tokens",
                  "json": payload
                }
            ops.append(Custom_json(new_json))

        #Claim GLX Node Rewards
        if autoGLXClaimNodeRewards:
            # Claim GLX Node rewards Payload
            payload = {"token":"GLSNODE","qty":0,"n":nString(),"memo":"auto Node claim"} 
            new_json = { 
                  "required_auths": [],
                  "required_posting_auths": [hiveName],
                  "id": "gls-plat-stake_tokens",
                  "json": payload
                }
            ops.append(Custom_json(new_json))

        #Claim GLX Pack Rewards
        if autoGLXClaimPackRewards:
            payload = {"token":"GMLSPA","qty":0,"n":nString(),"memo":"auto PACK claim"} 
            new_json = { 
                  "required_auths": [],
                  "required_posting_auths": [hiveName],
                  "id": "gls-plat-stake_tokens",
                  "json": payload
                }
            ops.append(Custom_json(new_json))

        #Claim GLX SPS Staked Rewards
        if autoGLXClaimSPSStakedRewards:
            if spsStakeCounter >= spsStakeCounterMax:               
                spsStakeCounter = 0 #reset counter
                #TODO, need to test this - this payload dose NOT work currently
                payload = {"token":"GLX","qty":0,"n":nString(),"memo":"auto SPS Staked Rewards claim"} 
                new_json = { 
                      "required_auths": [],
                      "required_posting_auths": [hiveName],
                      "id": "gls-plat-stake_tokens",
                      "json": payload
                    }
                ops.append(Custom_json(new_json))
            else:
                spsStakeCounter = spsStakeCounter + 1

        # Now send the combined transaction
        tx = TransactionBuilder() #lets build a tx
        tx.appendOps(ops) #add ops to tx
        tx.appendWif(wif) #add key
        tx.sign() #sign
        tx.broadcast() #broadcast

        await asyncio.sleep(15) #sleep for 15 seconds to allow for claims to process
        claimedTotal = getGLXLiqduidBalance() - preClaimBalance
        #print("Claimed Total = " + str(claimedTotal))
        print(str(timeNow(0)) + "  CLAIMED GLX: " + "{:.3f}".format(claimedTotal) + "  Next Claim at approximately " + timeNow(claimTime/sleepTime))
        await asyncio.sleep(claimTime) #wait for next time

async def stakeNow():
    global staked24
    await asyncio.sleep(25) #sleep for 25 seconds at start to offset stakes 30 seconds after claims 
    while True:
        canStake = getGLXLiqduidBalance()
        staked24 = staked24 + canStake
        tx = TransactionBuilder()
        payload = {"token":"GLX","qty":canStake, "memo":"auto STAKE glx"}
        new_json = {
              "required_auths": [],
              "required_posting_auths": [hiveName],
              "id": "gls-plat-stake_tokens",
              "json": payload
            }
        tx.appendOps(Custom_json(new_json))
        tx.appendWif(wif)
        tx.sign()
        tx.broadcast()
        print(str(timeNow(0)) + " Stake function: " + str(canStake) + " STAKED!  New Total: " + str(getGLXPStakedBalance() + canStake) + " Next Stake at approximately " + timeNow(stakeTime/sleepTime))
        await asyncio.sleep(stakeTime)

async def update24():
    #probably don't need this.  not useful and will not be seen in most cases
    global time24, staked24, balance24
    while True: #every 24 hours this should spit out some numbers xD
        t24 = time24 + datetime.timedelta(hours = 24)
        if t24 < datetime.datetime.now():
            print(str(timeNow(0)) + " Update 24 function: " + str(str("{0:.3f}".format(staked24))) + " STAKED in 24 hours!! \n Balance increased from: " + str("{0:.3f}".format(balance24)) + " to: " +str("{0:.3f}".format(getGLXPbalance())) + " GLX!")
            balance24 = getGLXPStakedBalance()
            staked24 = 0
            time24 = datetime.datetime.now()
        await asyncio.sleep(sleepTime)

async def main():
    #main code
    global isRunning #make sure we only run once
    if isRunning is False:
        refreshScreen()
        print("Started") #shows we are about to start tasks:
        if (autoGLXClaimStakedRewards or autoGLXClaimNodeRewards or autoGLXClaimPackRewards or autoGLXClaimSPSStakedRewards):
            asyncio.create_task(claimNow()) #claim loop    
        else:
            print ("None of the claim booleans are set to True. will never broadcast any claim transactions.  Claim loop NOT started.  Check keys file.")
        asyncio.create_task(stakeNow()) #stake loop
        asyncio.create_task(update24()) #balance snap loop
        print("Working...") #done with main function since loops are running after :D
        isRunning = True
    await asyncio.sleep(100000 * 60) #really long sleep or main stops

sleepTime = 60*1 # 1 minute
jsonAccounts = loadAccounts()
settings = loadSettings()
hiveName = jsonAccounts['accMainName']
wif = jsonAccounts['accMainPostingKey']
#claimTime is how often you want script to claim, numbers from keys file in minutes
claimTime = sleepTime*int(settings['autoGLXClaimTime'])
#stakeTime is how often you want to stake, numbers from keys file in minutes
stakeTime = sleepTime*int(settings['autoGLXStakeTime'])
#spsStakeCounterTimer is to limit this action to once every 6 hours if the claim time is less than 6 hours.  This is only available 1x per day anyway.
spsStakeCounterMax = 0
if(claimTime/sleepTime > 360):
    spsStakeCounterMax = 1 # run this every time if claimTime is greater than 360 minutes (6 hours)
else:
    # if detault is set (claimTime/sleepTime is 15 minutes then want 
    spsStakeCounterMax = int(360/(claimTime/sleepTime)) # want an interval here for how many times to 'skip' this to get close to once every 6 hours.  this claim is only available once a day, reduce extra transactions broadcast
spsStakeCounter = spsStakeCounterMax # set to max initially to make the first pass through activate the loop in the Claim cycle

#bit flags for each claim type from keys file
autoGLXClaimStakedRewards = settings['autoGLXClaimStakedRewards']=='True'
autoGLXClaimPackRewards = settings['autoGLXClaimPackRewards']=='True'
autoGLXClaimNodeRewards = settings['autoGLXClaimNodeRewards']=='True'
autoGLXClaimSPSStakedRewards = settings['autoGLXClaimSPSStakedRewards']=='True'

isRunning = False #for main loop check
balance24 = getGLXPStakedBalance() #for 24 hour snapshot to show balance increase
time24 = datetime.datetime.now() #used for the balance snapshot
staked24 = 0 #used for balance snapshot

asyncio.run(main()) # start the loops









