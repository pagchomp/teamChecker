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
import webbrowser
import sys

folder = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
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

  

def outputData(d, output):
    heroL = ""
    for hero in d[8]:
           heroL += hero[0]
           heroL += "<br>Matches: " + str(hero[1]) + " Win rate: " + str(hero[2]) + "%" + "<br>"
    laneL = ""
    for lane in range(5):
        if d[9][lane] >=5:
           laneL += lanes[lane] + ": " + str(int(round((d[9][lane]/25)* 100))) + "%<br>"
    output += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (d[0],  str(d[1]), str(d[2]),  str(d[3]), str(d[4]), str(d[5]) + "%", str(d[6]) + "%", str(d[7]), heroL, laneL)
    return(output) 

class Checker(object):
    def __init__(self):
        self._cached_stamp = 0
        self.filename = currFile

    def check(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            print('file changed!')
            currGame = idNewGame()
            currGame = currGame[currGame.find("(")+1:currGame.find(")")].split()
            print('checking...')
            del currGame[:3]
            output = """<style type="text/css">
.zui-table-zebra tbody tr:nth-child(odd) {
    background-color: #fff;
}
.zui-table-zebra tbody tr:nth-child(even) {
    background-color: #EEF7EE;
}
.zui-table {
    border: solid 1px #DDEEEE;
    border-collapse: collapse;
    border-spacing: 0;
    font: normal 13px Arial, sans-serif;
}
.zui-table thead th {
    background-color: #DDEFEF;
    border: solid 1px #DDEEEE;
    color: #336B6B;
    padding: 10px;
    text-align: left;
    text-shadow: 1px 1px 1px #fff;
}
.zui-table tbody td {
    border: solid 1px #DDEEEE;
    color: #333;
    padding: 10px;
    text-shadow: 1px 1px 1px #fff;
}
.zui-table-zebra tbody tr:nth-child(odd) {
    background-color: #fff;
}
.zui-table-zebra tbody tr:nth-child(even) {
    background-color: #EEF7EE;
}
.zui-table-horizontal tbody td {
    border-left: none;
    border-right: none;
}
</style>
<html><body><h1>RADIANT</h1><table class="zui-table zui-table-zebra zui-table-horizontal">"""
            output += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % ("Name", "Total Matches", "Solo MMR", "Recent Games MMR", "Party MMR", "Support %", "Core %", "Unique Heroes", "Heroes >3", "Lanes")
            for i in range(5):
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                output = outputData(outData, output)
            output += "</table><br><h1>DIRE</h1><table class=\"zui-table zui-table-zebra zui-table-horizontal\">"
            output += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % ("Name", "Total Matches", "Solo MMR", "Recent Games MMR", "Party MMR", "Support %", "Core %", "Unique Heroes", "Heroes >3", "Lanes")
            for i in range(5,10):
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                output = outputData(outData, output)
            output += "</table></body></html>"
            print(output)
            Html_file = open(folder2 + "teamChecker.html","w", encoding = "utf-8")
            Html_file.write(output)
            Html_file.close()
            webbrowser.open(folder2 + "teamChecker.html")
        
def trier():
   pub = Checker()
   while True: 
       try: 
           time.sleep(5)
           pub.check()
       except:
           print('failed')
           time.sleep(5)
           trier()
            
heroDict = {}
with open(folder2 + "heroNum.csv") as csvfile:
     spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
     # Skip header
     next(spamreader)
     for row in spamreader:
         heroDict[row[0]] = row[1]

trier()