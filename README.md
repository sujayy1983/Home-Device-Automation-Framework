```
Author: Sujayyendhiren Ramarao

Description: Home network automation micro web framework.
```

### What does this micro app offer ?

1. Home network discovery and caching 
  - D3Js Forcelayout visualization of discovered devices. Hover mouse over any node to view
       IP address and hostname of device.
       ![Discovered home network](/static/img/samplenw.png)
  - Caching of discovered info that can be leveraged by other parts of automation
        Current logic leverages cached data by looking at hostname for key match.

2. Basic Hue Light controls - Already configured lights are discovered and displayed on the UI
   ![Philips Hue view](/static/img/samplehue.png)

3. Bose Soundtouch - Device info display
   ![BoseSoundtouch view](/static/img/samplebose.png)

4. Os detection of discovered devices 
   Note: Few entries are intentionally removed for security reasons.
   ![OS detection of home devices](/static/img/sampleosdetect.png)

5. Assuming that this app is running on a Raspberry Pi and is running 24*7. You'll need to configure audio in case you havent configured it yet. To use this app as doorbell, place a few mp3 files in a local mp3 directory and install the following
```
sudo apt-get install -y alsa-utils  mpg321 lame
sudo modprobe snd_bcm2835
```

6. Initial analysis of Kaggle labelled datasets
   This tells us maximum occurrences per column
   Step1: Upload a csv dataset using upload options.
   Step2: Select a dataset and select top occurrence count in rows.
   TBD


### What does this tool leverage
1. Tested on MAC with Python 3.6 and Python3.4 on Raspberry Pi3.
2. Flask + jinja2 + html + bootstrap + D3js + nmap + scapy


### Configuring this micro app
(i) Add more configurable parameters in configuration/configuration.yml
(ii) As we add more features we will cache data into the directory cache/*.cache
(iii) If we are interested in running this app in two of the raspberry pis at home and make device detection more
      reliable then there is an evolving feature that can sync device detection from across secondary devices via sftp.
      for setting that feature create a file "configuration/haconf.yml" and fill in username and password of primary 
      Raspberry pi.

```
---

#------------------------------------------------------#
# HA configuration for Primary-Secondary Configuration #
# -----------------------------------------------------#

CLUSTERINFO:
  primary: "raspberrypi.local"
  others: ["raspberrypi-second.local"]

CREDENTIALS:
  username: <username> 
  password: <password> 

DIRECTORY:
  syncdir: "<absolute-path>/Home-Device-Automation-Framework/cache"
  getfiles: ["devices-{0}.cache", "osdetection-{0}.cache"]
```


### Install and run this application

##### Install dependencies on MAC

```
    Open Terminal
    pip3 install -r requirements.txt
    brew install libdnet nmap
```

##### Install dependencies on Raspberry Pi - 3
```
    Open Terminal
    sudo apt-get install python3-pandas libdnet nmap
    sudo pip3 install -r requirements.txt
```

##### Running the application
Run backgroud job that caches device information and that requires 
privileged permissions
```
    sudo python3 osdetectioncron.py
```

Run flask server
```
    python3 homeautomation.py
```

### Start home automation as a service on bootup - Debian

##### Systemd configuration

Please specify a user in the following 'systemd' config as it is not a 
good practice to provide elevated privileges. Only reason for giving
elevated privilege is to run OS scanning/detection. If we are not much
interested in that feature then we do not need higher privileges.

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

### Future plans
1. More organized and modular code with more improvements
2. More home automation devices shall be integrated here
3. Voice activated controls (Leveraging google assistant) 
   or integration with AIY Google kit
4. More detailed analysis of Kaggle datasets
5. Release unittest options. For now it is evolving


### Issues
- Container network and home network are different so issue discovering in
  containerized version
- No logging in the initial commit
- Improvements in REST abstraction 
- Code assumes that ip address ending with '.1' is Gateway


### Docker implementation

##### Build docker image
```
docker build -t homeautomation .
```

##### Run docker container
```
docker run -d --name="HomeAutomation" -p 5000:5000 sujayy1983/homeautomation
```

### Report issues and suggestions
- Contact: sujayy1983@gmail.com
- Author: Sujay
