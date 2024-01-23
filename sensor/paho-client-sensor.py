import paho.mqtt.client as mqtt
import time
import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT11(board.D4)
temperature: float = 0.0
humidity: float = 0.0
GPIO_TEMPSENSOR: int = 4
SERVER_IP: str = "192.168.1.6"

def mainMenu():
    print("Current MQTT Server IP: " + SERVER_IP)
    print("Current GPIO Pin: " + str(GPIO_TEMPSENSOR))
    command = int(input("Enter 1.Connect to MQTT, 2.Modify MQTT IP, 3.Modify GPIO Pin, 4.Terminate Program:"))
    if command == 4:
        print("Terminating...")
    elif command == 3:
        changeGPIO()
    elif command == 2:
        changeIPaddress()
    elif command == 1:
        client.connect(SERVER_IP, 1883, 60)
        client.loop_start()
        publishTemperature()
    else:
        mainMenu()
        client.loop_stop()

def changeGPIO():
    global GPIO_TEMPSENSOR
    gpioPin = int(input("Enter new GPIO Pin (0 to 27):"))
    if(gpioPin >= 0 and gpioPin <= 27):
        GPIO_TEMPSENSOR = gpioPin
        mainMenu()
    else:
        changeGPIO()

def changeIPaddress():
    global SERVER_IP
    ipAddr = int(input("Enter new IP address (x.x.x.x):"))
    SERVER_IP = ipAddr
    mainMenu()

def publishTemperature():
    global temperature, humidity
    while True:
        try:
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            client.publish("Temperature/status", str(temperature)+","+str(humidity))
            print("Temp: {:.1f} C Humidity: {}%".format(temperature, humidity))
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(10)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
        finally:
            time.sleep(10)

def controlTempSensor(status: bool):
    if status:
        print("Switching on temperature sensor...")
    else:
        print("Switching off temperature snseor...")

def on_connect(client, userdata, flags, rc):
    client.subscribe("Temperature/control")
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    if(msg.topic == "Temperature/control"):
        controlTempSensor(int(payload))

client = mqtt.Client(client_id="Sensor-PI")

client.on_connect = on_connect
client.on_message = on_message

mainMenu()



# while True:
#     currTime = time.localtime()
#     if currTime.tm_hour >= 19 and currTime.tm_hour < 22:
#         client.publish("Time/status", "Lights up")
#     else:
#         client.publish("Time/status", "Lights out")
#     time.sleep(3600)