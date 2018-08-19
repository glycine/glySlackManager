'''
Created on 2018/05/27

@author: glycine<haruhisa.ishida@gmail.com>
'''

import requests
from datetime import datetime
from operator import itemgetter
import yaml


class SlackClient:
    __access_point = "https://slack.com/api/"

    def __init__(self, access_token):
        self.__access_token = access_token
        self.__channels = None
        self.__files = None
        self.__users = None
    
    def channel_list(self, force_update = False):
        """ channelを返す．結果がない場合はslack APIを用いて取得する"""
        if self.__channels != None and not force_update:
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
    
    def files_list(self, force_update = False):
        """ fileを返す．結果がない場合はslack APIを用いて取得する """
        if self.__files != None and not force_update:
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
    
    def get_remove_files(self, size_threshold):
        """ 削除候補のファイルリストを返す．size_thresholdはMiB"""
        threshold = size_threshold * 1024*1024
        total_size = self.__get_total_size()
        remove_files = {}
        if total_size < threshold:
            return remove_files
        files = self.files_list()
        timestamps = self.__get_timestamps()
        remove_size = total_size - threshold
        size = 0
        for timestamp in timestamps:
            file_id = timestamp[0]
            file = files[file_id]
            size += file["size"]
            remove_files[file_id] = file
            if size > remove_size:
                break
        return remove_files
    
    def remove_file(self, file_id):
        url = self.__access_point + "files.delete"
        params = {'token': self.__access_token, 
                  'file': file_id}
        return requests.post(url, params = params)
        
    
    def __get_timestamps(self):
        """ fileIDとtimeStampの2次元配列を，timeStampの昇順で返す"""
        files = self.files_list()
        timestamps = []
        for file in files.values():
            file_id = file["id"]
            timestamp = file["timestamp"]
            timestamps.append([file_id, timestamp])
        timestamps.sort(key=itemgetter(1), reverse=False)
        return timestamps
    
    def __get_total_size(self):
        """ 現在のファイルの総容量を返す """
        files = self.files_list()
        total_size = 0
        for file in files.values():
            total_size += file["size"]
        return total_size
    
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
    
    client = SlackClient(conf['token'])
    files = client.files_list()
    
    remove_files = client.get_remove_files(size_threshold)
    
    for file in remove_files.values():
        if not conf['is_demo']:
            client.remove_file(files["id"])
            print("removed: ", file["id"], datetime.fromtimestamp(file["timestamp"]), file["name"])
        else:
            print("remove-demo: ", file["id"], datetime.fromtimestamp(file["timestamp"]), file["name"])
        break
    
    
    

