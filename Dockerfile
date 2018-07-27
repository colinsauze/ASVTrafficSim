FROM ubuntu:18.04
MAINTAINER Colin Sauze
RUN apt-get update && \
	apt-get -y install software-properties-common && \
	apt-add-repository ppa:opencpn/opencpn && \
    apt-get update && \
    apt-get install -y opencpn libjansson-dev python-gi-cairo build-essential python-pip git pkg-config build-essential libjansson-dev netcat && \
    pip install boatd python-boatdclient python-sailsd pynmea2 libais && \
    git clone --recursive https://github.com/colinsauze/ASVTrafficSim.git && \
    cd /ASVTrafficSim/sailsd && \
    make && \
    make install && \
    cd .. && \
    cd oceansofdata/ais-exploratorium-edu/ && \
    bunzip2 feed.ais.txt.bz2

EXPOSE 2222 3333

CMD cd /ASVTrafficSim/ && ./run.sh




