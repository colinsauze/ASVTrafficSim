import os
import ais.stream
import json
import ais.compatibility.gpsd
import time
import math

from Boat import Boat
from PositionReport import PositionReport



#returns the coordinates of a point a given distance and bearing from an origin point
def projectPoint(bearing,dist,lat1,lon1):
	'''
	dist = distance in metres 
	'''
	#d = angular distance covered on earth's surface
	
	
	dist = dist / 1000.0
	dist = dist/6367.0

	lat1 = math.radians(lat1)
	lon1 = math.radians(lon1)
	bearing = math.radians(bearing)

	lat2 = math.asin( math.sin(lat1)*math.cos(dist) + math.cos(lat1)*math.sin(dist)*math.cos(bearing) )
	lon2 = lon1 + math.atan2(math.sin(bearing)*math.sin(dist)*math.cos(lat1), math.cos(dist)-math.sin(lat1)*math.sin(lat2))

	if (math.isnan(lat2) or math.isnan(lon2)):
		return None
		
	#print("projecting %f,%f by %f on a heading of %f = %f,%f" % (math.degrees(lat1),math.degrees(lon1),dist*6367,math.degrees(bearing),math.degrees(lat2),math.degrees(lon2)))
	destpos = (math.degrees(lat2),math.degrees(lon2))
	return destpos

#gets the great circle course between two points 
def getCourse(lat1,lon1,lat2,lon2):
    
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)    
    
    heading = math.degrees(math.atan2(math.sin(lon2-lon1)*math.cos(lat2), math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(lon2-lon1)))
    
    #make headings between 0 and 360 not -180 and +180
    if(heading<0):
        heading = heading + 360

    return heading


#gets the great circle distance between two points 
def getDistance(lat1,lon1,lat2,lon2 ):
    
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.pow(math.sin(dlat/2),2) + math.cos(lat1) * math.cos(lat2) * math.pow(math.sin(dlon/2),2)
    d = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
    #halfway between equatorial radius (6378km) and polar radius(6357km)
    dist = 6367.0 * d

    return dist * 1000.0

def read_data(filename):
	now = 0
	boats = dict()

	with open(filename) as inf:
		for msg in ais.stream.decode(inf):

			# static information messages with boat length/width
			# unfortunately we have no data with these to verify this code
			if msg['id'] == 19 or msg['id'] == 5:
				#probably should store the reference point for more accurate collision detection
				boats[msg['mmsi']].setLength(int(msg['dim_a']) + int(msg['dim_b']))
				boats[msg['mmsi']].setWidth(int(msg['dim_c']) + int(msg['dim_d']))
				print(msg)

			# make an entry for this boat if it hasn't already got one
			if msg['mmsi'] not in boats:
				b = Boat(msg['mmsi'])
				boats[msg['mmsi']] = b

			# name updates
			if msg['id'] == 24:
				b = boats[msg['mmsi']]
				# set a name if we haven't got one already
				if 'name' in msg and b.getName() == None:
					# strip @ characters which some boats leave in remaining space
					b.setName(msg['name'].replace('@', ''))

			# get full timestamp from base stations
			if msg['id'] == 4 or msg['id'] == 11:
				timestamp = time.mktime((msg['year'], msg['month'], msg['day'], msg['hour'], msg['minute'], msg['second'], -1, -1, 0))
				now = timestamp

			# wait until we get one full valid timestamp
			if now < 1417000000:
				continue

			if 'timestamp' in msg and (int(msg['timestamp']) > 0 and int(msg['timestamp']) < 60):
				t = time.gmtime(now)

			# timestamp only contains seconds, if its less than our last full timestmap assume its in the next minute
				if msg['timestamp'] < t.tm_sec:
					now = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min+1, 0, -1, -1, 0))

				now = time.mktime((t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, int(msg['timestamp']), -1, -1, 0))         

			# position reports, both class A and B
			if (msg['id'] >= 1 and msg['id'] <= 3) or  msg['id'] == 18 or msg['id'] == 19:
				p = PositionReport(now, msg['y'], msg['x'], msg['cog'], msg['sog'])
				boats[msg['mmsi']].addPositionReport(p)

				# note if its a class B
				if(msg['id'] == 18 or msg['id'] == 19):
					boats[msg['mmsi']].setAISClass("B")

	return boats

# collision check algorithm
# get current time from simulator

# for each boat
# find most recent position report
# if first report doesn't exist yet ignore boat
# if report isn't at current time step project position forward based on last location, speed and heading
# update position info
# do collision check

def getCurrentLocation(timestamp,mmsi,boats):
	'''
	Gets the projected location for a boat at a given time
	'''
	b = boats[mmsi]
	#print(b.toJSON())
	reports = b.getPositionReports()
	min_diff = 9999999
	min_diff_index = -1
	#print("there are",len(reports),"positions available between",reports[0].time,"and",reports[len(reports)-1].time)
	
	for i in range(0,len(reports)):
		p = reports[i]
		time_diff = p.time - timestamp 
		#print("report",i,"timestamp = ",p.time,"diff=",time_diff)
		if time_diff < abs(min_diff):
			min_diff = time_diff
			min_diff_index = i
	#print("min_diff_index=",min_diff_index)

	if min_diff_index == -1:
		return None

	#print("nearest report for",mmsi,"at time",timestamp,"is at",reports[min_diff_index].time,"difference=",min_diff,"lat=",reports[min_diff_index].lat,"lon=",reports[min_diff_index].lon)
	if abs(min_diff) < 3600:
		#edge case, before the first report
		#project back along back azimuth of the COG
		if min_diff_index == 0:
			#print("first point")
			sog_ms = reports[min_diff_index].sog * 0.51444
			back_cog = (reports[min_diff_index].cog + 180) % 360
			return projectPoint(back_cog, sog_ms * abs(min_diff), reports[min_diff_index].lat, reports[min_diff_index].lon)

		#edge case, after last report 
		#project forward along the COG
		if min_diff_index == len(reports)-1:
			#print("last point sog=",reports[min_diff_index].sog,"cog=", reports[min_diff_index].cog)
			sog_ms = reports[min_diff_index].sog * 0.51444
			return projectPoint(reports[min_diff_index].cog, sog_ms * abs(min_diff), reports[min_diff_index].lat, reports[min_diff_index].lon)

		#cheating a bit by relying on having future data here, if we used realtime data we'd just have to project along COG at SOG

		if min_diff == 0:
			#print("Dead on, using report lat/lon")
			return ( reports[min_diff_index].lat ,  reports[min_diff_index].lon)
		#percent_covered=0.0
		#negative diff means report is before the time we want, position we want lies between this point and the next
		#md        timestamp        md+1 
		if min_diff<0:
			#print("our timestamp is after nearest one")
			lat1 = reports[min_diff_index].lat 
			lon1 = reports[min_diff_index].lon
			lat2 = reports[min_diff_index+1].lat 
			lon2 = reports[min_diff_index+1].lon
			time_diff = reports[min_diff_index+1].time - reports[min_diff_index].time
			#example, md = 10,  ts=15 md+1 = 20       (15 - 10) =5    / (20-10) = 10 0.5
			#example, md = 10,  ts=17 md+1 = 20       (17 - 10) =7    / (20-10) = 10 0.7
			percent_covered =  float(timestamp - reports[min_diff_index].time) / float(reports[min_diff_index+1].time - reports[min_diff_index].time)
			#print("percent_covered=",float(percent_covered),type(percent_covered))

		#positive diff means report is after the time we want, position we want lies between this point and the previous one
		#md-1    timestamp      md
		elif min_diff>0:
			#print("our timestamp is before nearest one")
			lat1 = reports[min_diff_index-1].lat 
			lon1 = reports[min_diff_index-1].lon
			lat2 = reports[min_diff_index].lat 
			lon2 = reports[min_diff_index].lon
			time_diff = reports[min_diff_index].time - reports[min_diff_index-1].time
			#example, md-1 = 10,  ts=15 md = 20       (15 - 10) =5    / (20-10) = 10 0.5
			#example, md-1 = 10,  ts=17 md = 20       (17 - 10) =7    / (20-10) = 10 0.7
			percent_covered =  float(timestamp - reports[min_diff_index-1].time) / float(reports[min_diff_index].time - reports[min_diff_index-1].time)

		#print("percent_covered=",percent_covered)
		course = getCourse(lat1,lon1,lat2,lon2)
		full_distance = getDistance(lat1,lon1,lat2,lon2)
		#print("full distance = ",full_distance,"lat1=",lat1,"lat2=",lat2,"lon1=",lon1,"lon2=",lon2)
		used_distance = full_distance * percent_covered
		return projectPoint(course,used_distance,lat1,lon1)
		
	else:
		#print("no report within an hour, assume target has gone")
		return None


def getFirstLast():
	'''gets the timestamps of the first and last reports'''
	boats = read_data("data/feed_short.ais.txt")

	for b in boats:
		#print(boats[b].toJSON())
		if len(boats[b].getPositionReports()) > 1:
			print("first",boats[b].getPositionReports()[0].time)
			last = len(boats[b].getPositionReports())-1
			print("last",boats[b].getPositionReports()[last].time)
