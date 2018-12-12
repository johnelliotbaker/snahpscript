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


