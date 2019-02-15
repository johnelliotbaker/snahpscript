import datetime

def log(status):
    with open('/home/ubm/script/snahpscript/cron/log.txt', 'a', encoding='utf-8') as f:
        now = datetime.datetime.now()
        datestrn = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        strn = '{} {}\n'.format(datestrn, status)
        f.write(strn)

log('test2')
