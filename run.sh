sailsd/sailsd &
sleep 1
./init_sails.sh
boatd boatd.yml &
sleep 5
boatdctl behaviour-start example
python recvBoatData.py
