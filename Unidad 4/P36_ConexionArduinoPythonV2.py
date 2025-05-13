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

from matplotlib import pyplot as plt
x = [i for i in range(len(datos))]
plt.plot(x, datos)
plt.show()