from SnahpConfig import SnahpConfig
import os
import shutil
import datetime
import subprocess
from subprocess import PIPE, Popen
import argparse


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

    def createDbBackup(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing MySQL Database Backup'.center(50)))
        print('++====================================================++')
        sDate = self.sDate
        pathToRoot = os.path.join(self.config.pathBackupRoot, sDate)
        username = self.config.db['username']
        database = self.config.db['database']
        dbFilename = sDate + '.gz'
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

    def createCodeBackup(self):
        print('\n\n')
        print('++====================================================++')
        print('|| {} ||'.format('Performing Extension Codebase Backup'.center(50)))
        print('++====================================================++')
        sDate = self.sDate
        aExt = self.config.aExtension
        pathPhpbb = self.config.pathPhpbb
        pathExt = self.config.pathExt
        pathToRoot = os.path.join(self.config.pathBackupRoot, sDate)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Snahp backup and install utility.')
    parser.add_argument('command', type=str, help='backup, install, all')
    args = parser.parse_args()

    command = args.command

    si = SnahpInstall()
    if not command:
        print('SnahpInstall requires one of the following commands:')
        print('install, backup, all')
    else:
        if command == 'backup':
            bDbBackup = si.createDbBackup()
            if bDbBackup:
                si.createCodeBackup()
            else:
                print('Skipping Code backup due to failed database backup.')
        elif command == 'install':
            si.install()
        elif command == 'all':
            bDbBackup = si.createDbBackup()
            if bDbBackup:
                si.createCodeBackup()
                si.install()
            else:
                print('Skipping Code backup and installation due to failed database backup.')
