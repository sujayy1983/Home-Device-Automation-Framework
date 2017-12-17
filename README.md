```
Author: Sujayyendhiren Ramarao

Description: Home network automation WEB UI framework.
```

### What does this micro app offer ?

1. Home network discovery and caching 
....(i) D3Js Forcelayout visualization of discovered devices. Hover mouse over any node to view
       IP address and hostname of device.
       ![Discovered home network](/static/img/samplenw.png)
....(ii) Caching of discovered info that can be leveraged by other parts of automation
        Current logic leverages cached data by looking at hostname for key match.

2. Basic Hue Light controls - Already configured lights are discovered and displayed on the UI
   ![Philips Hue view](/static/img/samplehue.png)

3. Bose Soundtouch - Device info display
   ![BoseSoundtouch view](/static/img/samplebose.png)

4. Os detection of discovered devices
   Note: Few entries are intentionally removed for security reasons.
   ![OS detection of home devices](/static/img/sampleosdetect.png)

5. Initial analysis of Kaggle labelled datasets
   This tells us maximum occurrences per column
   Step1: Upload a csv dataset using upload options.
   Step2: Select a dataset and select top occurrence count in rows.
   TBD


### What does this tool leverage
1. Python 3.6 (Tested on MAC and testing in progress on Raspberry Pi3)
2. Flask + jinja2 + html + bootstrap + D3js + nmap + scapy


### Configuring this micro app
(i) Add more configurable parameters in configuration/configuration.yml
(ii) As we add more features we will cache data into the directory cache/*.cache


### Install and run this application

##### MAC - Install and run this micro app 

```
    Open Terminal
    pip install -r requirements.txt
    brew install libdnet nmap
    sudo python homeautomation.py
```

##### Raspberry Pi - 3
```
    Open Terminal
    sudo apt-get install python-pandas libdnet nmap
    sudo pip install -r requirements.txt
    sudo python homeautomation.py
```

### Future plans
1. More organized and modular code with more improvements
2. More home automation devices shall be integrated here
3. Voice activated controls (Leveraging google assistant) 
   or integration with AIY Google kit
4. More detailed analysis of Kaggle datasets


### Issues
- Container network and home network are different so issue discovering in
  containerized version
- Failure to discover an IP for BoseSoundtouch/Philips hue bridge results in page crash corresponding page crash. Should display a message and exit gracefully. 
- No logging in the initial commit
- Cached device info should be used more intelligently than now
- Need to parallelize OS detection for faster response
- Improvements in REST abstraction 
- Code assumes that ip address ending with '.1' is Gateway
- Lots of code restructing shall be done soon and comply with coding standards



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