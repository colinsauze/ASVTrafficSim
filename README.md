# ASVTrafficSim

## Installation

### Install system libraries

sudo apt install libjansson-dev
sudo apt install python-gi-cairo

(or your system's equivalent)

### Install pip dependencies:

pip install boatd python-boatdclient python-sailsd pynmea2 libais

### Download this repository and its submodules

git clone --recursive https://github.com/colinsauze/ASVTrafficSim/asvtrafficsim.git

### Build sailsd

cd sailsd
make


### OpenCPN for chart plotting

sudo add-apt-repository ppa:opencpn/opencpn
sudo apt-get update
sudo apt-get install opencpn

launch opencpn

Click on the options icon (the spanner on the toolbar), go to connections
add a new incoming connection on UDP port 10110
add an outgoing UDP connection on port 10111 with only the GGA sentence enabled


### Running:

sailsd/sailsd

set initial lat/lon and wind direction
./init_sails.sh 

run boatd
boatd boatd.yml

(optional) run sails-ui
sails-ui/sails-ui

run opencpn plugin
boatd-opencpn/boatd-opencpn

run behaviour:
boatdctl behaviour-start example

run collision detector
python recvBoatData.py
