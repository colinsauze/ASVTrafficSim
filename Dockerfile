FROM ubuntu:18.04
MAINTAINER Colin Sauze
RUN apt-get update && \
	apt-get -y install software-properties-common && \
	apt-add-repository ppa:opencpn/opencpn && \
    apt-get update && \
    apt-get install -y opencpn libjansson-dev python-gi-cairo build-essential python-pip && \
    pip install boatd python-boatdclient python-sailsd pynmea2 libais && \
    git clone --recursive https://github.com/colinsauze/ASVTrafficSim/asvtrafficsim.git && \
    cd sailsd && \
    make && \
    make install && \
    cd .. && \
    
RUN 
EXPOSE 2222 3333
CMD cd ASVTrafficSim & 
