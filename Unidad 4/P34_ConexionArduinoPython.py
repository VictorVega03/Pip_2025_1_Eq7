import serial as controller
arduino = controller.Serial("COM", baudrate=9600, timeout=1)

while True:
    cadena = arduino.readLine().decode().string()
    if cadena != "":
        print(cadena)
