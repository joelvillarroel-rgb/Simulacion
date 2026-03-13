# app.py
# Simulación de Eventos Discretos (Sistema de Pacientes M/M/1)
# Archivo único listo para ejecutar en Streamlit

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Simulación de Eventos Discretos", layout="wide")

st.title("Simulación de Eventos Discretos – Sistema de Atención de Pacientes (M/M/1)")

st.markdown("""
Este programa implementa una **simulación de eventos discretos** para un sistema de colas con:

- Llegadas aleatorias de pacientes
- Un servidor (médico)
- Disciplina FIFO

El modelo corresponde a un sistema **M/M/1**.
""")

# -------------------------------------------------
# 1. DEFINICIÓN DEL MODELO
# -------------------------------------------------

st.header("1. Definición del Modelo de Simulación")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado del Sistema")
    st.write("""
    El estado del sistema está definido por:
    - Número de pacientes en el sistema
    - Estado del servidor (ocupado o libre)
    """)

    st.subheader("Eventos")
    st.write("""
    Los eventos que cambian el estado del sistema son:

    1. Llegada de paciente
    2. Fin de servicio (salida del paciente)
    """)

with col2:
    st.subheader("FEL – Future Event List")
    st.write("""
    La **FEL** es la lista de eventos futuros que el simulador debe procesar.

    En este modelo contiene:

    - Próxima llegada
    - Próximo fin de servicio
    """)

    st.subheader("Variables estadísticas acumulativas")
    st.write("""
    - Tiempo total de espera en cola
    - Tiempo total en el sistema
    - Número total de pacientes atendidos
    """)

# -------------------------------------------------
# 2. PARÁMETROS
# -------------------------------------------------

st.header("2. Parámetros del Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    n = st.slider("Número de pacientes", 10, 200, 10)

with col2:
    lambda_rate = st.number_input("Tasa de llegada λ", value=1.0)

with col3:
    mu_rate = st.number_input("Tasa de servicio μ", value=1.2)

np.random.seed(42)

# -------------------------------------------------
# 3. GENERACIÓN DE TIEMPOS
# -------------------------------------------------

interarrival = np.random.exponential(1 / lambda_rate, n)
service = np.random.exponential(1 / mu_rate, n)

arrival = np.cumsum(interarrival)

start_service = np.zeros(n)
end_service = np.zeros(n)
wait_queue = np.zeros(n)
time_system = np.zeros(n)

# -------------------------------------------------
# 4. SIMULACIÓN PASO A PASO
# -------------------------------------------------

for i in range(n):

    if i == 0:
        start_service[i] = arrival[i]
    else:
        start_service[i] = max(arrival[i], end_service[i - 1])

    end_service[i] = start_service[i] + service[i]

    wait_queue[i] = start_service[i] - arrival[i]

    time_system[i] = end_service[i] - arrival[i]

# -------------------------------------------------
# 5. TABLA DE SIMULACIÓN
# -------------------------------------------------

data = pd.DataFrame({
    "Paciente": range(1, n + 1),
    "Tiempo de llegada": arrival,
    "Tiempo de servicio": service,
    "Inicio de atención": start_service,
    "Fin de atención": end_service,
    "Tiempo en cola": wait_queue,
    "Tiempo en sistema": time_system
})

st.header("3. Simulación paso a paso")

st.dataframe(data, use_container_width=True)

# -------------------------------------------------
# 6. MÉTRICAS SIMULADAS
# -------------------------------------------------

st.header("4. Métricas Simuladas")

avg_wait = np.mean(wait_queue)
avg_system = np.mean(time_system)

col1, col2 = st.columns(2)

with col1:
    st.metric("Tiempo promedio en cola", round(avg_wait, 4))

with col2:
    st.metric("Tiempo promedio en sistema", round(avg_system, 4))

# -------------------------------------------------
# 7. RESULTADOS ANALÍTICOS
# -------------------------------------------------

st.header("5. Resultados Analíticos del Modelo M/M/1")

rho = lambda_rate / mu_rate

if rho < 1:

    Wq = rho / (mu_rate - lambda_rate)
    W = 1 / (mu_rate - lambda_rate)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Utilización ρ", round(rho, 4))

    with col2:
        st.metric("Wq teórico", round(Wq, 4))

    with col3:
        st.metric("W teórico", round(W, 4))

else:

    st.error("El sistema no es estable porque λ ≥ μ")

# -------------------------------------------------
# 8. COMPARACIÓN
# -------------------------------------------------

st.header("6. Comparación Simulación vs Analítico")

comparison = pd.DataFrame({
    "Métrica": ["Tiempo en cola", "Tiempo en sistema"],
    "Simulación": [avg_wait, avg_system],
    "Analítico": [Wq if rho < 1 else None, W if rho < 1 else None]
})

st.table(comparison)

# -------------------------------------------------
# 9. TRANSITORIO VS ESTACIONARIO
# -------------------------------------------------

st.header("7. Comportamiento Transitorio vs Estacionario")

st.markdown("""
**Comportamiento Transitorio**

Es el periodo inicial de la simulación donde el sistema aún no ha alcanzado estabilidad.
Durante esta fase los resultados pueden variar significativamente porque el sistema
parte vacío.

**Comportamiento Estacionario**

Es el estado en el que el sistema alcanza equilibrio estadístico.
Las métricas como el tiempo promedio en cola o en el sistema se estabilizan y
oscilan alrededor de un valor constante.
""")

st.success("Simulación completada correctamente")
