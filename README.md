# Apple-UserAg
A helper to build Apple User-Agent, using the ipsw.me API.
## Installation
```
pip install git+https://github.com/novitae/apple_userag
```
And to download the data from [ipsw.me](https://ipsw.me), do:
```
apple_userag update
```
## Usage
After having made sure that you installed the data with the upper command, you can use it as a library, as follows:
```py
>>> import apple_userag
>>>
>>> # Listing the available devices
>>> apple_userag.available_devices()
['iPhone', 'iPod', 'iPad', 'AppleTV', 'Watch', 'AudioAccessory', 'iBridge', 'MacBookPro', 'MacBookAir', 'ADP', 'Macmini', 'iMac', 'Mac', 'VirtualMac']
>>>
>>> # You can take a look at the list of a given device type by doing:
>>> d = apple_userag.devices['iPhone'][0]
>>> d
[AppleDevice(name='iPhone 2G', identifier='iPhone1,1', firmwares=[Firmware(version='3.1.3', buildid='7E18', releasedate=None, uploaddate=datetime.datetime(2010, 1, 22, 1, 53, 8, tzinfo=TzInfo(UTC)), signed=False), ...]
>>> 
>>> d.name, d.identifier
"iPhone 2G", "iPhone1,1"
>>>
>>> # You can choose a random version of off the device, using:
>>> d.random_firmware
Firmware(version='2.0', buildid='5A347', releasedate=None, uploaddate=datetime.datetime(2008, 7, 8, 18, 53, 47, tzinfo=TzInfo(UTC)), signed=False)
```