import paho.mqtt.client as mqtt
import threading
import time
import RPi.GPIO as GPIO

lightBuzzerStatus: int = 5
fanStatus: int = 0

GPIO_LIGHT: int = 18
GPIO_FAN: int = 17
GPIO_BUZZER: int = 12
SERVER_IP: str = "192.168.1.6"


def alertPatient():
    print("alert user")
    sound.ChangeFrequency(320)
    sound.ChangeDutyCycle(50)
    for i in range(2):
        time.sleep(0.3)

        GPIO.output(GPIO_LIGHT, GPIO.HIGH)
        print("Turning on LED light...")
        sound.start(50)

        time.sleep(0.3)

        GPIO.output(GPIO_LIGHT, GPIO.LOW)
        print("Turning off LED light...")
        sound.stop()
        
def run_interval():
    print("running interval")
    while True:
        # call the function
        alertPatient()
        # pause the program for the specified interval
        print(lightBuzzerStatus)
        time.sleep(lightBuzzerStatus)

def mainMenu():
    print("Current MQTT Server IP: " + SERVER_IP)
    print("Current GPIO Pin (Light): " + str(GPIO_LIGHT))
    print("Current GPIO Pin (Fan): " + str(GPIO_FAN))
    print("Current GPIO Pin (Buzzer): " + str(GPIO_BUZZER))
    command = int(input("Enter 1.Connect to MQTT, 2.Modify MQTT IP, 3.Modify GPIO Pins, 4.Terminate Program:"))
    if command == 4:
        print("Terminating...")
    elif command == 3:
        changeGPIO()
    elif command == 2:
        changeIPaddress()
    elif command == 1:
        GPIO.setmode(GPIO.BCM) #uses BCM way of numbering the GPIO pins
        GPIO.setup(GPIO_LIGHT, GPIO.OUT)
        GPIO.setup(GPIO_FAN, GPIO.OUT)
        GPIO.setup(GPIO_BUZZER, GPIO.OUT)
        global fan, sound, interval
        fan = GPIO.PWM(GPIO_FAN, 50)
        fan.start(0)
        sound = GPIO.PWM(GPIO_BUZZER, 100)

        interval = 5
        interval_thread = threading.Thread(target=run_interval)
        interval_thread.start()
        client.connect(SERVER_IP, 1883, 60)
        client.loop_forever()
    else:
        mainMenu()

def changeGPIO():
    global GPIO_FAN,GPIO_LIGHT
    selection = int(input("1.Fan GPIO, 2.Light GPIO"))
    gpioPin = int(input("Enter new GPIO Pin (0 to 27):"))
    if(gpioPin >= 0 and gpioPin <= 27):
        if(selection == 1):
            GPIO_FAN = gpioPin
            mainMenu()
        elif(selection == 2):
            GPIO_LIGHT = gpioPin
            mainMenu()
        else:
            changeGPIO()
    else:
        changeGPIO()

def changeIPaddress():
    global SERVER_IP
    ipAddr = int(input("Enter new IP address (x.x.x.x):"))
    SERVER_IP = ipAddr
    mainMenu()

def publishLightBuzzerStatus():
    global lightBuzzerStatus
    client.publish("Light/status", lightBuzzerStatus)
    print("Light status sent to server!")

def publishFanStatus():
    global fanStatus
    client.publish("Fan/status", fanStatus)
    print("Fan status sent to server!")

def controlLightBuzzer(desiredStatus: int):
    global lightBuzzerStatus
    lightBuzzerStatus = desiredStatus

    publishLightBuzzerStatus()
    
def controlFan(desiredStatus: int):
    global fanStatus
    fan_speed = 0
    if desiredStatus == 0:
        fan_speed = 0
    elif desiredStatus == 1:
        fan_speed = 40
    elif desiredStatus == 2:
        fan_speed = 70
    else:
        fan_speed = 100
    print(fan_speed)
    fan.ChangeDutyCycle(float(fan_speed))

def on_connect(client, userdata, flags, rc):
    client.subscribe("Light/control")
    client.subscribe("Fan/control")
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    if(msg.topic == "Light/control"):
        controlLightBuzzer(int(payload))
    elif(msg.topic == "Fan/control"):
        controlFan(int(payload))

client = mqtt.Client(client_id="Appliance-PI")

client.on_connect = on_connect
client.on_message = on_message

mainMenu()
# client.connect("192.168.1.3", 1883, 60)
# client.loop_forever()