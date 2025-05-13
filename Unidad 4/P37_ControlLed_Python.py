import serial as controller
arduino = controller.Serial("COM", baudrate=9600, timeout=1)

while True:
    accion = input("Ingresa el valor de accion para el led: ")
    cadena = arduino.readLine().decode().strip()
    arduino.write(accion.encode())

