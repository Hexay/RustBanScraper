import requests
import json
from datetime import datetime, timezone
import time
import os
import sys
import re
import discord.utils


class Api(object):
    def __init__(self, steamKey, discordKey):
        self.steamKey = steamKey
        self.discordKey = discordKey

    def fetch_messages(self, channel_id, guild_id, before, limit):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages?before={before}&limit={limit}"
        headers = {
            "authorization": self.discordKey,
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 429:
            retry_after = 70
            print(f"Rate limited. Retrying after {retry_after} seconds.")
            time.sleep(retry_after)
            return self.fetch_messages(channel_id, guild_id, before, limit)
        return response.json()

    def get_data(self, guild, channel, name, offset):
        print("GETTING DATA")
        url = "https://discord.com/api/v9/guilds/" + guild + "/messages/search"
        params = {
            "channel_id": channel,
            "content": name,
            "include_nsfw": "true",
            "offset": offset
        }
        headers = {
            "authorization": self.discordKey
        }
        return requests.get(url, headers=headers, params=params).json()

    def get_steam(self, steamID):
        url = f"http://api.steampowered.com/ISteamUser/GetPlayerBans/v1/?key={self.steamKey}&steamids={steamID}"
        return requests.get(url=url).json()


class Utils(object):
    @staticmethod
    def days_difference(date_str):
        given_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = (current_date - given_date).days
        return difference

    @staticmethod
    def time_difference(time_str):
        given_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        current_time = datetime.now(timezone.utc)
        time_diff = (current_time - given_time).total_seconds() / (3600 * 24)
        return time_diff

    @staticmethod
    def getSteamIDS(text):
        steam_id_pattern = re.compile(r'https://steamcommunity\.com/profiles/(\d+)')
        steam_ids = steam_id_pattern.findall(text)
        return steam_ids

    @staticmethod
    def get():
        current_time = datetime.utcnow()
        snowflake_id = discord.utils.time_snowflake(current_time)
        return snowflake_id

    @staticmethod
    def time_string_to_snowflake_id(time_str):
        time_obj = datetime.fromisoformat(time_str)
        snowflake_id = discord.utils.time_snowflake(time_obj)
        return snowflake_id


class FileHandler(object):
    @staticmethod
    def read_json(fileDir):
        with open(fileDir, 'r') as f:
            data = f.read()
        return json.loads(data)

    @staticmethod
    def write_json(fileDir, data):
        with open(fileDir, 'w') as f:
            f.write(json.dumps(data))

    @staticmethod
    def list_dir(dir):
        files = os.listdir(dir)
        return files

    @staticmethod
    def read_file(fileDir):
        with open(fileDir, 'r') as f:
            data = f.read()
        return data

    @staticmethod
    def write_file(fileDir, data):
        with open(fileDir, "w", encoding="utf-8") as f:
            f.write(data)

class explored(object):
    def __init__(self):
        self.data = self.exists()
        self.count = 0

    def exists(self):
        if "explored0.json" in FileHandler.list_dir(os.getcwd()):  # Lists files in current directory
            return FileHandler.read_json("explored0.json")
        else:
            self.no_config()

    def no_config(self):
        print("Explored json file has now been created!");
        FileHandler.write_json("explored0.json", json.dumps({}))
        time.sleep(3);
        sys.exit()

    def save(self):
        if self.count == 0:
            self.count += 1
        else:
            self.count = 0
        FileHandler.write_json(f"explored{self.count}.json", self.data)


class config(object):
    def __init__(self):
        self.data = self.exists()
        self.steamKey = self.data["steamKey"]
        self.discordKey = self.data["discordKey"]
        self.name = self.data["searchQuery"]
        self.guildID = self.data["guildID"]
        self.channelID = self.data["channelID"]

    def exists(self):
        if "configGB.json" in FileHandler.list_dir(os.getcwd()):  # Lists files in current directory
            return FileHandler.read_json("configGB.json")
        else:
            self.no_config()

    def no_config(self):
        print("Copy config file from github!");
        FileHandler.write_json("configGB.json", "")
        time.sleep(3);
        sys.exit()


def find_banned_accounts(data, exploredIDs, bannedInfo):
    bannedString = ""
    for i, v in bannedInfo.items():
        bannedString += f"{i} {v[0]} {v[1]}\n"
    FileHandler.write_file("output.txt", bannedString)
    for message in data:
        try:
            fields = message["embeds"][0]["fields"]
        except:
            continue
        print(fields)
        print(bannedInfo)

        for i in fields:
            currentField = i["value"]
            currentIDs = Utils.getSteamIDS(currentField)
            for id in currentIDs:
                if id not in exploredIDs:
                    info = api.get_steam(id)["players"][0]
                    exploredIDs[id] = 1
                    if info["NumberOfGameBans"] - info["NumberOfVACBans"] >= 1 and info["DaysSinceLastBan"] < Utils.time_difference(message["timestamp"]):
                        bannedInfo[id] = (info["DaysSinceLastBan"], info["NumberOfGameBans"])




def recentBans():
    before = Utils.get()
    while True:
        data = api.fetch_messages(config.channelID, config.guildID, before,100)
        if len(data) == 0:
            print(data)
            break

        t = data[-1]
        t = t["timestamp"]
        before = Utils.time_string_to_snowflake_id(t)
        find_banned_accounts(data, exploredIDs, bannedInfo)

    bannedString = ""
    for i, v in bannedInfo.items():
        bannedString += f"{i} {v[0]} {v[1]}\n"
    FileHandler.write_file("output.txt", bannedString)
    print(data)

def addSteamId():
    before = Utils.get()
    while True:
        data = api.fetch_messages(config.channelID, config.guildID, before, 100)
        if len(data) == 0:
            print(data)
            break

        t = data[-1]
        t = t["timestamp"]
        before = Utils.time_string_to_snowflake_id(t)
        for message in data:
            try:
                fields = message["embeds"][0]["fields"]
            except:
                continue
            for i in fields:
                currentField = i["value"]
                currentIDs = Utils.getSteamIDS(currentField)
                for id in currentIDs:
                    if not explored.data.get(id):
                        current = message["timestamp"]
                        explored.data[id] = {
                            "gamebanned": False,
                            "lastCheckedGb": 1272959521,
                            "bansAtlas": 0,
                            "lastBanAtlas":1272959521,
                            "lastSeen": current,
                        }
                    else:
                        if message["timestamp"] < explored.data[id]["lastSeen"]:
                            explored.data[id]["lastSeen"] = message["timestamp"]
        explored.save()

def checkSteamIds():
    for id, data in explored.data.items():
        info = api.get_steam(id)["players"][0]
        if info["NumberOfGameBans"] - info["NumberOfVACBans"] >= 1 and info["DaysSinceLastBan"] < Utils.time_difference(explored.data[id]["lastSeen"]):
            
            bannedInfo[id] = (info["DaysSinceLastBan"], info["NumberOfGameBans"])


config = config()
api = Api(config.steamKey, config.discordKey)
explored = explored()
time = time.time()
global exploredIDs
global bannedInfo
exploredIDs = dict()
bannedInfo = dict()

option = int(input("1. Recent Bans, 2. Add steam ids, 3: Check steam ids, 4: Add atlas bans, 5: Check explored length : "))
if option == 1:
    recentBans()
elif option == 2:
    addSteamId()
elif option == 3:
    checkSteamIds()
elif option == 4:
    pass
elif option == 5:
    print(len(explored.data))

