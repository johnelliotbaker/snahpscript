# SnahpScript
A collection of administrative scripts for Snahp

## Installation
git clone git@github.com:johnelliotbaker/snahpscript.git

## SnahpDiff
#### Requires: Python3.5+

#### Usage
python3 SnahpDiff.py

For custom phpbb directory:
python3 SnahpDiff.py --path_phpbb /path/to/phpbb

Includes 3 modes to be used with -m (or --mode) switch:  
**-m gitclone**: Only git clones the extensions from repo to TMP  
**-m verify**  : Only runs file to generate diff reports  
**-m all**     : Runs gitclone and verify sequentially  
It may be more efficient to gitclone once,
then only run verify on subsequent runs.


## SnahpInstall
#### Requires: Python3.5+

#### Usage
It is advised to make back up before installation.

Make code and database backup
```
python3 SnahpInstall.py backup

```

Install Snahp related extensions
```
python3 SnahpInstall.py install
```

Backup & install in single command
```
python3 SnahpInstall.py all

```

#### Configuration
**config.json** serves the role of assigning core constants and parameters for the SnahpInstall.
The following parameters are required for proper execution.

- path->phpbb        = The path to phpbb directory  
- database->username = MySQL username used to access phpbb database  
- database->database = MySQL database name  

In addition, path->backup and path->tmp are used to define backup
directories and for storing temporary files used in other operations.


#### Backup
The back ups are stored in the directory defined in config.json

#### Database restoration
Database backup can be restored in shell using:
```
gunzip < NAME_OF-FILE.GZ | mysql -u USERNAME -p --default-character-set=utf8 DATABASE_NAME
```
