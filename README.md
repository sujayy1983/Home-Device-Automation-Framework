```
Author: Sujayyendhiren Ramarao

Description: Home network automation WEB UI framework.
```

### What does this micro app offer ?

1. Home network discovery and caching 
   (i) D3Js Forcelayout visualization of discovered devices
   (ii) Caching of discovered info that can be leveraged by other parts of automation
        Current logic leverages cached data by looking at hostname for key match.

2. Basic Hue Light controls - Already configured lights are discovered and displayed on the UI

3. Bose Soundtouch - Device info display

4. Initial analysis of Kaggle datasets


### What does this tool leverage
1. Python 3.6 (Tested on MAC)
2. Flask + jinja2 + html + bootstrap + D3js


### Configuring this micro app
(i) Add more configurable parameters in configuration/configuration.yml
(ii) As we add more features we will cache data into the directory cache/*.cache


### Run this application

For normal usage
```
    python homeautomation.py
```

If we want more details like MAC address for discovered devices then 'python-nmap'
library requires 'sudo' permissions
```
    sudo python homeautomation.py
```


### Future plans
1. Isnt dockerized yet (planned soon)
2. More organized and modular code
2. More and more refinement
3. More home automation devices shall be integrated here
4. Voice activated controls (Leveraging google assistant) 
   or integration with AIY Google kit
5. More detailed analysis of Kaggle datasets


### Issues
-  No logging in the initial commit
- Cached device info should be used more intelligently than now
- Improvements in REST abstraction 
- Code assumes that ip address ending with '.1' is Gateway
- Lots of code restructing shall be done soon and comply with coding standards

### Report issues and suggestions
- Contact: sujayy1983@gmail.com
- Author: Sujay
