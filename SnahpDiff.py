from filecmp import dircmp
import os
import shutil
import difflib


### Constants
PATH_PHPBB = '/var/www/phpbb/'
#  PATH_PHPBB = '/var/www/forum/' # Snahp
PATH_EXT = os.path.join(PATH_PHPBB, 'ext')
PATH_TMP = '/tmp/'
PATH_LOGFILE = './log.txt'

### Definitions
GITDEF = {
        'hidebbcode': {
            'title': 'hideBBcode',
            'giturl': 'git@github.com:johnelliotbaker/hideBBcode.git',
            #  'giturl': 'git@github.com:marcovo/phpbb_hidebbcode.git',
            'path': os.path.join(PATH_PHPBB, PATH_EXT, 'marcovo', 'hideBBcode'),
            'pathtmp': os.path.join(PATH_TMP, 'hideBBcode')
            },
        'gfksx': {
            'title': 'gfksx',
            'giturl': 'git@github.com:johnelliotbaker/gfksx.git',
            'path': os.path.join(PATH_PHPBB, PATH_EXT, 'gfksx'),
            'pathtmp': os.path.join(PATH_TMP, 'gfksx')
            },
        'snahp': {
            'title': 'snahp',
            'giturl': 'git@github.com:johnelliotbaker/snahp.git',
            'path': os.path.join(PATH_PHPBB, PATH_EXT, 'jeb', 'snahp'),
            'pathtmp': os.path.join(PATH_TMP, 'snahp')
            }
        }


class Git(object):

    def __init__(self):
        pass

    def exec(self):
        self.PrepareTmp()

    def PrepareTmp(self):
        import subprocess
        for key in GITDEF:
            entry = GITDEF[key]
            title = entry['title']
            url = entry['giturl']
            fullpath = os.path.join(PATH_TMP, title)
            if os.path.isdir(fullpath):
                shutil.rmtree(fullpath)
            os.mkdir(fullpath)
            cmd = ['git', 'clone', url, fullpath]
            print('Executing {}'.format(cmd))
            subprocess.call(cmd)


class SnahpDiff(object):
    """For Diffing snahp related files"""
    def __init__(self):
        self.bVerbose    = True
        self.bLog        = True
        self.logFilename = PATH_LOGFILE
        if self.bLog:
            self.makeNewLog()

    def makeNewLog(self):
        if not self.bLog: return False
        fn = self.logFilename
        with open(fn, 'w', encoding='utf-8') as f:
            pass

    def logToFile(self, strn):
        if not self.bLog: return False
        fn = self.logFilename
        with open(fn, 'a', encoding='utf-8') as f:
            f.write(strn)
        
    def procOnlyLeft(self, dcmp):
        if dcmp.left_only:
            strn = ''
            strn += '\n\n*********************************************************\n'
            strn += "<<<<<<<<<< {}\n".format(dcmp.left)
            for name in dcmp.left_only:
                strn += '{}\n'.format(name)
            strn += '\n'
            if self.bVerbose and strn: print(strn)
            self.logToFile(strn)

    def procOnlyRight(self, dcmp):
        if dcmp.right_only:
            strn = ''
            strn += '\n\n*********************************************************\n'
            strn += ">>>>>>>>>> {}\n".format(dcmp.right)
            for name in dcmp.right_only:
                strn += '{}\n'.format(name)
            strn += '\n'
            if self.bVerbose and strn: print(strn)
            self.logToFile(strn)

    def procContent(self, dcmp):
        strn = ''
        for name in dcmp.diff_files:
            left = os.path.join(dcmp.left, name)
            right = os.path.join(dcmp.right, name)
            with open(left, 'r', encoding='utf-8') as f:
                l = list(map(str.strip, f.readlines()))
            with open(right, 'r', encoding='utf-8') as f:
                r = list(map(str.strip, f.readlines()))
            diff = difflib.unified_diff(l, r, fromfile=left, tofile=right)
            strn += '\n\n*********************************************************\n'
            strn += '\n'.join(diff)
            strn += '\n'
        if self.bVerbose and strn: print(strn)
        self.logToFile(strn)

    def exec(self, dcmp):
        strn = ''
        strn += '\n\n'
        strn += '++=====================================================++\n'
        strn += '||                                                     ||\n'
        strn += '|| {:52s}||\n'.format(dcmp.left)
        strn += '||                                                     ||\n'
        strn += '++=====================================================++\n'
        self.logToFile(strn)
        if self.bVerbose and strn: print(strn)
        p1 = dcmp.left
        p2 = dcmp.right
        if not os.path.isdir(p1):
            strn = '{} doesn''t exist'.format(p1)
            self.logToFile(strn)
            if self.bVerbose and strn: print(strn)
            return
        if not os.path.isdir(p2):
            strn = '{} doesn''t exist'.format(p2)
            self.logToFile(strn)
            if self.bVerbose and strn: print(strn)
            return
        self.procAll(dcmp)

    def procAll(self, dcmp):
        self.procOnlyLeft(dcmp)
        self.procOnlyRight(dcmp)
        self.procContent(dcmp)
        for sub_dcmp in dcmp.subdirs.values():
            self.procAll(sub_dcmp)


if __name__ == "__main__":
    #  git = Git()
    #  git.exec()

    sd = SnahpDiff()
    sd.bVerbose = True
    sd.bLog     = True
    for key in GITDEF:
        entry = GITDEF[key]
        p1    = entry['path']
        p2    = entry['pathtmp']
        dcmp  = dircmp(p1, p2)
        sd.exec(dcmp)
