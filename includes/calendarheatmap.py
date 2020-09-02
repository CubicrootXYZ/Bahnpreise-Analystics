import matplotlib.pylab as plt
import datetime, calendar
import numpy as np



class Heatmap():
    def __init__(self, data):
        self.data = data

    def makePlots(self):
        pass

    def getMonths(self):
        months = {}
        for date, value in self.data.items():
            month = date.strftime("%Y.%m")
            day = date.strftime("%#d")
            #print(month)
            if month in months:
                if day in months[month]:
                    months[month][day].append(value)
                else:
                    months[month][day] = [value]
            else:
                months[month] = {}
                months[month][day] = [value]
        x_labels = months.keys()
        #months = sorted(months)
        print(x_labels)
        hmap = np.zeros((len(months), 38))
        l = -1
        for i in months:
            l+=1
            first_weekday, num_days_in_month = calendar.monthrange(int(i.split(".")[0]), int(i.split(".")[1]))
            #first_weekday=1
            hmap[l,0:first_weekday] = -1
            hmap[l,first_weekday+num_days_in_month:] = -1
            
            for j in range(31):
                try:
                    if len(months[i][str(j+1)]) > 10:
                        hmap[l,j+first_weekday] = np.mean(months[i][str(j+1)])
                except Exception as e:
                    print(e)
                    pass

        return hmap, x_labels


    def getWeekdays(self):
        months = {}
        for date, value in self.data.items():
            month = date.strftime("%w")
            day = date.strftime("%#H")
            if day == "23":
                
            if month in months:
                if day in months[month]:
                    months[month][day].append(value)
                    
                else:
                    months[month][day] = [value]
            else:
                months[month] = {}
                months[month][day] = [value]
    
        months2={}
        for l in ["1","2","3","4","5","6","0"]:
            months2[l] = months[l]
        months = months2
        x_labels = months.keys()
        print(x_labels)
        hmap = np.zeros((7,24))
        l = -1
        for i in months:
            l+=1
            
            for j in range(24):
                print(j)
                try:
                    if len(months[i][str(j)]) > 10:
                        hmap[l,j] = np.mean(months[i][str(j)])
                except Exception as e:
                    print(e)
                    pass

        return hmap, x_labels

