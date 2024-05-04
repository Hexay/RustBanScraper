import requests
import json
from datetime import datetime, timezone
import time
import os
import sys

#-------------------------------------------------------------------------            
#Helper functions

class Utils(object):
    @staticmethod
    def days_difference(date_str):
        given_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
        current_date = datetime.utcnow().replace(tzinfo=timezone.utc)
        difference = (current_date - given_date).days
        return difference

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

class config(object):
    def __init__(self):
        self.data = self.exists()
        self.bearer = self.data["bearer"]
        self.serverID = self.data["serverID"]
        self.minAccountAge = self.data["minAccountAge"]
        self.totalServers = self.data["totalServers"]
        self.hours = self.data["hours"]
        self.firstJoinAge = self.data["firstJoinAge"]
        self.webhook_url = self.data["webhook_url"]
        self.serversPt = dict()
        for i in self.data["serversPt"]:
            self.serversPt[i] = 0

    def exists(self):
        if "config.json" in FileHandler.list_dir(os.getcwd()): # Lists files in current directory
            info = FileHandler.read_json("config.json")
            return info
        else:
            self.no_config()

    def no_config(self):
        print("Copy config file from github!");
        FileHandler.write_json("config.json", "")
        time.sleep(3)
        sys.exit()


#-------------------------------------------------------------------------   
#Classes         

class Api(object):
    def __init__(self):
        self.config = config()
        self.bearer = self.config.bearer
        self.webhook_url = self.config.webhook_url
        self.serverID = self.config.serverID
        self.headers = {
            'Authorization': f'Bearer {self.bearer}',
            'Content-Type': 'application/json',
        }

    @staticmethod
    def get_data(url, headers={}, params={}):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            server_data = response.json()
            return server_data
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def get_server_list(self):
        params = {
            'include': 'player',
        }
        return self.get_data(f"https://api.battlemetrics.com/servers/{self.serverID}", self.headers, params=params)

    def get_activity(self, bm_id):
        responses = []
        url = f"https://api.battlemetrics.com/activity?tagTypeMode=and&filter[types][blacklist]=event:query&filter[players]={bm_id}&include=organization,user&page[size]=1000&access_token={self.bearer}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            responses.extend(data['data'])
            while data['links']['next']:
                response = requests.get(data['links']['next'] + f"&access_token={self.bearer}")
                if response.status_code == 200:
                    data = response.json()
                    responses.extend(data['data'])
                else:
                    break
        return responses

    def get_info(self, responses, bmid):
        for response in responses:
            for activity in response['attributes']['activities']:
                if activity['messageType'] == "rustLog:playerDeath:PVP":
                    if activity['data']['killer_id'] == bmid:
                        kills += 1
                    elif activity['data']['player_id'] == bmid:
                        deaths += 1

    def get_player_info(self, player_id):
        headers = {
            'Authorization': f'Bearer {self.bearer}',
            'Content-Type': 'application/json',
        }
        params = {
            "include": "server",
            "fields[server]": "name"
        }
        return self.get_data("https://api.battlemetrics.com/players/"+player_id, headers=headers, params=params)

    def find_reason(self, player):
        reason = ""
        color = 16777215
        if player.totalServers < self.config.totalServers:
            reason = "Low Servers"
            color = 16711680
            print("Super low severs", player.id)
        elif player.AccountAge < self.config.minAccountAge:
            reason = "New Account"
            color = 16753920
            print("Low age", player.id)
        elif player.hours < self.config.hours:
            reason = "Low hours"
            color = 8388736
            print("Low hours", player.id)
        return reason, color

    def send_webhook(self, player):
        us5x = player.selectPt["12859681"]
        eu5x = player.selectPt["16772881"]
        us10x = player.selectPt["21763974"]
        reason, color = self.find_reason(player)
        if reason == "":
            return
        data = {
        "content": "",
        "embeds": [
            {
            "title": player.name,
            "url": f"https://www.battlemetrics.com/rcon/players/{player.id}",
            "description": f"Reason: {reason}", "color": color,
            "fields": [
                {
                "name": "Rust",
                "value": f"{round(player.hours,2)} Hours",
                "inline": "true"
                },
                {
                "name": "🇺🇸 US 5x",
                "value": f"{us5x} Hours",
                "inline": "true"
                },
                {
                "name": "🇺🇸 US 10x",
                "value": f"{us10x} Hours",
                "inline": "true"
                },
                {
                "name": "🇪🇺 EU 5x",
                "value": f"{eu5x} Hours",
                "inline": "true"
                },
                {
                "name": "Atlas PVP Statistics 48hr",
                "value": "Ratio: 0\nKills: 0\nDeaths: 0",
                "inline": "false"
                },
                {
                "name": "Total Servers",
                "value": f"{player.totalServers} Servers",
                "inline": "true"
                },
                {
                "name": "Account Age",
                "value": f"{player.AccountAge} Days",
                "inline": "true"
                },
                {
                "name": "Game Banned IP Alts",
                "value": f"No Access",
                "inline": "false"
                },
                {
                "name": "Server Banned IP Alts",
                "value": f"No Access",
                "inline": "true"
                },
                {
                "name": "Reports 48 hr",
                "value": f"No Access",
                "inline": "true"
                }
            ],
            "thumbnail": {
                "url": "https://cdn.discordapp.com/avatars/674023543071309844/60b662bc82cbe73ae235e09dcc08978d.webp?size=100"
            },
            "footer": {
                "text": "Atlas Profile Viewer • Today at 13:18"
            }
            }
        ],
        "username": "Atlas Rust",
        "avatar_url": "https://cdn.discordapp.com/avatars/674023543071309844/60b662bc82cbe73ae235e09dcc08978d.webp?size=100"
        }
        response = requests.post(self.webhook_url, json=data)
        if response.status_code == 204:
            print("Webhook sent successfully")
        else:
            print(f"Failed to send webhook: {response.status_code}")

    def get_eac_banned_alts_bulk(self, related_players):
        banned_alts = []
        for related_player in related_players:
            url = f"https://api.battlemetrics.com/players/{related_player[0]}?include=identifier&access_token={self.bearer}"
            response = requests.get(url)
            if response.status_code != 200:
                continue
            data = response.json()
            identifier = next((include for include in data["included"] if include["type"] == "identifier" and include["attributes"]["type"] == "steamID"), None)
            if identifier is None:
                continue
            metadata = identifier["attributes"]["metadata"]
            if metadata is None or "rustBans" not in metadata or metadata["rustBans"] is None or metadata["rustBans"].get("count", 0) == 0:
                continue
            banned_alts.append({
                "name": data["data"]["attributes"]["name"],
                "BMID": related_player[0],
                "relativeTime": self.get_relative_time(datetime.fromisoformat(metadata["rustBans"]["lastBan"])),
                "sharedIPs": related_player[1],
                "temp": not metadata["rustBans"]["banned"],
            })
        return banned_alts   

    def get_relative_time(self, timestamp):
        now = datetime.utcnow()
        diff = now - timestamp
        if diff.total_seconds() < 60:
            return f"just now"
        elif diff.total_seconds() < 3600:
            return f"{diff.seconds} seconds ago"
        elif diff.total_seconds() < 86400:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.days} days ago" 


class Player(object):
    def __init__(self, data, selectPt):
        self.id = data["id"]
        self.name = data["attributes"]["name"]
        self.AccountAge = Utils.days_difference(data["attributes"]["createdAt"])
        self.hours = 0
        self.serverHours = 0
        self.firstJoinAge = None
        self.playerData = None
        self.totalServers = 0
        self.selectPt = selectPt

    def get_hours(self, data):
        for i in data["included"]:
            if i["relationships"]["game"]["data"]["id"] != "rust":
                continue
            self.totalServers += 1
            self.hours += i["meta"]["timePlayed"] / 3600
            if i["id"] in self.selectPt:
                self.selectPt[i["id"]] = round(i["meta"]["timePlayed"] / 3600, 2)



#-------------------------------------------------------------------------   
#Main
if __name__ == "__main__":
    api = Api()
    explored = set()
    '''
    a = api.get_server_list()
    for i in a["included"]:
        explored.add(i["id"])
    '''
    while True:
        players = api.get_server_list()
        newExplored = set()
        for i in players["included"]:
            newExplored.add(i["id"])
            if i["id"] not in explored:
                explored.add(i["id"])
                thisPlayer = Player(i, api.config.serversPt.copy())
                thisData = api.get_player_info(i["id"])
                thisPlayer.get_hours(thisData)
                api.send_webhook(thisPlayer)
        explored = newExplored
        time.sleep(5)
        

