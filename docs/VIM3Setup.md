# VIM3 Setup
Before the VIM3 is installed in the system it has to be configured with an operating system image and basic setup to allow connection to it once it is installed into the Water Auto Turret because there is no access to the USB-C or Ethernet ports once installed. The serial debug port is brought out onto the top of the main board for any issues that need a hard wired connection. 

First the latest version of Ubuntu Server needs to be installed into the EMMC following the instructions [here](https://docs.khadas.com/linux/vim3/InstallOsIntoEmmc.html). Then do a full system upgrade as per the instructions [here](https://docs.khadas.com/linux/vim3/UpgradeSystem.html). 

Next the WiFi connection has to be setup following the instructions [here](https://docs.khadas.com/linux/vim3/Wifi.html#server). Alternatively it may be useful to set the VIM3 up as a hotspot following the instructions [here](https://docs.khadas.com/linux/vim3/WifiApstaMode.html) to avoid the need for a wifi network but I haven't tested this yet and have just used a wifi hotspot from my phone to connect the Water Auto Turret to when out of range of my home WiFi. 

Finally make sure that it is possible to SSH into the VIM3 over the WiFi connection and then one can either shutdown the VIM3 ready for installation into the Electronics Enclosure or install the rest of the software as described below.

## Software Installation 
The following steps have to be carried out to install the software for the Water Auto Turret:
* WiringPi-Python is required for GPIO access this is installed by following the instructions [here](https://github.com/khadas/WiringPi-Python#manual-build) for Python 3.
* Clone the GitHub repository for the Water Auto Turret
  * `git clone https://github.com/neilbirtles/WaterAutoTurret`
* Change to the project directory, create a Python virtual environment with access to the system site packages to pick up WiringPi-Python and activate it
  * `cd WaterAutoTurret`
  * `python3 -m venv venv --system-site-packages`
  * `source venv/bin/activate`
* Install PIP
  * `sudo apt install python3-pip`
* Install all dependencies:
  * `pip3 install matplotlib`
  * `pip3 install install numpy`
  * `wget https://github.com/khadas/ksnn/blob/master/ksnn/ksnn-1.3-py3-none-any.whl`
  * `pip3 install ksnn-1.3-py3-none-any.whl`
  * `pip3 install Flask`
  * `pip3 install Bootstrap-Flask`
  * `pip3 install spidev`

Once everything is installed then the web app can be run using the following command:
* `python3 autoturret.py`

The web interface should then be available on the VIM3’s IP address on port 5000, but some errors may be thrown if the other hardware is not available (i.e. this is benign just run on the bare VIM3).

[{Home}](https://github.com/neilbirtles/WaterAutoTurret/blob/main/docs/README.md) [{Next}](https://github.com/neilbirtles/WaterAutoTurret/blob/main/docs/SoftwareDescription.md)
