from geopy.geocoders import Nominatim
import matplotlib.pylab as plt

class Geomap():
    def __init__(self, up, down, left, right, cities):
        loc = Nominatim(user_agent='myapplication')
        size=0.006
        self.box = ((left,right,down,up))
        ruh_m = plt.imread('PATH TO/map.jpg')
        fig, ax = plt.subplots(figsize = (1515*size,2000*size))
        for c in cities:
            try:
                coords = loc.geocode(c)
                if coords is not None:
                    #lowest = 40
                    #highest = 50 # for early booking
                    lowest = 33
                    highest = 36 # for late booking
                    s = 10000*((cities[c]-lowest)/highest)
                    c = (1*((cities[c]-lowest)/highest),1-1*((cities[c]-lowest)/highest),0,1)
                    ax.scatter(float(coords.raw["boundingbox"][2]),float(coords.raw["boundingbox"][1]), zorder=1, alpha= 0.8, c=[c], s=s)
            except:
                pass
        ax.set_title('Karte mit Durschnittspreisen der Startbahnhöfe')
        ax.set_xlim(self.box[0],self.box[1])
        ax.set_ylim(self.box[2],self.box[3])
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.imshow(ruh_m, zorder=0, extent = self.box, aspect= 'auto')
        fig.tight_layout()
        plt.show()

