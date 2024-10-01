
from datetime import datetime
import traceback

file = f"_logs/log{datetime.now().strftime("%Y%m%d%H%M%S")}.txt"
fileex = f"_logs/logex{datetime.now().strftime("%Y%m%d%H%M%S")}.txt"

def init_log():
    global file
    global fileex
    
    file = f"_logs/log{datetime.now().strftime("%Y%m%d%H%M%S")}.txt"
    fileex = f"_logs/logex{datetime.now().strftime("%Y%m%d%H%M%S")}.txt"

def log(message):
    print(message)
    with open(file, 'a') as f:
        dateStr = datetime.now().strftime("%d/%m %H:%M") 
        f.write(dateStr + ' - ' + message + '\n')

def logex():
    with open(fileex, 'a') as f:
        dateStr = datetime.now().strftime("%d/%m %H:%M") 
        f.write(dateStr + ' - ' + traceback.format_exc() + '\n')