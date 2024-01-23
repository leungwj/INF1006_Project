from flask import Flask, request, render_template, jsonify
import paho.mqtt.client as mqtt
import time

# To start project, run the following command:
# flask --app app.py --debug run / python3 app.py

app = Flask(__name__)

auto = { "Fan" : 
            {
                26.0 : 0,
                27.0 : 3,
                35.0 : 2,
                40.0 : 3
            }, 
        "Light" : {
                64800 : 1
        }}

def changeIPaddress():
    global SERVER_IP
    ipAddr = input("Enter new IP address (x.x.x.x):")
    SERVER_IP = ipAddr

def setFanStatus(client: mqtt.Client, desiredStatus: int):
    global environment_readings
    client.publish("Fan/control", desiredStatus)
    print("Sending command to set fan speed to: " + desiredStatus)

def setLightStatus(client: mqtt.Client, desiredStatus: int):
    client.publish("Light/control", desiredStatus)
    print("Sending command to set light brightness to: " + desiredStatus)

def setTempSensorStatus(client: mqtt.Client, desiredStatus: bool):
    client.publish("Temperature/control", int(desiredStatus))
    print("Sending command to set temperature sensor's status to: " + int(desiredStatus))

def updateLightStatus(status: int):
    global lightStatus
    lightStatus = status
    updateWebpage()

def updateFanStatus(status: int):
    global fanStatus
    fanStatus = status
    updateWebpage()

def updateTempSensorStatus(status: str):
    global tempSensorStatus
    tempSensorStatus = status
    updateWebpage()

def processTemperature(reading: str):
    global environment_readings
    print(reading)
    environment_readings.append([round(time.time() * 1000), float(reading.split(",")[0]), float(reading.split(",")[1])])
    if fanStatus == 4:
        for temperature in sorted(auto["Fan"].keys()):
            if float(reading.split(",")[0]) < temperature:
                setFanStatus(auto["Fan"][temperature])
                break
    else:
        updateWebpage()
        
def updateWebpage():
    global lightStatus,fanStatus,environment_readings
    pass

#when i connect, this is what i will do
def on_connect(client, userdata, flags, rc):
    client.subscribe("Temperature/status") #subscribe to this message area to see if any clients posted a message
    client.subscribe("Light/status")
    client.subscribe("Fan/status")
    client.subscribe("TemperatureSensor/status")
    client.subscribe("$SYS/broker/clients/connected") #subscribe to the event of clients connecting to my broker
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    if(msg.topic == "Light/status"):
        print("Received LED Light brightness: " + payload)
        updateLightStatus(int(payload))
    elif(msg.topic == "Fan/status"):
        print("Received Fan speed: " + payload)
        updateFanStatus(int(payload))
    elif(msg.topic == "TemperatureSensor/status"):
        print("Received Temp Sensor status: " + payload)
        updateTempSensorStatus(str(payload))
    elif(msg.topic == "Temperature/status"):
        processTemperature(str(payload))
    elif(msg.topic == "$SYS/broker/clients/connected"):
        print(payload + "has connected!")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Data
actuator_data = { 'fan': 0, 'light': 0 }
lightStatus: int = 0
fanStatus: int = 0
tempSensorStatus: str = 0
SERVER_IP: str = "192.168.1.6"
new_reading: list[float] = [0.0, 0.0]
environment_readings: list[list[float]] = []

@app.route('/', methods = ["GET", "POST"])
def index():
    return render_template('index.html')

@app.route('/environment_tracker', methods = ["GET", "POST"])
def environment_tracker():
    return render_template('environment_tracker.html', data=environment_readings[-10:])

@app.route('/patient_control', methods = ["GET", "POST"])
def patient_control():
    return render_template('patient_control.html', data=actuator_data)

@app.route('/fan', methods=['POST'])
def handle_fan_request():
    global client, fanStatus
    fan_status = request.form['fan']
    # Do something with fan_status, e.g. turn a fan on or off
    response_data = {'status': 'success', 'message': f'Fan turned {fan_status}'}

    if fan_status != 4:
        setFanStatus(client, fan_status)

    return jsonify(response_data)

@app.route('/light', methods=['POST'])
def handle_light_request():
    global client, lightStatus
    light_status = request.form['light']
    # Do something with light_status, e.g. turn a light on or off
    response_data = {'status': 'success', 'message': f'Light turned {light_status}'}
    setLightStatus(client, light_status)
    return jsonify(response_data)

if __name__ == "__main__":        # on running python app.py
    client.connect(SERVER_IP, 1883, 60)
    client.loop_start()
    app.run(host='192.168.1.6', port='8080', debug='true') # run the flask app
    