sailsd/sailsd > /dev/null &
sleep 1
./init_sails.sh
boatd boatd.yml &
sleep 5
boatdctl behaviour-start example
boatd-opencpn/boatd-opencpn 127.0.0.1:2223 10111 &
python recvBoatData.py
killall boatd
killall sailsd
killall boatd-opencpn
