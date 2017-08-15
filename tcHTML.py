# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:30:35 2017

@author: bmburk
"""

import os
import time
import json
import webbrowser
#import csv
import urllib.request
import numpy as np
#from tkinter import *
#from tkinter import filedialog

#root = Tk()
#folder2 = filedialog.askdirectory() + "/"
#root.destroy()

#for k,d in playerDict.items():
#    print(k, d)
    
folder = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
folder2 = "E:/Projects/teamChecker/"
currFile = folder + "server_log.txt"
stratzAPI = "https://apibeta.stratz.com/api/v1/"
playerID = "84195549"

colorsDota = ["Blue", "Teal", "Purple", "Yellow", "Orange",
              "Pink", "Grey", "Light Blue", "Green", "Brown"]
lanes = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
activity = ["None", "Very Low", "Low", "Medium", "High", "Very High", "Intense"]
rowOrder = ['playerName', 'recentWinPct', 'recentMMRAvg', 'partyMMR', 'soloMMR', 'matches', 'supports', 'cores', 'uniqueHeroes', 'heroes', 'lanesL']

colorDict = {"Blue" : "2E6AE6",
   "Teal" : "5DE6AD",
   "Purple" : "AD00AD",
   "Yellow" : "DCD90A",
   "Orange" : "E66200",
   "Pink" : "E67AB0",
   "Grey" : "92A440",
   "Light Blue" : "5CC5E0",
   "Green" : "00771F",
   "Brown" : "956000"
}
colNamesDict = {'playerName': "Player Name",
        'supports' : "Support",
        'cores' : "Core",
        'recentMMRAvg' : "Recent MMR",
        'heroes' : "Heroes",
        'lanesL' : "Lanes",
        'uniqueHeroes' : "Unique Heroes",
        'recentWinPct' : "Recent Win %",
        'partyMMR' : "Party MMR",
        'soloMMR' : "Solo MMR",
        'matches' : "Total Matches"
}

css = """<style type="text/css">
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
"""

def loadHeroes():
    print('Loading heroes')
    heroDict = {}
    heroLoad = json.loads(urllib.request.urlopen(stratzAPI +
                                          "hero").read().decode('utf-8'))
    for i in heroLoad:
        heroDict[i] = heroLoad[i]['displayName']
    return heroDict
    
def idNewGame():
    with open(currFile) as myfile:
        currLine = -1
        searchingGame = True
        temp = list(myfile)
        while searchingGame:
            if "DOTA_GAMEMODE" in temp[currLine]:
                return temp[currLine]
            else:
                currLine -= 1

def pullData(playerID):
    playerWeb = stratzAPI + "player/"
    behavior = json.loads(urllib.request.urlopen(playerWeb +
                                                 playerID +
                                                 "/behaviorChart").read().decode('utf-8'))
    player = json.loads(urllib.request.urlopen(playerWeb +
                                               playerID).read().decode('utf-8'))
    playerDict = {'playerName': player['name'],
        'supports' : 0,
        'cores' : 0,
        'recentMMRAvg' : 0,
        'heroes' : [],
        'lanesL' : [0, 0, 0, 0, 0],
        'uniqueHeroes' : 0,
        'recentWinPct' : 0,
        'partyMMR' : 0,
        'soloMMR' : 0,
        'matches' : 0
            }
    try:
        playerDict['supports'] = int(round((behavior['supportCount']/(behavior['supportCount'] +
                                                        behavior['coreCount'])) * 100, 0))
        playerDict['cores'] = 100 - playerDict['supports']
        playerDict['recentMMRAvg'] = int(round(np.mean([k['rank'] for k in behavior['matches']]), 0))
        playerDict['lanesL'] = [0, 0, 0, 0, 0]
        playerDict['recentWinPct'] = int(round(100 * behavior['winCount']/behavior['matchCount'], 0))
        heroes = behavior['heroes']
        playerDict['uniqueHeroes'] = len(heroes)
        for hero in range(len(heroes)):
            currHero = heroes[hero]
            if currHero['matchCount'] > 2:
                heroName = heroDict[str(currHero['heroId'])]
                heroMatches = currHero['matchCount']
                heroWinPct = int(round((currHero['winCount']/heroMatches) * 100))
                playerDict['heroes'].append([heroName, heroMatches, heroWinPct])
            currLane = currHero['lanes']
            for l in currLane:
                playerDict['lanesL'][l['lane']] += l['matchCount']
    except:
        print("no behavior data")
    try:
        playerDict['partyMMR'] = player['mmrDetail']['partyValue']
        playerDict['soloMMR'] = player['mmrDetail']['soloValue']
    #    avatar = player['avatar']
    except:
        print("no player data")
    try:
        playerDict['matches'] = json.loads(urllib.request.urlopen(stratzAPI +
                                                    "match/?steamId=" +
                                                    playerID).read().decode('utf-8'))['total']
    except:
        print("no matches data")
    return(playerDict)

def outHeroesLanes(playerDict):
    out = ""
    for row in rowOrder:
        if row == "heroes":
            heroL = "<td>"
            for hero in playerDict['heroes']:
                heroL += hero[0]
                heroL += "<br>Matches: " + str(hero[1]) + " Win rate: " + str(hero[2]) + "%" + "<br>"
            out += heroL + "</td>"
        elif row == "lanesL":
            laneL = "<td>"
            for lane in range(5):
                laneL += lanes[lane] + ": " + str(int(round((playerDict['lanesL'][lane]/25)* 100))) + "%<br>"
            out += laneL + "</td>"
        else:
            currStr = str(playerDict[row])
            if row == 'recentWinPct' or row == 'supports' or row == 'cores':
                currStr += "%"
            out += "<td>%s</td>" % currStr
    return out

def genHTML(output):
    Html_file = open(folder2 + "teamChecker.html", "w", encoding = "utf-8")
    Html_file.write(output)
    Html_file.close()
    webbrowser.open(folder2 + "teamChecker.html")

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
            output = css
            output += "<html><body>"
            factions = ['RADIANT', 'DIRE']
            #hack, fix
            output += "<table>"
            for i in range(10):
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                if i == 0 or i == 5:
                    output += "</table><br><h1>%s</h1><table class=\"zui-table zui-table-zebra zui-table-horizontal\">" % factions[i == 5]
                    output += "<tr>"
                    for currCol in rowOrder:
                        output += "<td>%s</td>" % str(colNamesDict[currCol]) 
                    output += "</tr>"
                output += "<tr>%s</tr>" % outHeroesLanes(outData)
            output += "</table>"
            output += "</body></html>"
            genHTML(output)
        
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

heroDict = loadHeroes()
trier()