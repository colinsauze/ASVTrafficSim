Bootstrap:docker
From:ubuntu:18.04

%help
    Container for ASVTrafficSim

%labels
    MAINTAINER Colin Sauze

%environment
    #define environment variables here
    
%post  
    apt-get update
    apt-get -y install software-properties-common
    apt-get update
    apt-get install -y libjansson-dev python-gi-cairo build-essential python-pip git pkg-config build-essential libjansson-dev netcat
    pip install boatd python-boatdclient python-sailsd pynmea2 libais
    git clone --recursive https://github.com/colinsauze/ASVTrafficSim.git
    cd /ASVTrafficSim/sailsd
    make
    make install
    cd ..


%runscript
    cd /ASVTrafficSim/
    ./run.sh