from singleton import Singleton
import os.path
import datetime

@Singleton
class logWriter:
    def __init__(self, filepath = None):
        if filepath == None:
            #if there is no defined filepath we will use this:
            # ~/simplerss_YYYY-MM-DD
            today = datetime.date.today()
            directory = os.path.expanduser('~')
            filename = "simplerss_{0}-{1}-{2}".format(today.year,str(today.month).zfill(2),str(today.day).zfill(2)) 
            filepath = os.path.join(directory,filename)

        self.filepath = filepath
        print("Writing logs to {0}".format(self.filepath))

    def write(self, content):
        f = open(self.filepath, 'a')
        today = datetime.datetime.today()
        year = today.year
        month = str(today.month).zfill(2)
        day = str(today.day).zfill(2)
        hour = str(today.hour).zfill(2)
        minute = str(today.minute).zfill(2)
        second = str(today.second).zfill(2)
        line = "({0}-{1}-{2} {3}:{4}:{5}) {6}\r\n".format(year,month,day,hour,minute,second,content)
        f.write(line)
        f.close()
