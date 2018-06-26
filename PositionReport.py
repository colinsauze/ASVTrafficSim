 
class PositionReport(object):
    
    def __init__(self, time, lat, lon, cog, sog):
        self.time = time
        self.lat = lat
        self.lon = lon
        self.cog = cog
        self.sog = sog

    def __str__(self):
        return "Time: %d Lat: %f Lon: %f COG: %f SOG: %f" % (self.time,self.lat,self.lon,self.cog,self.sog)


