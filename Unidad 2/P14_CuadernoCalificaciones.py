archivo = open("../archivos/calificacionesConNombre.csv")
contenido = archivo.readlines()

print(contenido, "\n")

datos = [i.split(",") for i in contenido]

print(datos, "\n")

datos = [[i[0], list(map(int,i[1:])) ] for i in datos]

print(datos, "\n")

#calcular el promedio de cada alumno y agregar el resultado
# a la lista asociada al usuario

datos = [[ i[0], i[1] , sum(i[1])/len(i[1]) ] for i in datos]
print(datos, "\n")