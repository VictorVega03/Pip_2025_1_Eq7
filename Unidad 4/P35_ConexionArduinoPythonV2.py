import serial as controller
arduino = controller.Serial("COM", baudrate=9600, timeout=1)

datos = []
lectura = 0
tot_lectura = 25

while lectura < tot_lectura:
    cadena = arduino.readLine().decode().strip()
    if cadena != "":
        print(cadena)
        datos.append(cadena)
        lectura += 1

datos = [int(i) for i in datos]
print(datos)