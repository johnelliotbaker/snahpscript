import os
import json


PATH_CONFIG = './config.json'


class SnahpConfig(object):

    def __init__(self):
        if os.path.isfile(PATH_CONFIG):
            self.pathConfig = PATH_CONFIG
        else:
            self.pathConfig = None
        self.data = None
        self.aExtension = []


    def loadConfig(self, cfgpath=None):
        if not cfgpath:
            if not self.pathConfig:
                raise Exception("Require valid snahp config file.")
            cfgpath = self.pathConfig
        with open(cfgpath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.procConfig()
        self.procExtension()

    def procConfig(self):
        path = self.data['path']
        self.pathTmp = path['tmp']
        self.pathBackupRoot = path['backup']
        self.pathPhpbb = path['phpbb']
        self.pathExt = path['ext']
        database = self.data['database']
        self.db = database

    def procExtension(self):
        aExt = self.data['extensions']
        for ext in aExt:
            self.aExtension.append(ext)
        

if __name__ == "__main__":
    sc = SnahpConfig()
    sc.loadConfig()

