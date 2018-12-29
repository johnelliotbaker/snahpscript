import subprocess
from subprocess import PIPE
import hashlib
import argparse
import os
from os.path import join as pjoin
from datetime import datetime
import json
import uuid
import glob
import pdb


PACKAGE_SUBPATH = 'package/'
PATCH_PATH      = 'patch_data/'
DBFILE_NAME     = 'db.json'


class Database(object):
    def __init__(self, pathToDatabaseFile):
        self.aEntry = []
        self.aPair = set()
        self.fullpath = pathToDatabaseFile
        self.load()

    @classmethod
    def fromFilepath(cls, pathToDatabaseFile):
        db = {
                "aEntry": [],
                "aPair": [],
                }
        with open(pathToDatabaseFile, 'w') as f:
            json.dump(db, f, indent=2)
        return Database(pathToDatabaseFile)


    def isValidPath(self):
        if os.path.isfile(self.fullpath):
            return True
        return False

    def save(self):
        if not self.isValidPath():
            raise Exception("Database doesn't have valid file path.")
        db = {
                "aEntry": self.aEntry,
                "aPair": self.aPair,
                }
        with open(self.fullpath, 'w') as f:
            json.dump(db, f, indent=2)

    def load(self):
        if not self.isValidPath():
            raise Exception("Database doesn't have valid file path.")
        with open(self.fullpath, 'r') as f:
            db          = json.loads(f.read())
            self.aEntry = db["aEntry"]
            self.aPair  = db["aPair"]


def getmd5(filename):
    #  https://stackoverflow.com/questions/1131220/get-md5-hash-of-big-files-in-python
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def checkWritePermission(db):
    pass

def listPatch(db):
    aEntry = db.aEntry
    nEntry = len(aEntry)
    print("\n======================= Available Patches =======================\n")
    for i in range(nEntry): 
        entry = aEntry[i]
        path = entry['path']
        hash = entry['hash']
        pf, pt = path['fro'], path['too']
        pathfro = pjoin(pf['base'], pf['top'], pf['basename'])
        pathtoo = pjoin(pt['base'], pt['top'], pt['basename'])
        patchStatus = "patched" if entry['bApplied'] else "unpatched"
        strn = '  {}: {} : {}'.format(i, patchStatus, pathtoo)
        print(strn)
    print("\n=================================================================\n")

def printPatchDetail(db, iSelect, packageName):
    deploymentPath = pjoin(PACKAGE_SUBPATH, packageName)
    aEntry = db.aEntry
    entry = aEntry[int(iSelect)]
    eid = entry['id']
    fpath = pjoin(deploymentPath, '{}.patch'.format(eid))
    print('Reading from {} ...'.format(fpath))
    with open(fpath, 'r') as f:
        data = f.read()
        print(data)

def applyPatch(db, iSelect, packageName, bReverse=False):
    deploymentPath = pjoin(PACKAGE_SUBPATH, packageName)
    aEntry = db.aEntry
    entry = aEntry[int(iSelect)]
    eid = entry['id']
    path = entry['path']
    hash = entry['hash']
    pf, pt = path['fro'], path['too']
    pathpatch = pjoin(deploymentPath, '{}.patch'.format(eid))
    pathfro = pjoin(pf['base'], pf['top'], pf['basename'])
    pathtoo = pjoin(pt['base'], pt['top'], pt['basename'])
    hashfro = getmd5(pathfro)
    hashtoo = getmd5(pathtoo)
    if not os.path.isfile(pathtoo):
        print("Non-existent destination path {}".format(pathtoo))
        return False

    if (hashtoo != hash['too'] and bReverse is False) or \
       (hashtoo != hash['fro'] and bReverse is True):
        print("The current target hash does not match database.")
        return False
    args = ['patch', '-d', os.path.dirname(pathtoo)]
    if bReverse is True:
        args.append('--reverse')
        entry['bApplied'] = False
        entry['datetime']['patched'] = None
    else:
        entry['bApplied'] = True
        entry['datetime']['patched'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prCat = subprocess.Popen(['cat', pathpatch], stdout=PIPE )
    prPatch = subprocess.Popen(args, stdout=PIPE, stdin=prCat.stdout)
    patchStrn = prPatch.communicate()[0].decode('utf-8')

    print("\n{} {} on {} ...".format(
        'Restoring' if bReverse else 'Applying', eid, pathtoo))
    if "is read-only;" in patchStrn:
        print(patchStrn)
        print()
        print('+=============================================+')
        print("|  You don't have write permission to patch.  |")
        print('+=============================================+')
        print()
        raise Exception("You need to have write permission to apply this patch.\n\n")
    else:
        db.save()
    listPatch(db)
    

def deploy(packageName):
    deploymentPath = pjoin(PACKAGE_SUBPATH, packageName)
    print(deploymentPath)
    dbFile = pjoin(deploymentPath, DBFILE_NAME)
    db = Database(dbFile)
    print(dbFile)
    
    aEntry = db.aEntry
    nEntry = len(aEntry)
    command = None
    listPatch(db)
    while(command != "q"):
        command = input("\n(l)ist, (a)pply, (r)evert, (d)etail, (q)uit: ")
        print(command)
        if command == "":
            continue
        if command == "l":
            listPatch(db)
        elif command in "adr":
            iSelect = input("\nEnter patch number (0 to {}): ".format(nEntry-1))
            if not iSelect.isdigit():
                print('Patch number must be an integer.')
            else:
                if command == "d":
                    printPatchDetail(db, int(iSelect), packageName)
                elif command == "a":
                    applyPatch(db, int(iSelect), packageName)
                elif command == "r":
                    applyPatch(db, int(iSelect), packageName, True)


def makeDeployment(packageName, target):
    deploymentPath = pjoin(PACKAGE_SUBPATH, packageName)
    modifiedPath = pjoin(PATCH_PATH, packageName)
    if not os.path.isdir(PATCH_PATH):
        os.mkdir(PATCH_PATH)
    if not os.path.isdir(deploymentPath):
        os.mkdir(deploymentPath)
    dbFile = pjoin(deploymentPath, DBFILE_NAME)
    db = Database.fromFilepath(dbFile)

    filelist = glob.glob(pjoin(modifiedPath, '**', '*.php'), recursive=True)
    print(modifiedPath)
    for filename in filelist:
        basename = os.path.basename(filename)
        basepath = os.path.dirname(filename)
        toppath = os.path.relpath(basepath, modifiedPath)
        print(basename)

        #  pdb.set_trace()
        entry = {}
        path = {}
        hash = {}
        dt = {'created': None, 'patched': None}

        fropath = {}
        fropath['base']     = modifiedPath
        fropath['top']      = toppath
        fropath['basename'] = basename

        toopath = {}
        toopath['base']     = target
        toopath['top']      = toppath
        toopath['basename'] = basename


        path['fro'] = fropath
        path['too'] = toopath

        frofull = pjoin(fropath['base'], fropath['top'], fropath['basename'])
        toofull = pjoin(toopath['base'], toopath['top'], toopath['basename'])

        hashfro = hash['fro'] = getmd5(frofull)
        hashtoo = hash['too'] = getmd5(toofull)

        dt['created'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry['path'] = path
        entry['hash'] = hash
        entry['datetime'] = dt

#  start making patch

        try:
            with open(dbFile, 'r') as f:
                db = json.loads(f.read())
        except:
            with open(dbFile, 'w') as f:
                db = {"aEntry":[], "aPair":[]}
                json.dump(db, f)


        sPair = set(db['aPair'])
        hashpair = '{}{}'.format(hashfro, hashtoo)
        if hashpair in sPair:
            continue
        db['aPair'].append(hashpair)

        patchpath = {}
        patchpath['base'] = deploymentPath
        patchpath['top'] = './'
        entryid = uuid.uuid4().hex
        patchpath['basename'] = '{}.patch'.format(entryid)
        patchfull = pjoin(patchpath['base'], patchpath['top'], patchpath['basename'])
        path['patch'] = patchpath
        makePatchFile(toofull, frofull, patchfull)
        entry['id'] = entryid
        entry['bApplied'] = False

        db['aEntry'].append(entry)

        with open(dbFile, 'w') as f:
            json.dump(db, f, indent=2)

    return


def makePatchFile(old, new, outputfilename):
    args = ['diff', '-u', old, new]
    prDiff = subprocess.Popen(args, stdout=PIPE)
    patchStrn = prDiff.communicate()[0]
    with open(outputfilename, "wb") as f:
        f.write(patchStrn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="(m)ake, (d)eploy, (l)ist")
    parser.add_argument("--source")
    parser.add_argument("-t", "--target")
    parser.add_argument("-p", "--package")
    args = parser.parse_args()
    mode = args.mode
    package = args.package
    target = args.target if args.target else '/var/www/forum/'

    if not os.path.isdir(PACKAGE_SUBPATH):
        os.mkdir(PACKAGE_SUBPATH)

    if mode in ["m", "make"]:
        if package:
            makeDeployment(package, target=target)
        else:
            makeDeployment('testpackage')
    elif mode in ["d", "deploy"]:
        if package:
            if os.path.isdir(pjoin(PACKAGE_SUBPATH, package)):
                deploy(package)
            else:
                raise Exception('Unknown package name "{}"'.format(package))
    elif mode in ["l", "list"]:
        if os.path.isdir(PATCH_PATH):
            filelist = glob.glob(pjoin(PATCH_PATH, '*'))
            aPackage = []
            for filename in filelist:
                basepath = filename
                toppath = os.path.relpath(basepath, PATCH_PATH)
                aPackage.append(toppath)
            if aPackage:
                print("The following packages are available.")
                print("+=======================================================+")
                for package in aPackage:
                    print('|{:^55s}|'.format(package))
                print("+=======================================================+")
        else:
            print("No packages currently available.")
    elif mode in ["p", "plist"]:
        if os.path.isdir(PACKAGE_SUBPATH):
            filelist = glob.glob(pjoin(PACKAGE_SUBPATH, '**', "db.json"), recursive=True)
            aPackage = []
            for filename in filelist:
                basepath = os.path.dirname(filename)
                toppath = os.path.relpath(basepath, PACKAGE_SUBPATH)
                aPackage.append(toppath)
            if aPackage:
                print("The following packages are available.")
                print("+=======================================================+")
                for package in aPackage:
                    print('|{:^55s}|'.format(package))
                print("+=======================================================+")
        else:
            print("No packages currently available.")
