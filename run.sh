sailsd/sailsd > /dev/null &
sleep 1
./init_sails.sh
boatd/bin/boatd boatd.yml &
sleep 5
boatdctl behaviour-start example
boatd-opencpn/boatd-opencpn 127.0.0.1:2223 10111 &
python recvBoatData.py
killall boatd
killall sailsd
kill `ps a | grep "boatd-opencpn 127.0.0.1:2223 10111" | grep -v grep | awk '{print $1}'`
kill `ps a | grep "python simulator-behaviour/looped-waypoint-behaviour" | grep -v grep | awk '{print $1}'`

