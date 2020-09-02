from orator import DatabaseManager
import datetime, os, pickle, statistics, calmap
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
from includes.calendarheatmap import Heatmap
from includes.geomap import Geomap
import matplotlib.cm as cm

os.chdir("YOUR DIRECTORY")


config = # DATABASE CONNECTION HERE


#### - LOADING THE DATA - ####

class DataLoader():
    def __init__(self, config):
        self.db = DatabaseManager(config)

    def getConnections(self):
        return self.db.table("bahn_monitoring_connections").where("active", "=", "0").get()

    def getPrices(self):
        return self.db.table("bahn_monitoring_prices").join('bahn_monitoring_connections', 'connection_id', '=', "bahn_monitoring_connections.id").get()

    def writeConnections(self):
        with open('connections.pkl', 'wb') as f:
            pickle.dump(self.getConnections(), f, pickle.HIGHEST_PROTOCOL)

    def writePrices(self):
        with open('prices.pkl', 'wb') as f:
            pickle.dump(self.getPrices(), f, pickle.HIGHEST_PROTOCOL)

    def readConnections(self):
        with open('connections.pkl', 'rb') as f:
            self.connections = pickle.load(f)

    def readPrices(self):
        with open('prices.pkl', 'rb') as f:
            self.prices = pickle.load(f)



dl = DataLoader(config)
dl.readPrices()
dl.readConnections()

#### - PLOTTING THE DATA - ####

class Plotter():
    def plotDataDaily(self):
        data_daily = {}

        for con in dl.connections:
            if con["starttime"].date() in data_daily:
                data_daily[con["starttime"].date()] += 1
            else:
                data_daily[con["starttime"].date()] = 1

        data_daily = sorted(data_daily.items())
        x, y = zip(*data_daily)

        self.plotBar(x,y,"Verbindungen pro Tag", rotate_x=True, plot_y="Anzahl an Verbindungen [-]")

    def plotBar(self, x, y, title, plot_y=False, line_width=1, rotate_x=False, fully_rotate_x=False, margin=0.5, height_scale=1.1):
        fig = plt.figure(figsize=(1.1*6.25984252,height_scale*3.12992126))
        ax1 = fig.add_subplot(1, 1, 1)
        plt.bar(x, y, line_width, color=(0.2,0.4,0.9,1))
        ax1.grid(which='major', axis='y', linewidth=0.71, linestyle='-', color='0.75')
        ax1.set_axisbelow(True)
        plt.title(title)
        if plot_y is not False:
            h=plt.ylabel(plot_y)
        fig.tight_layout()
        if rotate_x:
            plt.xticks(rotation=45, ha="right")
            plt.subplots_adjust(bottom=0.2)
        if fully_rotate_x:
            plt.xticks(rotation=90, ha="center")
            plt.subplots_adjust(bottom=margin)
        plt.show()
    
    def plotErrorbar(self, x, y, e, title, plot_y=False, rotate_x=False):
        fig = plt.figure(figsize=(1.1*6.25984252,1.1*3.12992126))
        ax1 = fig.add_subplot(1, 1, 1)
        plt.errorbar(x, y, e, color=(0.2,0.4,0.9,1), linestyle="None", marker="o", capsize=3)
        ax1.grid(which='major', axis='y', linewidth=0.71, linestyle='-', color='0.75')
        ax1.set_axisbelow(True)
        plt.title(title)
        if plot_y:
            h=plt.ylabel(plot_y)
        fig.tight_layout()
        if rotate_x:
            plt.xticks(rotation=45, ha="right")
            plt.subplots_adjust(bottom=0.2)
        plt.show()

    def multiplot(self, X, Y, title, plot_y=False, rotate_x=False, colors=False):
        fig = plt.figure(figsize=(1.1*6.25984252,1.1*3.12992126))
        ax1 = fig.add_subplot(1, 1, 1)
        for i in range(len(X)):
            if not colors:
                plt.plot(X[i], Y[i])
            else:
                plt.plot(X[i], Y[i], color=colors[i])
        ax1.grid(which='major', axis='y', linewidth=0.71, linestyle='-', color='0.75')
        ax1.set_axisbelow(True)
        plt.title(title)
        if plot_y:
            h=plt.ylabel(plot_y)
        fig.tight_layout()
        if rotate_x:
            plt.xticks(rotation=45, ha="right")
            plt.subplots_adjust(bottom=0.2)
        plt.show()


    def plotDataHourly(self):
        data_daily = {}

        for con in dl.connections:
            if con["starttime"].strftime("%H") in data_daily:
                data_daily[con["starttime"].strftime("%H")] += 1
            else:
                data_daily[con["starttime"].strftime("%H") ] = 1

        data_daily = sorted(data_daily.items())
        x, y = zip(*data_daily)

        self.plotBar(x,y,"Verbindungen pro Stunde", line_width=0.8, plot_y="Anzahl an Verbindungen [-]")
        print(len(dl.getConnections()))

    def plotDataWeekly(self):
        data_daily = {}

        for con in dl.connections:
            if con["starttime"].strftime("%w") in data_daily:
                data_daily[con["starttime"].strftime("%w")] += 1
            else:
                data_daily[con["starttime"].strftime("%w") ] = 1

        data_daily = sorted(data_daily.items())
        x, y = zip(*data_daily)

        self.plotBar(["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],y,"Verbindungen pro Wochentag", line_width=0.8, plot_y="Anzahl an Verbindungen [-]")
        print(len(dl.getConnections()))

p = Plotter()
#p.plotDataHourly()
#p.plotDataWeekly()


#### - STATISTICS - ####

class Statistics():
    def calcMultiAverage(self, days_to_departure):
        data = {}
        for d in days_to_departure:
            data[int(d)] = []
        for i in dl.prices:
            delta = int((i["starttime"]-i["time"]).total_seconds()/86400)
            if delta in days_to_departure and float(i["price"]) > 17.8 and float(i["price"]) < 200:
                data[delta].append(float(i["price"]))

        x = data.keys()
        y = []
        e = []
        for key, d in data.items():
            y.append(np.mean(d))
            e.append(statistics.stdev(d))

        p.plotErrorbar(x, y, e, "Durchschnittspreis nach Buchungstag", plot_y="Ticketpreis [€]")

        X = []
        Y = []
        for i in range(3):
            X.append(list(data.keys()))

        mi = []
        ma = []
        av = []
        for key, d in data.items():
            av.append(np.mean(d))
            mi.append(min(d))
            ma.append(max(d))
        Y.append(mi)
        Y.append(ma)
        Y.append(av)

        p.multiplot(X,Y, "Durchschnittspreis nach Buchungstag", colors=[(0.7,0.7,0.7,1), (0.7,0.7,0.7,1), (0.2,0.4,0.9,1)], plot_y="Ticketpreis [€]")

    def calcDailyHeatmap(self, departure_range):
        data = dl.prices
        series = {}
        for i in data:
            if int((i["starttime"]-i["time"]).total_seconds()/86400) >= departure_range[0] and int((i["starttime"]-i["time"]).total_seconds()/86400) <= departure_range[1]:
                
                if i["starttime"].date() in series:
                    series[i["starttime"]].append(i["price"])
                else:
                    series[i["starttime"]] = [i["price"]]

        single_series = {}
        
        h = Heatmap(series)
        m, lx = h.getMonths()

        m = np.ma.masked_where(m == -1, m)
        cmap = cm.Blues  # Can be any colormap that you want after the cm
        cmap.set_bad(color='black')
        fig = plt.figure(figsize=(1.1*6.25984252,0.8*3.12992126))
        ax = fig.add_subplot(1, 1, 1)
        plt.title("Ticketpreise nach Abfahrtstag")
        plot = plt.imshow(m, cmap=cmap)
        ax.set_yticks(range(len(lx)))
        ax.set_yticklabels(lx)
        ax.set_xticks([0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36])
        cbar = fig.colorbar(plot, ax=ax)
        cbar.set_label('Ticketpreis [€]', rotation=270,  labelpad=15)
        ax.set_xticklabels(["Mo", "Mi", "Fr", "So", "Di", "Do", "Sa", "Mo", "Mi", "Fr", "So","Di", "Do", "Sa", "Mo", "Mi", "Fr", "So", "Di" ])
        plt.show()

    def calcHourlyHeatmap(self, departure_range):
        data = dl.prices
        series = {}
        for i in data:
            if int((i["starttime"]-i["time"]).total_seconds()/86400) >= departure_range[0] and int((i["starttime"]-i["time"]).total_seconds()/86400) <= departure_range[1]:
                
                if i["starttime"].date() in series:
                    series[i["starttime"]].append(i["price"])
                else:
                    series[i["starttime"]] = [i["price"]]

        single_series = {}
        
        h = Heatmap(series)
        m, lx = h.getWeekdays()

        m = np.ma.masked_where(m == -1, m)
        cmap = cm.Blues  # Can be any colormap that you want after the cm
        cmap.set_bad(color='black')
        fig = plt.figure(figsize=(1.1*6.25984252,0.8*3.12992126))
        ax = fig.add_subplot(1, 1, 1)
        plt.title("Ticketpreise nach Uhrzeit")
        plot = plt.imshow(m, cmap=cmap)
        ax.set_yticks(range(len(lx)))
        ax.set_yticklabels(["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"])
        ax.set_xticks(range(24))
        cbar = fig.colorbar(plot, ax=ax)
        cbar.set_label('Ticketpreis [€]', rotation=270, labelpad=15)
        #ax.set_yticklabels(["Mo", "Mi", "Fr", "So", "Di", "Do", "Sa", "Mo", "Mi", "Fr", "So","Di", "Do", "Sa", "Mo", "Mi", "Fr", "So", "Di" ])
        plt.show()

    def calcStartstations(self, departure_range):
        cons = dl.connections
        prices = dl.prices
        stations_id = {}
        data_start = {}

        for price in prices:
            if int((price["starttime"]-price["time"]).total_seconds()/86400) >= departure_range[0] and int((price["starttime"]-price["time"]).total_seconds()/86400) <= departure_range[1] and price["price"] > 17.8 and price["price"] < 200:
                try:
                    if price["start"] in data_start:
                        data_start[price["start"]].append(price["price"])
                    else:
                        data_start[price["start"]] = [price["price"]]
                except Exception as e:
                    print(e)

        data = {}
        for d in data_start:
            if len(data_start[d]) > 10:
                data[d] = np.mean(data_start[d])
        data.pop("Brüssel Hbf", None)
        data={k: v for k, v in sorted(data.items(), key=lambda item: item[1])}

        p.plotBar(list(data.keys())[:10]+list(data.keys())[-10:], list(data.values())[:10]+list(data.values())[-10:], "Durchschnittspreis nach Startbahnhof", fully_rotate_x=True, line_width=0.8, plot_y="Ticketpreis [€]")

        m = Geomap(55.05864,47.271679,5.866944,15.043611,data)

    def calcEndstations(self, departure_range):
        cons = dl.connections
        prices = dl.prices
        stations_id = {}
        data_start = {}

        for price in prices:
            if int((price["starttime"]-price["time"]).total_seconds()/86400) >= departure_range[0] and int((price["starttime"]-price["time"]).total_seconds()/86400) <= departure_range[1] and price["price"] > 17.8 and price["price"] < 200:
                try:
                    if price["start"] in data_start:
                        data_start[price["end"]].append(price["price"])
                    else:
                        data_start[price["end"]] = [price["price"]]
                except Exception as e:
                    print(e)

        data = {}
        for d in data_start:
            if len(data_start[d]) > 10:
                data[d] = np.mean(data_start[d])
        data.pop("Brüssel Hbf", None)
        data={k: v for k, v in sorted(data.items(), key=lambda item: item[1])}

        p.plotBar(list(data.keys())[:10]+list(data.keys())[-10:], list(data.values())[:10]+list(data.values())[-10:], "Durchschnittspreis nach Endbahnhof", fully_rotate_x=True, line_width=0.8, plot_y="Ticketpreis [€]")

    def calcTracks(self, departure_range):
        cons = dl.connections
        prices = dl.prices
        stations_id = {}
        data_start = {}

        for price in prices:
            if int((price["starttime"]-price["time"]).total_seconds()/86400) >= departure_range[0] and int((price["starttime"]-price["time"]).total_seconds()/86400) <= departure_range[1] and price["price"] > 17.8 and price["price"] < 200:
                try:
                    if price["start"]+" - "+price["end"] in data_start:
                        data_start[price["start"]+" - "+price["end"]].append(price["price"])
                    elif price["end"]+" - "+price["start"] in data_start:
                        data_start[price["end"]+" - "+price["start"]].append(price["price"])
                    else:
                        data_start[price["start"]+" - "+price["end"]] = [price["price"]]
                except Exception as e:
                    print(e)

        data = {}
        for d in data_start:
            if len(data_start[d]) > 10:
                data[d] = np.mean(data_start[d])
        data={k: v for k, v in sorted(data.items(), key=lambda item: item[1])}

        p.plotBar(list(data.keys())[:10]+list(data.keys())[-10:], list(data.values())[:10]+list(data.values())[-10:], "Durchschnittspreis nach Verbindung", fully_rotate_x=True, line_width=0.8, margin=0.6, height_scale=1.8, plot_y="Ticketpreis [€]")


s = Statistics()
#s.calcMultiAverage(range(120))
#s.calcDailyHeatmap([30,40])
#s.calcHourlyHeatmap([30,40])
#s.calcStartstations([30,40])
#s.calcEndstations([3,7])
#s.calcTracks([3,7])