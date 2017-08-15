# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:30:35 2017

@author: bmburk
"""

import os
import time
import json
import urllib.request
import numpy as np
import pandas as pd
import csv

folder = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
#folder = "C:/Users/bmburk/Dropbox/Team Checker/"
folder2 = "E:/Projects/teamChecker/"
currFile = folder + "server_log.txt"

colorsDota = ["Blue", "Teal", "Purple", "Yellow", "Orange", "Pink", "Grey", "Light Blue", "Green", "Brown"]
lanes = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
activity = ["None", "Very Low", "Low", "Medium", "High", "Very High", "Intense"]

def idNewGame():
    with open(currFile) as myfile:
        currLine = -1
        searchingGame = True
        temp = list(myfile)
        while searchingGame:
            if "DOTA_GAMEMODE" in temp[currLine]:
                return(temp[currLine])
            else:
                currLine -= 1
            
def pullData(playerID):
    behavior = json.loads(urllib.request.urlopen("https://apibeta.stratz.com/api/v1/player/" + playerID + "/behaviorChart").read().decode('utf-8'))
    player = json.loads(urllib.request.urlopen("https://apibeta.stratz.com/api/v1/Player/" + playerID).read().decode('utf-8'))
    playerName = player['name']
    try:
        supports = int(round((behavior['supportCount']/(behavior['supportCount'] + behavior['coreCount'])) * 100, 0))
        cores =  100 -  supports
        recentMMRAvg = int(round(np.mean([k['rank'] for k in behavior['matches']]), 0))
        
        heroes = []
        lanesL = [0, 0, 0, 0, 0]
        heroRecent = behavior['heroes']
        for hero in range(len(heroRecent)):
            currHero = heroRecent[hero]
            if currHero['matchCount'] > 2:        
                heroName = heroDict[str(currHero['heroId'])]
                heroMatches = currHero['matchCount']
                heroWinPct = int(round((currHero['winCount']/heroMatches) * 100))
                heroes.append([heroName, heroMatches, heroWinPct])
            currLane = currHero['lanes']
            for l in currLane:
                lanesL[l['lane']] += l['matchCount']
        uniqueHeroes = len(heroRecent) 
        
    except:
        print("no behavior data")
        supports = 0
        cores = 0
        recentMMRAvg = 0
        heroes = []
        lanesL = [0, 0, 0, 0, 0]
        uniqueHeroes = 0
    
    try:
        partyMMR = player['mmrDetail']['partyValue']
        soloMMR = player['mmrDetail']['soloValue']
    #    avatar = player['avatar'] 
    except:
        print("no player data")
        partyMMR = 0
        soloMMR = 0
    
    try:
        matches = json.loads(urllib.request.urlopen("https://apibeta.stratz.com/api/v1/match/?steamId=" + playerID).read().decode('utf-8'))['total']
    except:
        print("no matches data")
        matches = 0
      
    return(playerName, matches, soloMMR, recentMMRAvg, partyMMR, supports, cores, uniqueHeroes, heroes, lanesL)

  

def outputData(d):
    print(d[0])
    print("")
    print("Total Matches: " + str(d[1]))
    print("Solo MMR: " + str(d[2]))
    print("Recent Games MMR: " + str(d[3]))
    print("Party MMR: " + str(d[4]))
    print("Support: " + str(d[5]) + "%")
    print("Core: " + str(d[6]) + "%")
    print("Unique Heroes in 25 Games: " + str(d[7]))
    print("*" * 10)
    for hero in d[8]:
        print(hero[0])
        print(" Matches: " + str(hero[1]) + " Win rate: " + str(hero[2]) + "%")
        print("*" * 10)
    for lane in range(5):
        print(lanes[lane] + ": " + str(d[9][lane]))
    print("-" * 30)
   # Lanes
   # Activity
#   format=xml
    
    
# playerID = '84195549' - me
# 82293085 - stratz Ken

class Checker(object):
    def __init__(self):
        self._cached_stamp = 0
        self.filename = currFile

    def check(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            print('file changed!')
            time.sleep(10)
            currGame = idNewGame()
            currGame = currGame[currGame.find("(")+1:currGame.find(")")].split()
#            if pastG == currGame[1]:
#                print('same old game')
#                pass
#            else:
#                if len(pastG) != 13:
#                    print('not 10 heroes')
#                    pass
#                else:
            print('checking...')
            print('=' * 70)
            pastG = currGame[1]
            del currGame[:3]
            print("x" * 50)
            print("RADIANT")
            print("x" * 50)
            for i in range(5):
                print(colorsDota[i])
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                outputData(outData)
            print("x" * 50)
            print("DIRE")
            print("x" * 50)
            for i in range(5,10):
                print(colorsDota[i])
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                outputData(outData)
        

def trier():
   pub = Checker()
   while True: 
       try: 
           time.sleep(10)
           pub.check()
       except:
           print('failed')
           time.sleep(10)
           trier()
            
heroDict = {}
with open(folder2 + "heroNum.csv") as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     # Skip header
     next(spamreader)
     for row in spamreader:
         heroDict[row[0]] = row[1]

pastG = ""
trier()