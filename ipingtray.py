import pingparsing
import time
from datetime import datetime
import pystray
from pystray import Menu, MenuItem
from PIL import Image, ImageDraw, ImageFont


def exit_action(icon):
    icon.visible = False
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


def create_image(color,average_time, fsize,fcolor):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (16, 16), color)
    dc = ImageDraw.Draw(image)
    #dc.rectangle((width // 50, 50, width, height // 50), fill=color1)
    #dc.rectangle((100, height // 50, width // 50, height), fill=color2)
    dc.text((2,2),str(average_time), fill=fcolor, size=fsize)
    return image


def setup(icon):
    icon.visible = True
    
    ping_lost = 0
    total_ping_lost = 0
    
    
    while icon.visible:
        time.sleep(1)
        r = ping()
        received = r["received"]
        average_time = r["average_time"]

        if average_time == None:
            average_time = 3500

        if received and average_time < 25:
            print("Everything working fine", average_time, end='\r')
            icon.icon = create_image(good,int(average_time),10,white)
            ping_lost=0

        elif received and average_time > 25 and average_time < 100:
            print("Working but not optimal", average_time, end='\r')
            icon.icon = create_image(average,int(average_time),10,black)
            ping_lost=0

        elif received and average_time > 100 and average_time < 3000:
            print("Working but slow", average_time, end='\r')
            icon.icon = create_image(bad,int(average_time),4,white)
            ping_lost=0

        else:# not received:
            ping_lost+=1
            total_ping_lost+=1
            with open(filename, "a") as f:
                f.write(time.ctime() + " for: " + str(ping_lost) + ". Total ping lost: " + str(total_ping_lost)+ "\n")
            print("Not working at: ", time.ctime(), "Down for: ", str(ping_lost), " seconds. Total ping lost: " + str(total_ping_lost))
            icon.icon = create_image(down,"Down",10,white)
            #ping_lost = pinglost + ping_lost
        time.sleep(1)
        pass
    

def init_icon():
    icon = pystray.Icon('Network downtime detector')

    icon.menu = Menu(MenuItem('Exit', lambda : exit_action(icon)))

    icon.icon = create_image(down,"Start",12,white)

    icon.title = 'Network downtime detector'

    icon.run(setup)

good = "GREEN"
average = "YELLOW"
bad = "BLUE"
down = "RED"
white = "WHITE"
black = "BLACK"


filename = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

init_icon()