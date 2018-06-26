#!/bin/sh

echo "{\"set\": {\"latitude\": 37.821, \"longitude\": -122.413}}" | nc 127.0.0.1 3333
echo "{\"set\": {\"wind-angle\": 180}}" | nc 127.0.0.1 3333
echo "{\"set\": {\"rudder-angle\": 0}}" | nc 127.0.0.1 3333