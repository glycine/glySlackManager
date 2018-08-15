'''
Created on 2018/05/27

@author: glycine<haruhisa.ishida@gmail.com>
'''

import requests
from datetime import datetime
import yaml


class SlackClient:
    __access_point = "https://slack.com/api/"
    __access_token = None
    __channels = None
    __files = None
    __users = None

    def __init__(self, access_token):
        self.__access_token = access_token
    
    def channel_list(self):
        """ channelを返す．結果がない場合はslack APIを用いて取得する"""
        if self.__channels != None:
            return self.__channels
        
        # slack APIのアクセス
        url = self.__access_point + "channels.list"
        params = {'token': self.__access_token}
        r = requests.get(url, params=params)
        data = r.json()
        channels = []
        if data["ok"] == True:
            channels = data["channels"]
        
        # 結果の内部への格納
        self.__channels = {}
        for channel in channels:
            self.__channels[channel["id"]] = channel
        return self.__channels
    
    def files_list(self):
        """ fileを返す．結果がない場合はslack APIを用いて取得する """
        if self.__files != None:
            return self.__files
        
        # slack APIのアクセス
        url = self.__access_point + "files.list"
        params = {'token': self.__access_token}
        r = requests.get(url, params=params)
        data = r.json()
        files = []
        if data["ok"] == True:
            total_pages = data["paging"]["pages"]
            for page in range(1, total_pages + 1):
                files.extend(self.__files_list(page))
            files = sorted(files, key=lambda file: file["timestamp"])
        
        # 結果の内部への格納
        self.__files = {}
        for file in files:
            self.__files[file["id"]] = file
        
        return self.__files
    
    def users_list(self):
        if self.__users != None:
            return self.__users
        url = self.__access_point + "users.list"
        params = {'token': self.__access_token}
        r = requests.get(url, params = params)
        data = r.json()
        users = []
        if data["ok"] == True:
            users = data["members"]
        
        self.__users = {}
        for user in users:
            self.__users[user["id"]] = user
        
        return self.__users
         
    
    def __files_list(self, page):
        url = self.__access_point + "files.list"
        params = {'token': self.__access_token, 'page': page}
        r = requests.get(url, params=params)
        data = r.json()
        if data["ok"] == True:
            return data["files"]
        else:
            return []
    
    def show_files(self):
        files = self.files_list()
        for file in files.values():
            self.__show_file(file)
    
    def __show_file(self, file):
        channels = self.channel_list()
        created = datetime.fromtimestamp(file["created"])
        tstamp = datetime.fromtimestamp(file["timestamp"])
        channels = list(map(lambda x: channels[x]["name"], file["channels"]))
        user = self.users_list()[file["user"]]["name"]
        print(file["id"], ",", created, ",", tstamp, ",", file["name"], ",", file["title"], ",", file["mimetype"], ",", file["filetype"], ",", user, ",", file["size"], ",", file["is_external"], ",", channels,",",len(file["channels"]))
        return 


if __name__ == '__main__':
    f = open("conf.yaml", "r+")
    conf = yaml.load(f)
    size_threshold = int(conf['filesize_threshold'])
    print(size_threshold)
    
    client = SlackClient(conf['token'])
    client.show_files()

