```
Author: Sujayyendhiren Ramarao

Description: This app is being tested on MAC book pro and Raspberry Pi3. 
             As this app evolves, this document shall get better too :)
```

### Configuring this micro app
  - Core configuration file is configuration/configuration.yml
  - Sqlite data storage is present in cache/*.db
  - If we are looking at master-slave setup i.e. on two raspberry-pis or a primary raspberry pi and secondary on MAC then we need an additional 
     "configuration/haconf.yml", format is shared later in this document but not shared in this git repo.

### Install dependencies

##### Install dependencies on Raspberry Pi - 3
```
    Open Terminal
    sudo apt-get install python3-pandas libdnet nmap libssl-dev
    sudo pip3 install -r requirements.txt
```

##### Install dependencies on MAC

```
    Open Terminal
    pip3 install -r requirements.txt
    brew install libdnet nmap
```

##### Running the application
Run backgroud job that caches device information and that requires 
privileged permissions
```
    Manually run the following the first time
    sudo python3 osdetectioncron.py

    For subsequent periodic runs configure cron entry (crontab -e)
    15,45 * * * *  cd <app-path>/Home-Device-Automation-Framework; sudo /usr/bin/python3 osdetectioncron.py >> <path>/output
```

Run flask server
```
    python3 homeautomation.py
```
Note: We do not require sudo permissions for running this app.


### Start home automation as a service on bootup - Debian

##### Systemd configuration

Please specify a user in the following 'systemd' config as it is not a 
good practice to provide elevated privileges.

```
[Unit]
Description=My Home Network automation
After=network.target

[Service]
Type=simple
WorkingDirectory=<Your working directory>
ExecStart=/usr/bin/python3 homeautomation.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```