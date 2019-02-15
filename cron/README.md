# CRON
CRON script to run scheduled tasks on phpbb board

## Installation
git clone git@github.com:johnelliotbaker/snahpscript.git

## Configuration
**cron_manifest.json** configures cron jobs

### cron_manifest.json

- host->url             = Hostname of the phpbb server
- credentials->username = phpbb moderator username
- credentials->password = phpbb moderator password

To setup a job, define an entry in the jobs
A job entry requires 2 fields
- name           = Job name
- url            = url to trigger controller on phpbb
- last_performed = Timestamp of last cron execution. Set to 0 on init
- duration       = Interval at which the cron should run

Typically most cron jobs require moderators to run as many of the
functions involved uses included function from mcp

## Setting up system cron
System cron is used to call the cron script in snahpscript

Edit the system crontab with
```
sudo vi /etc/crontab
```
Then add an entry to run system cron to call our cron script
`
*/1 * * * * root python3 /home/username/script/snahpscript/cron/snahp_cron.py > /dev/null 2>&1
`

