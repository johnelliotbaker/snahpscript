from SnahpConfig import SnahpConfig
import os
import shutil
import datetime
import subprocess
from subprocess import PIPE, Popen
import argparse
import glob
from os.path import join as pjoin



def getDirList(path):
    dlist = glob.glob(pjoin(path, '*/'))
    dlist.sort()
    return [os.path.relpath(x, path) for x in dlist]


def listBackup(pathBackup):
    aBackup = getDirList(pathBackup)
    n = len(aBackup)
    for i in range(n):
        backup = aBackup[i]
        print('{} : {} '.format(i, backup))




def createPath(path, bDelete=False):
    if os.path.isdir(path):
        if bDelete is True:
            print('{} exists and will be deleted.'.format(path))
            shutil.rmtree(path)
        else:
            print('{} exists and will not be deleted.'.format(path))
            return False
    os.makedirs(path)


class SnahpInstall(object):

    def __init__(self):
        self.setup()
        self.backupPathSuffix = ''

    def setup(self):
        self.config = SnahpConfig()
        self.config.loadConfig()
        if not os.path.isdir(self.config.pathPhpbb):
            raise Exception("{} is not a valid phpbb directory.\nEnter correct information into config.json > path > phpbb.".format(
                self.config.pathPhpbb
                ))
        now = datetime.datetime.now()
        sDate = now.strftime('%Y-%m-%d-%H_%M_%S')
        self.sDate = sDate
        self.config.dbUsername = 'root'

    def getBackupPath(self):
        sDate = self.sDate
        if self.backupPathSuffix:
            return sDate + '_' + self.backupPathSuffix
        return sDate

    def createDbBackup(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing MySQL Database Backup'.center(50)))
        print('++====================================================++')
        newPath = self.getBackupPath()
        pathToRoot = os.path.join(self.config.pathBackupRoot, newPath)
        username = self.config.db['username']
        database = self.config.db['database']
        dbFilename = newPath + '.gz'
        pathDb = os.path.join(pathToRoot, 'db')
        os.makedirs(pathDb)
        fullpath = os.path.join(pathDb, dbFilename)
        cmd = ('mysqldump', '-u', username, '-p', '--default-character-set=utf8', database)
        with open(fullpath, 'wb') as f:
            GZ = Popen('gzip', stdin=PIPE, stdout=f)
        p = Popen(cmd, stdout=GZ.stdin, stderr=PIPE)
        p.wait()
        GZ.stdin.close()
        GZ.wait()
        errmsg = p.stderr.read()
        if errmsg:
            print('\n\n')
            print('==============================================')
            print(errmsg)
            print('      Failed to create database backup.')
            return False
        else:
            if os.path.isfile(fullpath):
                print()
                print('MySQL database has been saved to:')
                print('{}'.format(fullpath))
                return True

    def createFullCodeBackup(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing Full Codebase Backup'.center(50)))
        print('++====================================================++')
        newPath = self.getBackupPath()
        pathPhpbb = self.config.pathPhpbb
        pathToRoot = os.path.join(self.config.pathBackupRoot, newPath)
        fro = os.path.join(pathPhpbb)
        to = os.path.join(pathToRoot, 'FullCode')
        os.makedirs(to)
        fullpath = os.path.abspath(os.path.join(to, 'forum.tar.gz'))
        os.chdir(fro)
        cmd = ('tar', '-zcf', fullpath, '.')
        print(cmd)
        p = Popen(cmd, stderr=PIPE)
        p.wait()

    def createExtBackup(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing Extension Codebase Backup'.center(50)))
        print('++====================================================++')
        newPath = self.getBackupPath()
        aExt = self.config.aExtension
        pathPhpbb = self.config.pathPhpbb
        pathExt = self.config.pathExt
        pathToRoot = os.path.join(self.config.pathBackupRoot, newPath)
        for ext in aExt:
            fro = os.path.join(pathPhpbb, pathExt, ext['path'], ext['title'])
            to = os.path.join(pathToRoot, pathExt, ext['path'], ext['title'])
            print('Backing up {}'.format(fro))
            print('        to {}'.format(to))
            if os.path.isdir(fro):
                shutil.copytree(fro, to)

    def install(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing Extension Installtion'.center(50)))
        print('++====================================================++')
        pathPhpbb = self.config.pathPhpbb
        pathExt = self.config.pathExt
        aExt = self.config.aExtension
        for ext in aExt:
            to = os.path.join(pathPhpbb, pathExt, ext['path'], ext['title'])
            if os.path.isdir(to):
                shutil.rmtree(to)
            os.makedirs(to)
            url = ext['giturl']
            cmd = ['git', 'clone', url, to]
            subprocess.call(cmd)

    def restore(self):
        command = ''
        config = self.config
        pForum = config.pathPhpbb
        print(config)
        while (command != "q"):
            command = input("(l)ist, (D)elete Forum, (R)estore (q)uit: ")
            if command == "q":
                return
            elif command == "D":
                confirm = input("Are you sure you want to delete {}? (type yes)".format(
                    pForum
                    ))
                if confirm == "yes":
                    try:
                        os.rmdir(pForum)
                    except Exception as e:
                        print(e)
            elif command == "l":
                path = listBackup(config.pathBackupRoot)
                print(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Snahp backup and install utility.')
    parser.add_argument('command', type=str, help='backupdb, backupext, backupfull, install')
    args = parser.parse_args()

    command = args.command

    si = SnahpInstall()
    if not command:
        print('SnahpInstall requires one of the following commands:')
        print('backupdb, backupext, backupfull, install')
    else:
        if command == 'install':
            si.install()
        elif command[:6] == 'backup':
            suffix = input('Enter path suffix if desired: ')
            suffix = '_'.join(suffix.split())
            si.backupPathSuffix = suffix
            if command == 'backupext':
                si.createExtBackup()
            elif command == 'backupdb':
                bDbBackup = si.createDbBackup()
                if not bDbBackup:
                    print('Skipping Code backup and installation due to failed database backup.')
            elif command == 'backupfullcode':
                print("Making Full Codebase Backup")
                si.createFullCodeBackup()
            elif command == 'backupfull':
                bDbBackup = si.createDbBackup()
                if bDbBackup:
                    si.createFullCodeBackup()
                else:
                    print('Skipping Code backup and installation due to failed database backup.')
        elif command == 'restore':
            si.restore()

