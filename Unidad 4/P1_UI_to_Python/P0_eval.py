import matplotlib, math
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

cadena = "3+5/2"
a = eval(cadena)
print(a)

cadena = "math.pow(2,3)"
a = eval(cadena)
print(a)

valores_x = [i for i in range(-10,10, 1)]
y = "x**2"

valores_y = [eval(y) for x in valores_x]
print(valores_y)

plt.plot(valores_x, valores_y)
plt.show()