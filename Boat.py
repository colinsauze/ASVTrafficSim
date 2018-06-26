class Boat(object):

#current position, where we are now including iterpolation
#position reports, list of reports of where boat has been/will be, latest report isn't necessarily where the boat is currently reported

    def __init__(self, MMSI):
        self.MMSI = MMSI
        self.positionReports = []
        self.name = None
        self.callsign = None
        self.width = 10.0
        self.length = 100.0
        self.position = 0.0
        self.AISClass = 'A'

    def setName(self,name):
        self.name = name
        
    def getName(self):
        return self.name
        
    def setCallsign(self,callsign):
        self.callsign = callsign
        
    def setWidth(self,width):
        self.width = width
        
    def setLength(self,length):
        self.length = length

    def setPosition(self,position):
        self.position = position
        
    def setAISClass(self,AISClass):
        #default size for class B boats is 10m long, 3m wide
        if AISClass == 'B':
            if self.width == 0.0 and self.length == 0.0:
                self.width = 3
                self.length = 10
        self.AISClass = AISClass

    def addPositionReport(self,positionReport):
        self.positionReports.append(positionReport)
    
    def getPositionReports(self):
        return self.positionReports

    def toJSON(self):
        return "{ 'mmsi': %s, 'name': %s, 'class' : %s, 'width': %f 'length': %f }" % (self.MMSI,self.name,self.AISClass,self.length,self.width)