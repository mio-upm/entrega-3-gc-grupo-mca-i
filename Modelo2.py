# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 11:14:38 2024

@author: Usuario
"""
#PASO 1: Importar librerías
import pandas as pd
import pulp as lp

#PASO 2: Cargar datos del excel
costes=pd.read_excel("241204_costes.xlsx")
operaciones=pd.read_excel("241204_datos_operaciones_programadas.xlsx")
# Renombrar la columna "Unnamed: 0" a "Quirófano" para mayor claridad
costes.rename(columns={"Unnamed: 0": "Quirófano"}, inplace=True)

#PASO 3: Definir problema
problema=lp.LpProblem("Set_Covering_Quirofanos", lp.LpMinimize)

#PASO 4: Crear conjuntos
servicios=["Cardiología Pediátrica", "Cirugía Cardíaca Pediátrica", "Cirugía Cardiovascular", "Cirugía General y del Aparato Digestivo"]
operaciones_multiservicio=operaciones[operaciones["Especialidad quirúrgica"].isin(servicios)]
#Extraer las operaciones
operaciones1=operaciones_multiservicio["Código operación"].tolist()
#Verificar que todas las operaciones tienen costos en costes
operaciones1=[op for op in operaciones1 if op in costes.columns]
#Verificar que no faltan operaciones
if not operaciones1:
    raise ValueError("No hay operaciones válidas en costes después del filtrado.")

#PASO 5: Calcular los costos promedio para cada operación
costos_medios=costes.loc[:, operaciones1].mean()
#Quirófanos disponibles
n_quirofanos=costes.shape[0]
# Crear planificaciones factibles
planificaciones=[]
costes_planificaciones=[]
for quir in range(n_quirofanos):
    for i in range(1, 4):  # Tres planificaciones posibles por quirófano
        # Crear planificación factible
        planificacion = {op: 1 if idx % 3 == i-1 else 0 for idx, op in enumerate(operaciones1)}
        planificaciones.append(planificacion)
        # Calcular el costo total para esta planificación
        operaciones_incluidas = [op for op in operaciones1 if planificacion[op] == 1]
        costo_total = costos_medios[operaciones_incluidas].sum() if operaciones_incluidas else 0
        costes_planificaciones.append(costo_total)
#Convertir planificaciones a un DataFrame binario
Bik=pd.DataFrame(planificaciones, columns=operaciones1)
#Costes de cada planificación
Ck=costes_planificaciones  

#PASO 6:Definir variables de decisión
y=lp.LpVariable.dicts("y", range(len(planificaciones)), cat='Binary')

#PASO 7: Declarar función objetivo y restricciones
problema+=lp.lpSum(Ck[k]*y[k] for k in range(len(planificaciones)))
# Restricción 1:
for op in operaciones1:
    problema+=lp.lpSum(Bik[op][k]*y[k] for k in range(len(planificaciones)))>=1

#PASO 8: Resolver problema
problema.solve()
# Mostrar resultados
print("Estado:", lp.LpStatus[problema.status])
print("Coste total mínimo:", lp.value(problema.objective))
print("Planificaciones seleccionadas:")
for k in range(len(planificaciones)):
    if y[k].value() == 1:
        print(f"Planificación {k+1} seleccionada con coste {Ck[k]}")