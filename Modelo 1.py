#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:08:05 2024

@author: mariaalonsobarciela
"""
#Modelo 1 
import pandas as pd
import pulp as lp

# Cargamos los datos
datosoperaciones = "241204_datos_operaciones_programadas.xlsx"
costes = "241204_costes.xlsx"

# Leemos los datos
operaciones_df = pd.read_excel(datosoperaciones)
costes_df = pd.read_excel(costes, index_col=0)

# Filtrar operaciones de Cardiología Pediátrica
operaciones_df = operaciones_df[operaciones_df["Especialidad quirúrgica"] == "Cardiología Pediátrica"]

# Conjuntos
I = list(operaciones_df["Código operación"])  # Operaciones
J = list(costes_df.index)  # Quirófanos

# Convertir las columnas de tiempo a datetime
operaciones_df["Hora inicio "] = pd.to_datetime(operaciones_df["Hora inicio "])
operaciones_df["Hora fin"] = pd.to_datetime(operaciones_df["Hora fin"])

# Parámetros de Costos
costeij = {(i, j): costes_df.at[j, i] for i in I for j in J}

# Creamos la matriz de incompatibilidades
Li = {}
for i in I:
    incompatibles = [] #creamos una lista vacía que almacenará las op. incompatibles con i 
    op_i = operaciones_df[operaciones_df["Código operación"] == i].iloc[0] #filtrar para obtener la fila correspondiente a la op i 
    for h in I:
        if i != h: # asegurar no comparar una operación consigo misma 
            op_h = operaciones_df[operaciones_df["Código operación"] == h].iloc[0] #filtrar para obtener la fila correspondiente a la op i 
            # Verificar solapamiento en el tiempo
            if not (op_i["Hora fin"] <= op_h["Hora inicio "] or op_h["Hora fin"] <= op_i["Hora inicio "]):
                incompatibles.append(h) # si hay solapamienyo se agrega a la lista de incompatibilidades
    Li[i] = incompatibles #asignar la lista incompatibles al diccionario Li

# Crear el modelo
problema = lp.LpProblem("Asignacion_Operaciones_Quirofanos", lp.LpMinimize)

# Variables de decisión
xij = lp.LpVariable.dicts("x", [(i, j) for i in I for j in J], cat="Binary")

# Función objetivo
problema += lp.lpSum(costeij[i, j] * xij[(i, j)] for i in I for j in J), "Coste_total"

# Restricción 1: Cada operación debe asignarse a un quirófano
for i in I:
    problema += lp.lpSum(xij[(i, j)] for j in J) == 1, f"Asigna_{i}"

# Restricción 2: Operaciones incompatibles no pueden estar en el mismo quirófano
for j in J:
    for i in I:
        for h in Li[i]:
            problema += xij[(i, j)] + xij[(h, j)] <= 1, f"Incompatibles_{i}_{h}_en_{j}"

# Resolver el modelo
problema.solve()

# Resultados
print("El estado del problema es: ", lp.LpStatus[problema.status])

if problema.status == 1:  # Solución óptima encontrada
    print("Costo mínimo:", lp.value(problema.objective))
    asignaciones = []
    for i in I:
        for j in J:
            if xij[(i, j)].value() == 1:
                asignaciones.append((i, j))
                print(f"Operación {i} asignada al quirófano {j}")

# Verificar el costo óptimo
print("El valor óptimo de la función objetivo es:", lp.value(problema.objective))