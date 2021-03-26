# import json
import pingparsing
import time
from datetime import datetime
import pystray
from PIL import Image, ImageDraw, ImageFont
import signal
import sys

def signal_handler(sig, frame,icon):
    sys.exit(0)
    icon.stop()



def ping():
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = "google.com"
    transmitter.count = 1
    result = transmitter.ping()
    # print(json.dumps(ping_parser.parse(result).as_dict(), indent=4))
    resultdict = ping_parser.parse(result).as_dict()
    results = dict()
    packet_received = bool
    if resultdict["packet_receive"] == 1:
        packet_received = True
    elif resultdict["packet_receive"] == None:
        packet_received = False

    if resultdict["rtt_avg"] == None:
        rtt_avg = 0
    else:
        rtt_avg = resultdict["rtt_avg"]

    res = {
        "received" : packet_received,
        "average_time" : resultdict["rtt_avg"]
        }
    return res

icon = pystray.Icon('Network downtime detector')

#width = 20
#height = 20
good = "GREEN"
average = "YELLOW"
bad = "BLUE"
down = "RED"
white = "WHITE"
black = "BLACK"

def create_image(color,average_time, fsize,fcolor):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (16, 16), color)
    dc = ImageDraw.Draw(image)
    #dc.rectangle((width // 50, 50, width, height // 50), fill=color1)
    #dc.rectangle((100, height // 50, width // 50, height), fill=color2)
    dc.text((2,2),str(average_time), fill=fcolor, size=fsize)
    return image

icon.icon = create_image(down,"Start",12,white)

global ping_lost
ping_lost = 0

def setup(icon):
    icon.visible = True
    global ping_lost
    time.sleep(1)
    
    while True:
        r = ping()
        received = r["received"]
        average_time = r["average_time"]

        if average_time == None:
            average_time = 3500
        if received and average_time < 25:
            print("Everything working fine", average_time, end='\r')
            icon.icon = create_image(good,int(average_time),10,white)
        
        elif received and average_time > 25 and average_time < 100:
            print("Working but not optimal", average_time, end='\r')
            icon.icon = create_image(average,int(average_time),10,black)
        elif received and average_time > 100 and average_time < 3000:
            print("Working but slow", average_time, end='\r')
            icon.icon = create_image(bad,int(average_time),4,white)
        else:# not received:
            f = open(filename,"a")
            print("Not working at: ", time.ctime(), "Down for: ", str(ping_lost), " seconds.")
            icon.icon = create_image(down,"Down",10,white)
            f.write(time.ctime() + "\n")
            f.close()
            ping_lost+=2
            #ping_lost = pinglost + ping_lost
        time.sleep(1)
        pass
    print("cerrando aca")
    f.close()

filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
icon.run(setup)
