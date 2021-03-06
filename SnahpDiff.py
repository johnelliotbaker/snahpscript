from filecmp import dircmp
import os
import shutil
import difflib
import argparse


### Constants
#  PATH_PHPBB = '/var/www/phpbb/'
#  PATH_PHPBB = '/var/www/forum/' # Snahp
PATH_TMP = './tmp/'
PATH_LOGFILE = './log.txt'

### Definitions
GITDEF = {
        'hidebbcode': {
            'title': 'hideBBcode',
            'giturl': 'https://github.com/johnelliotbaker/hideBBcode.git',
            #  'giturl': 'git@github.com:marcovo/phpbb_hidebbcode.git',
            'subpath': os.path.join('ext', 'marcovo', 'hideBBcode'),
            'pathtmp': os.path.join(PATH_TMP, 'hideBBcode')
            },
        'gfksx': {
            'title': 'ThanksForPosts',
            'giturl': 'https://github.com/johnelliotbaker/gfksx.git',
            'subpath': os.path.join('ext', 'gfksx', 'ThanksForPosts'),
            'pathtmp': os.path.join(PATH_TMP, 'ThanksForPosts')
            },
        'snahp': {
            'title': 'snahp',
            'giturl': 'https://github.com/johnelliotbaker/snahp.git',
            'subpath': os.path.join('ext', 'jeb', 'snahp'),
            'pathtmp': os.path.join(PATH_TMP, 'snahp')
            }
        }


class Git(object):

    def __init__(self):
        pass

    def exec(self):
        self.PrepareTmp()

    def PrepareTmp(self):
        if not os.path.isdir(PATH_TMP):
            try:
                os.mkdir(PATH_TMP)
            except Exception as e:
                print(e)
                raise e
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
            strn = "{} doesn't exist".format(p1)
            self.logToFile(strn)
            if self.bVerbose and strn: print(strn)
            return
        if not os.path.isdir(p2):
            strn = "{} doesn't exist".format(p2)
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


def doGit():
    git = Git()
    git.exec()

def doDiff(bVerbose=True, bLog=True):
    global PATH_PHPBB
    sd = SnahpDiff()
    sd.bVerbose = bVerbose
    sd.bLog     = bLog
    for key in GITDEF:
        entry = GITDEF[key]
        p1    = os.path.join(PATH_PHPBB, entry['subpath'])
        p2    = entry['pathtmp']
        dcmp  = dircmp(p1, p2)
        sd.exec(dcmp)

if __name__ == "__main__":
    global PATH_PHPBB
    PATH_PHPBB = '/var/www/forum/'

    parser = argparse.ArgumentParser(description='Verify integrity of snahp extensions.')
    parser.add_argument('-m', '--mode',  type=str, help='Available modes are: all, gitclone, verify')
    parser.add_argument('--path_phpbb',  type=str, help='Path to phpbb directory')
    args = parser.parse_args()

    mode = args.mode
    if args.path_phpbb:
        PATH_PHPBB = args.path_phpbb
    if not os.path.isdir(PATH_PHPBB) or not os.path.isdir(os.path.join(PATH_PHPBB, 'ext')):
        raise Exception("{} is not a valid phpbb directory".format(PATH_PHPBB))
    if mode:
        if mode == 'all':
            doGit()
            doDiff()
        elif mode == 'gitclone':
            doGit()
        elif mode == 'verify':
            doDiff()
        else:
            print('Invalid mode selection.')
    else:
        doGit()
        doDiff()


