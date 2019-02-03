import re
from collections import defaultdict
import datetime

#  RE_DATE = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}).(\d{6})Z\s*(\d+)\s.*?(\d+)\s(\w+)\s([\w\W]*)$')


class SqlList(object):
    def __init__(self, data):
        self.totalTime = 0
        self.data = []
        self.filter(data)
        self.convert2diff()
        self.hm = {}

    def print(self, n=10):
        for i in range(n):
            print(self.data[i])

    def __str__(self, n=10):
        n = len(self.data)
        for i in range(n-1):
            print(self.data[i])
        return str(self.data[-1])

    def append(self, val):
        self.arr.append(val)

    def print_total_time(self):
        print(self.strfdelta(self.totalTime, '{hours} hours {minutes} minutes {seconds}.{micro} seconds'))

    def convert2diff(self):
        data = self.data
        n = len(data)
        log = []
        for i in range(n-1):
            curr = data[i]
            next = data[i+1]
            diff = next.dt - curr.dt
            if 'Quit' in curr.command:
                diff = datetime.timedelta(0)
            curr.duration = diff
        if data:
            data.pop()
        self.data = [data for data in self.data if data.query_type == 'Query']

    def filter(self, data):
        log = []
        for line in data:
            if line[:4] == '2019':
                entry = SqlEntry(line)
                log.append(entry)
        self.data = log
        self.totalTime = self.data[-1].dt - self.data[0].dt

    def sort_by_time(self):
        self.data.sort(reverse=True)

    def aggregate(self):
        self.hm = defaultdict(dict)
        for entry in self.data:
            duration = entry.duration
            command = entry.command
            if command not in self.hm:
                self.hm[command]['count'] = 1
                self.hm[command]['duration'] = duration
            else:
                self.hm[command]['count'] += 1
                self.hm[command]['duration'] += duration

    def strfdelta(self, tdelta, fmt):
        d = {'days': tdelta.days}
        d['hours'], rem = divmod(tdelta.seconds, 3600)
        d['minutes'], d['seconds'] = divmod(rem, 60)
        d['micro'] = tdelta.microseconds
        return fmt.format(**d)

    def get_max_duration_snahp(self, n=10, bPrint=False):
        aQuery = self.hm
        res = []
        for command in aQuery:
            query = aQuery[command]
            durationStrn = self.strfdelta(query['duration'], '{seconds}.{micro}')
            duration = query['duration']
            if 'snahp' in command:
                res.append([duration.seconds+duration.microseconds/1000000, command])
        res.sort(key=lambda x:x[0], reverse=True)
        res = res[:n]
        if bPrint:
            print('====================================================')
            print('{0: <12} | {1:}'.format('  Duration  ', 'Query by Snahp Extension'))
            print('=============+======================================')
            for r in res:
                fstr = '{:.6f}'.format(r[0])
                fstr = fstr.rjust(10, ' ')
                print('{0: <12} | {1:}'.format(fstr, r[1]))
        return res


    def get_max_duration(self, n=10, bPrint=False):
        aQuery = self.hm
        res = []
        for command in aQuery:
            query = aQuery[command]
            durationStrn = self.strfdelta(query['duration'], '{seconds}.{micro}')
            duration = query['duration']
            res.append([duration.seconds+duration.microseconds/1000000, command])
        res.sort(key=lambda x:x[0], reverse=True)
        res = res[:n]
        if bPrint:
            print('====================================================')
            print('{0: <12} | {1:}'.format('  Duration  ', 'Query'))
            print('=============+======================================')
            for r in res:
                fstr = '{:.6f}'.format(r[0])
                fstr = fstr.rjust(10, ' ')
                print('{0: <12} | {1:}'.format(fstr, r[1]))
        return res

    def get_max_count(self, n=10, bPrint=False):
        aQuery = self.hm
        res = []
        for command in aQuery:
            query = aQuery[command]
            res.append([query['count'], command])
        res.sort(key=lambda x:x[0], reverse=True)
        res = res[:n]
        if bPrint:
            print('====================================================')
            print('{0: <12} | {1:}'.format('     Count  ', 'Query'))
            print('=============+======================================')
            for r in res:
                fstr = '{:6d}'.format(r[0])
                fstr = fstr.rjust(10, ' ')
                print('{0: <12} | {1:}'.format(fstr, r[1]))
        return res


class SqlEntry(object):
    def __init__(self, strn):
        self._strn = strn
        self.parse(strn)

    #  def __str__(self):
    #      dtstr = self.duration.strftime('%s')
    #      return '[{}, {}]'.format(dtstr, self.command)
    #
    #  def __repr__(self):
    #      return str(self)

    def __lt__(self, other):
        return self.dt < other.dt

    def parse(self, strn):
        RE_DATE = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}).(\d{6})Z\s*(\w+)\s*(\w+)\s*([\w\W]*)$')
        match      = RE_DATE.match(strn)
        yr         = int(match.group(1))
        mo         = int(match.group(2))
        day        = int(match.group(3))
        hour       = int(match.group(4))
        minute     = int(match.group(5))
        second     = int(match.group(6))
        micro      = int(match.group(7))
        pid        = int(match.group(8))
        query_type = match.group(9)
        query      = match.group(10)
        dt         = datetime.datetime(yr, mo, day, hour, minute, second, micro)
        command = query.strip()
        command = command.replace('\t', ' ')
        self.dt = dt
        self.command = command
        self.query_type = query_type


if __name__=='__main__':
    #  with open('/home/ubm/tmp/mail.log', 'r', encoding='utf-8') as f:
    #  with open('/var/lib/mysql/mail.log', 'r', encoding='utf-8') as f:
    with open('snahp.log', 'r', encoding='utf-8') as f:
        data = f.readlines()
    sl = SqlList(data)
    sl.aggregate()
    res = sl.get_max_count(10, bPrint=True)
    res = sl.get_max_duration(10, bPrint=True)
    res = sl.get_max_duration_snahp(10, bPrint=True)
    print('=========== TOTAL TIME SPENT =============')
    sl.print_total_time()
