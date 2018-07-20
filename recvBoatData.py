import socket
import pynmea2
import time
import datetime
import readData

UDP_IP = "127.0.0.1"
UDP_PORT = 10111

sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))

print("Loading data")
aisdata = readData.read_data("oceansofdata/ais-exploratorium-edu/feed.ais.txt")
print("Data Loaded")

start_time = time.time()

#our datasources are old and don't change time
sim_start_time = 1417005700
#sim_end_time = 1417007806
sim_end_time = 1417012900
sim_real_diff = start_time - sim_start_time

#used to store a list of collisions and near misses 
collisions = list()
near_misses = list()
position_log = dict()

position_log[0] = list()

#ships with bad position data
blacklist = [366999711,366985330] 

while True:
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data_str = data.decode('utf-8')
    
    #print("received message:", data_str)
    if data_str.startswith("$GPGGA") or data_str.startswith("$GPRMC") or data_str.startswith("$GPGLL"):
        msg = pynmea2.parse(data_str)
        #print(msg.latitude,msg.longitude)
        

        sim_time = time.time() - sim_real_diff
        
        print("real time=",msg.timestamp,"sim_time=",sim_time)
        
        if sim_time > sim_end_time:
            break

        
        position_log[0].append((sim_time,msg.latitude,msg.longitude))
        
        #test for collisions
        for ais_target in aisdata:

	    #ignore blacklisted ships
	    if ais_target in blacklist:
		continue

            #print(aisdata[ais_target].toJSON())
            if len(aisdata[ais_target].getPositionReports()) > 1:
                
                ais_target_loc = (readData.getCurrentLocation(sim_time,aisdata[ais_target].MMSI,aisdata))
                
                if ais_target_loc != None:
                    
                    #ignore things at the north pole, null point etc
                    if ais_target_loc[0] == 0.0 and ais_target_loc[1] == 0.0:
                        continue
                    if ais_target_loc[0] == 90.0:
                        continue               
             
                    #print(ais_target_loc)
                    if ais_target not in position_log:
                        print("mmsi",ais_target,"not in position log yet")
                        position_log[ais_target] = list()
                        
                    #print("position log for ",ais_target,aisdata[ais_target])
                    l = position_log[ais_target]
                    l.append((sim_time,ais_target_loc[0],ais_target_loc[1]))
                    #print("l=",position_log[ais_target])
                    #print("AIS target",aisdata[ais_target].MMSI,"(",aisdata[ais_target].name,")","is at location",ais_target_loc)

                    name = aisdata[ais_target].MMSI
                    if aisdata[ais_target].name != None:
                        name = aisdata[ais_target].name
                
                    #doesn't work, write to a file instead
                    #openCPNMsg = openCPNOutput.fpros(name,ais_target_loc[0],ais_target_loc[1],0,0)
                    ##print(msg)
                    #openCPNOutput.write(name,loc[0],loc[1])
                    #openCPNOutput.send(openCPNMsg,("127.0.0.1",2000))
                
                    dist = readData.getDistance(ais_target_loc[0],ais_target_loc[1],msg.latitude,msg.longitude)
                    if dist < 100 and dist > 10:
                        print(sim_time,"near miss with",aisdata[ais_target].MMSI,"(",aisdata[ais_target].name,")")
                        near_miss = (sim_time,aisdata[ais_target].MMSI,msg.latitude,msg.longitude)
                        near_misses.append(near_miss)
                    elif dist <= 10:
                        print(sim_time,"collision with",aisdata[ais_target].MMSI,"(",aisdata[ais_target].name,")")
                        collision = (sim_time,aisdata[ais_target].MMSI,msg.latitude,msg.longitude)
                        collisions.append(collision)

                #transmit boat positions
                #transmitPositions()
    else:
        print(data_str,"doesn't start with a GPS string")

print("Collisions:")
print(collisions)

print("\n\n")

print("Near Misses:")
print(near_misses)


f = open("boatlog.gpx","w")

#<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><gpx version="1.1" creator="GPS Essentials - http://www.gpsessentials.com" xmlns="http://www.topografix.com/GPX/1/1"><trk><name>Track-130301-031021</name><desc>null</desc><number>11</number><trkseg><trkpt lat="52.399887" lon="-3.8696077"><ele>385.2</ele><speed>0.0</speed><time>2013-03-01T15:10:27Z</time></trkpt>
#<trkpt lat="52.399887" lon="-3.86959"><ele>384.6</ele><speed>0.0</speed><time>2013-03-01T15:11:06Z</time></trkpt>
#<trkpt lat="52.399902" lon="-3.8697505"><ele>396.3</ele><speed>0.70710677</speed><time>2013-03-01T15:12:54Z</time></trkpt>



f.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n");
f.write("<gpx version=\"1.1\" xmlns=\"http://www.topografix.com/GPX/1/1\">\n")


for mmsi in position_log:
    f.write("<trk>\n\t<name>%d</name>\n\t\t<trkseg>\n" % (mmsi))
    count = 0
    for data in position_log[mmsi]:
        #only log every 10th point to reduce output size
        if count % 10 == 0:
            timestamp=datetime.datetime.fromtimestamp(data[0]).strftime('%Y-%m-%dT%H:%M:%SZ')
            f.write("\t\t\t<trkpt lat=\"%f\" lon=\"%f\"><ele>0.0</ele><speed>0.0</speed><time>%s</time></trkpt>\n" % (data[1],data[2],timestamp))
        count += 1
    f.write("\t\t</trkseg>\n\t</trk>\n")

collision_count = 0
for c in collisions:
    f.write("\t\t<wpt lat=\"%f\" lon=\"%f\">\n" % (c[2],c[3]))
    f.write("\t\t\t<name>Collision %d</name>\n" % (collision_count))
    collision_count += 1
    timestamp = datetime.datetime.fromtimestamp(c[0]).strftime('%Y-%m-%dT%H:%M:%SZ')
    f.write("\t\t\t<cmt>Collision with %s (%s) at %s</cmt>\n",c[1],aisdata[c[1]].name,timestamp)
    
miss_count = 0
for m in near_misses:
    f.write("\t\t<wpt lat=\"%f\" lon=\"%f\">\n" % (m[2],m[3]))
    f.write("\t\t\t<name>Near Miss %d</name>\n" % (miss_count))
    collision_count += 1
    timestamp = datetime.datetime.fromtimestamp(m[0]).strftime('%Y-%m-%dT%H:%M:%SZ')
    f.write("\t\t\t<cmt>Near Miss with %s (%s) at %s</cmt>\n",m[1],aisdata[m[1]].name,timestamp)


f.write("</gpx>\n");
f.close()

