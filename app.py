#!/usr/bin/python
#
#simple app to read string from serial port
#and publish via MQTT
#
#uses the Python MQTT client from the Mosquitto project
#http://mosquitto.org
#
#AMatthew Nichols http://mattnics.com
#2019/7/3




import serial,os,json
import xml.etree.ElementTree as ET
import paho.mqtt.publish as publish
import requests

serialdev = '/dev/ttyUSB0'
broker = "10.0.3.11"
port = 1883
emon_url="http://10.0.3.96:8080/input/post"
emon_api_key="021f0e3fec3956a6f1b1e5ac7d24bd71"

def cleanup():
    print ("Ending and cleaning up")
    ser.close()
    mqttc.disconnect()

# Connect Serial and bomb out if not connected

try:
    print ("Connecting... "), serialdev
    #connect to serial port
    ser = serial.Serial(serialdev, 57600, timeout=3)
except:
    print ("Failed to connect serial")
    #unable to continue with no serial input
    raise SystemExit

try:
    #read data from serial port
            while True:
                # Read the XML from serial
                line = ser.readline()
                line = line.decode('utf-8')
                #need to handle empty lines and the summary line
                if "watts" in line:
                    # Parse the XML to capture the temperature and the Power COnsuption from my sensor
                    root = ET.fromstring(line)
                    temp = root[3].text
                    power = root[7][0].text
                    print (temp+" "+power)
                    #Update MQTT with values
                    values = {
                        "temp":temp,
                        "power":power,
                        "power1":power
                    }
                    json_output = json.dumps(values)
                    publish.single("home/garage/powermeter", json_output, hostname=broker)
                    payload = {'node':'emonpi','fulljson':json_output,'apikey':emon_api_key}
                    #url = emon_url+json_output+"&apikey="+emon_api_key
                    #print (url)
                    print(payload)
                    try:
                        response =  requests.get(emon_url, params=payload)
                    except requests.exceptions.RequestException as e:  # This is the correct syntax
                        print (e)
                    

    
# handle list index error (i.e. assume no data received)
except (IndexError):
    print ("No data received within serial timeout period")
    cleanup()
# handle app closure
except (KeyboardInterrupt):
    print ("Interrupt received")
    cleanup()
except (RuntimeError):
    print ("uh-oh! time to die")
    cleanup()
