# Patcher utility script for Snahp
Modifying phpbb functionalities can be done via
1) Extensions
2) Direct modification to core phpbb files

For developing extensions, it is perferable to use git since extensions can be
developed entirely in isolation.

For modifying core files, it may be preferable to use diff-patch as the
board itself may be installed using git. Any modification will be undone
with future git pulls and likely cause forced merges.
For novices, this often leads to big headaches.


## Installing
This is part of the snahpscript package, and should be cloned as such.
```
git clone https://github.com/johnelliotbaker/snahpscript.git
```
If local repository already exists, cd into snahpscript directory

```
git pull
```

## Listing Available Development Packages
Diff files are provided by the developer in "patch_data" directory.
To see available packages for deployment:

```
python SnahpPatch.py list
```

## Making Deployment Package
The development packages cannot directly be deployed.
To make a system specific deployment package:
```
python SnahpPatch.py make -p PACKAGE_NAME
```
Here, PACKAGE_NAME should be replaced with the name of the available package from the listing.

## Deploying a Package
Once a deployment package is created, it can be applied.

```
python SnahpPatch.py deploy -p PACKAGE_NAME
```

This will start an interactive prompt for deploying the package.
The following commands are available.

```
+---+--------+--------------------------------------------+   
|   | cmd    | Description                                |   
+---+--------+--------------------------------------------+   
| l | list   | List the available patches                 |   
+---+--------+--------------------------------------------+   
| a | apply  | Apply the package. Once Selected,          |   
|   |        | a second prompt will ask for patch number. |   
+---+--------+--------------------------------------------+   
| r | revert | If a patch was applied previously,         |   
|   |        | this will revert that change.              |   
+---+--------+--------------------------------------------+   
| d | detail | Show the actual diff                       |   
+---+--------+--------------------------------------------+   
| q | quit   | Quit the interactive deployment            |   
+---+--------+--------------------------------------------+   
```

Once a patch has been applied, the listing should show correct status for
that patch.
