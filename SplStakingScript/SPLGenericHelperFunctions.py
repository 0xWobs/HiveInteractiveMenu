import json
import requests
import random
import string
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Custom_json

# token tuples to give [0] token names, and [1] readable names
tknBloodStones = ("BLDSTONE", "Bloodstones") # Bloodstones, used with gladius cases to increase chances of legendary gladius cards
tknChaosPacks = ("CHAOS", "Chaos Packs") # Chaos Legion card packs
tknCredits = ("CREDITS", "Credits") # In game credits
tknDEC = ("DEC", "DEC") # Dark Energy Crystals
tnkDECB = ("DEC-B", "DEC Batteries") # DEC batteries, no longer available
tknDicePacks = ("DICE", "Dice Packs") # dice card packs
tknGladiusCases = ("GLADIUS", "Gladius Cases") # gladius cases card packs
tknGoldPotions = ("GOLD", "Gold Potions") #gold potions to get gold foil cards
tknGrain = ("GRAIN", "Grain") # the first land resource
tknAlchemyPotions = ("LEGENDARY", "Legendary Potions") #alchemy potions to help get legendary cards
tknLicense = ("LICENSE", "SPS Node Licenses") # SPL node licenses
tknMerits = ("MERITS", "Merits") # merits earned from brawls, gladius resources
tknNightmareTDPacks = ("NIGHTMARE", "Nightmare TD Packs") # packs for the Tower Defense expansion
tknPlots = ("PLOT", "Plot Tokens (non-specified)") # unclaimed/unsurveyed plots? not sure
tknPurchasedEnergy = ("PURCHASED_ENERGY", "Purchased Energy") #extra energy purchased via in game menus, limited to 50 per day
tknPowerStone = ("PWRSTONE", "Power Stones") # the guild powerstone upgrade to get better gold foil gladius cards
tknQuest = ("QUEST", "Quest Tokens") # no longer used?
tknRiftWatcherPacks = ("RIFT", "RiftWatcher Packs") # Riftwatchers packs
tknSPSLiquid = ("SPS", "SPS Liquid") # SPS in game account, liquid
tknSPSDAOPromoCardNumber = ("SPS_DAO_PROMO_CARD", "SPS DAO Promo Card Credits") # how many SPS promo cards will get, 1 per 1000 sps staked
tknSPSStaked = ("SPSP", "SPS Staked") # SPS staked in game
tknTimeCrytals = ("TC", "Time Crystals") # Time crystals for land expansion
tknUntamedPacks = ("UNTAMED", "Untamed Card Packs") #untamed card packs
tknVoucher = ("VOUCHER", "Voucher SPS-Chain")  # SPS Chain Vouchers
tknVoucherInGame = ("VOUCHER-G", "Voucher In-Game") # In Game Vouchers
tknVoucherTotal = ("VOUCHER-TOTAL", "Vouchers") # should be SPS chain vouchers + In Game vouchers
tknEnergy = ("ECR", "Battle Energy") # energy for battles

# return a single int value from the balance token; return -1 if not found
def getTokenAmount(accName, tokenName):
    try:
        r = requests.get('https://api.splinterlands.io/players/balances?username='+accName)
        jsonData = json.loads(r.text)
        for item in jsonData:
            if item["token"]==tokenName:
                return round(item["balance"],3)
        print("could not find token: " + tokenName + " from account: " + accName)
        return -1
    except Exception as e:
        print("ERROR occured getting account balance in GetTokenAmount.")
        print(e)
        return

# print important collection of acocunt balances
# important things currently defined as DEC, SPS and Voucher
def printAccountBalances(accName):
    tokenList = {tknDEC, tknSPSLiquid, tknSPSStaked, tknVoucherTotal}
    printAccountBalancesTokenList(accName,tokenList)

#token is token type tuple [0] dict name [1] readable name
def printAccountBalancesTokenList(accName, tokenList):
    try:
        r = requests.get('https://api.splinterlands.io/players/balances?username='+accName)
        jsonData = json.loads(r.text)

        output = ""
        for token in tokenList:
            for item in jsonData:
                if item["token"]==token[0]:
                    output = output + "Account " + accName + " has " + str(round(item["balance"],3)) + " " + token[1] + "\n"
                    break # end the loop
        print(output)
    except Exception as e:
        print("ERROR occured getting account balance.")
        print(e)
        return
    #code

# generic function to initiate a token transfer, should work for any token type
def tokenTransfer(accFrom, accFromActiveKey, accTo, tokenName, tokenQuantity):
    tx = TransactionBuilder()
    payload = {"to":accTo,"qty":round(tokenQuantity,3),"token":tokenName,"n":nString(),"app":"splinterlands/0.7.139"} #will this version need updating???
    new_json = {
            "required_auths": [accFrom],
            "required_posting_auths": [],
            "id": "sm_token_transfer",
            "json": payload
        }
    tx.appendOps(Custom_json(new_json))
    tx.appendWif(accFromActiveKey)
    tx.sign()
    tx.broadcast()

# generic function to initiate a token transfer, should work for any token type: ONLY TO HIVE-ENGINE!
# tokenName here is the string token name, not the token tuple
def tokenTransferToHiveEngineFromInGame(accFrom, accFromActiveKey, tokenName, tokenQuantity):
    tx = TransactionBuilder()
    payload = {"to":"sl-hive","qty":round(tokenQuantity,3),"token":tokenName,"memo":accFrom,"n":nString(),"app":"splinterlands/0.7.139"} #will this version need updating???
    new_json = {
            "required_auths": [accFrom],
            "required_posting_auths": [],
            "id": "sm_token_transfer",
            "json": payload
        }
    tx.appendOps(Custom_json(new_json))
    tx.appendWif(accFromActiveKey)
    tx.sign()
    tx.broadcast()

#generic function to initiate a token transfer from Hive Engine to In Game !
# tokenName here is the string token name, not the token tuple
def tokenTransferToInGameFromHiveEngine(accFrom, accFromActiveKey, tokenName, tokenQuantity):
    tx = TransactionBuilder()
    payload2 = {"symbol":tokenName,"to":"steemmonsters","quantity":str(round(tokenQuantity,3)),"memo":""}
    payload = {"contractName":"tokens","contractAction":"transfer","contractPayload":payload2} #will this version need updating???
    new_json = {
            "required_auths": [accFrom],
            "required_posting_auths": [],
            "id": "ssc-mainnet-hive",
            "json": payload
        }
    tx.appendOps(Custom_json(new_json))
    tx.appendWif(accFromActiveKey)
    tx.sign()
    tx.broadcast()

#send tokens (DEC, SPS, VOUCHER) to Hive Engine
#may work with other token types also, not sure
# min amount remaining is the floor amount to keep in the account
# Token is the TUPLE
def sendTokensToHiveEngine(accFrom, accFromActiveKey, tokenTuple, minAmountRemaining):
    accTokensTotal = getTokenAmount(accFrom, tokenTuple[0])
    accTokens = accTokensTotal - minAmountRemaining
    if accTokens > 0:
        tokenTransferToHiveEngineFromInGame(accFrom,accFromActiveKey,tokenTuple[0],accTokens) # THIS WORKS
        print("Initiated transfer of " + str(accTokens) + " " + tokenTuple[1] + " from account " + accFrom + " to Hive Engine.")
    else:
        print("No transfer initiated.  " + accFrom + " has " + str(accTokensTotal) + " " + tokenTuple[1] + " tokens which is at or below the minimum requested of " + str(minAmountRemaining) + ".")
        #print("No " + tokenTuple[1] + " found in account " + accFrom + ". No transfer initiated.")
 

#tokenName expecting the tuple, not just the string
#this function has output to utilize the tokentransfer function easier
def sweepTokensToMain(toAccount, fromAccount, fromAccountActiveKey, token, minAmountRemaining):
    accTokensTotal = getTokenAmount(fromAccount, token[0])
    accTokens = accTokensTotal - minAmountRemaining
    if accTokens > 0:
        tokenTransfer(fromAccount,fromAccountActiveKey,toAccount,token[0],accTokens) # THIS WORKS
        print("Initiated transfer of " + str(accTokens) + " " + token[1] + " from account " + fromAccount + " to account " + toAccount)
    else:
        print("No transfer initiated.  " + fromAccount + " has " + str(accTokensTotal) + " " + token[1] + " tokens which is at or below the minimum requested of " + str(minAmountRemaining) + ".")
        #print("No " + token[1] + " found in account " + fromAccount + ". No transfer initiated.")
        


# method to return the "n" string argument
def nString():
    r = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    return r
    #return str("\"" + r + "\"")