DATA_FILE_PATH = '/home/username/script/snahpscript/cron/cron_manifest.json'

from lib.Browser import Browser
import json
import time
import requests
from urllib.parse import urljoin
import datetime
import os

def log(status):
    logfilename = '/home/username/script/snahpscript/cron/log.txt'
    statinfo = os.stat(logfilename)
    if statinfo.st_size > 1000000:
        with open(logfilename, 'w') as f:
            pass
    with open(logfilename, 'a', encoding='utf-8') as f:
        now = datetime.datetime.now()
        datestrn = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        strn = '{} {}\n'.format(datestrn, status)
        f.write(strn)

class Cron(object):

    def __init__(self, data_file_path):
        self.data_file_path = data_file_path
        data = self.load_data(data_file_path)
        if not data:
            log('Invalid data or no data file specified.')
            raise Exception('Invalid data or no data file specified.')
        self.data     = data
        self.jobs     = data['jobs']
        self.username = data['credentials']['username']
        self.password = data['credentials']['password']
        self.host     = data['host']['url']
        self.browser  = Browser()

    def validate_data(self, data):
        if 'jobs' not in data:
            return False
        if 'credentials' not in data:
            return False
        return True

    def load_data(self, filepath):
        try:
            with open(filepath) as f:
                data = json.load(f)
                if self.validate_data(data):
                    return data
        except:
            return False
        return False

    def save_data(self):
        with open(self.data_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4)

    def is_ready(self, job):
        lt = float(job['last_performed'])
        duration = float(job['duration'])
        now = time.time()
        return now > (lt + duration)

    def perform(self, job):
        host = self.host
        br = self.browser
        if not br.isLoggedIn():
            resp = br.login(host, self.username, self.password);
        url = urljoin(host,  job['url'])
        resp = br.request(type='get', url=url)
        if resp.status_code == requests.codes.OK:
            job['last_performed'] = time.time()
            self.save_data()
            return True
        return False

    def execute(self):
        for job in self.jobs:
            b_ready = self.is_ready(job)
            if b_ready:
                b_perform = self.perform(job)
                if b_perform:
                    name = job['name']
                    log(name)


if __name__=='__main__':
    log('Start')
    cron = Cron(DATA_FILE_PATH)
    cron.execute()
