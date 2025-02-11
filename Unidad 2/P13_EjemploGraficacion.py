import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

# y = mx + b
x = [i for i in range(-5, 5+1, 1)]
print(x)

m = 3
b = 2

y = [i*m+b for i in x]
print(y)

plt.plot(x, y, marker="o", color='blue', linestyle='--', linewidth=2, markersize=8, markerfacecolor='green')

# Personalización de la gráfica
plt.title('Gráfica de y = mx + b')
plt.xlabel('Eje X')
plt.ylabel('Eje Y')
plt.grid(True)
plt.show()

# práctica 4....-> Probar otras maneras de personalizar el diseño de las graficas
# con matplotlib