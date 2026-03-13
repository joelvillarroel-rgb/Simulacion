import streamlit as st
import numpy as np
import pandas as pd
import math
import random

st.set_page_config(page_title="Simulación SED Clínica", layout="wide")

st.title("Simulación de Sistema de Colas - Clínica (M/M/1, M/G/1, M/M/2)")

st.sidebar.header("Parámetros del sistema")

lambda_rate = st.sidebar.number_input("Tasa de llegadas λ (pacientes por hora)", value=5.0, step=0.1)
service_minutes = st.sidebar.number_input("Tiempo promedio de servicio (minutos)", value=10.0)

mu = 60 / service_minutes

st.sidebar.write(f"μ calculado: {mu:.2f} pacientes/hora")

patients_small = st.sidebar.number_input("Pacientes simulación pequeña", value=20)
patients_large = st.sidebar.number_input("Pacientes simulación grande", value=100000)

st.header("1. Modelo Analítico M/M/1")

rho = lambda_rate / mu

if rho >= 1:
    st.error("Sistema inestable (ρ ≥ 1)")
else:
    L = rho / (1 - rho)
    Lq = rho**2 / (1 - rho)
    W = 1 / (mu - lambda_rate)
    Wq = rho / (mu - lambda_rate)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Utilización ρ", round(rho,3))
    col2.metric("L", round(L,3))
    col3.metric("Lq", round(Lq,3))
    col4.metric("Wq (horas)", round(Wq,3))

    st.metric("W (horas)", round(W,3))


st.header("2. Simulación de Eventos Discretos M/M/1")


def simulate_mm1(n, lam, mu):

    arrivals = []
    service = []
    start = []
    finish = []
    wait = []
    system = []

    current_time = 0
    last_finish = 0

    for i in range(n):

        interarrival = np.random.exponential(1/lam)
        arrival = current_time + interarrival

        service_time = np.random.exponential(1/mu)

        start_service = max(arrival, last_finish)
        finish_service = start_service + service_time

        wait_time = start_service - arrival
        system_time = finish_service - arrival

        arrivals.append(arrival)
        service.append(service_time)
        start.append(start_service)
        finish.append(finish_service)
        wait.append(wait_time)
        system.append(system_time)

        current_time = arrival
        last_finish = finish_service

    df = pd.DataFrame({
        "Llegada": arrivals,
        "Servicio": service,
        "Inicio Servicio": start,
        "Fin Servicio": finish,
        "Tiempo Cola": wait,
        "Tiempo Sistema": system
    })

    return df


if st.button("Simular 20 pacientes"):

    df_small = simulate_mm1(int(patients_small), lambda_rate, mu)

    st.subheader("Tabla simulación")
    st.dataframe(df_small)


st.header("3. Simulación grande (convergencia)")

if st.button("Simular 100,000 pacientes"):

    df_large = simulate_mm1(int(patients_large), lambda_rate, mu)

    Wq_sim = df_large["Tiempo Cola"].mean()
    W_sim = df_large["Tiempo Sistema"].mean()

    st.subheader("Comparación teoría vs simulación")

    results = pd.DataFrame({
        "Métrica": ["Wq", "W"],
        "Teórico": [Wq, W],
        "Simulación": [Wq_sim, W_sim]
    })

    st.table(results)


st.header("4. Hora pico (+15% llegadas)")

lambda_peak = lambda_rate * 1.15

if lambda_peak < mu:

    rho_peak = lambda_peak / mu
    W_peak = 1/(mu - lambda_peak)
    Wq_peak = rho_peak/(mu - lambda_peak)

    peak_df = pd.DataFrame({
        "Escenario": ["Normal", "Hora pico"],
        "λ": [lambda_rate, lambda_peak],
        "W": [W, W_peak],
        "Wq": [Wq, Wq_peak]
    })

    st.table(peak_df)


st.header("5. Modelo M/G/1 (Pollaczek-Khinchine)")

service_var = st.slider("Varianza del servicio", 0.1, 5.0, 1.0)

Es = 1/mu
Es2 = service_var + Es**2

Wq_mg1 = (lambda_rate * Es2) / (2 * (1 - rho))

st.write("Tiempo promedio de espera en cola (M/G/1):", Wq_mg1)


st.header("6. Modelo M/M/2")

s = 2


def mm2_metrics(lam, mu):

    rho = lam/(s*mu)

    sum_terms = sum([(lam/mu)**k / math.factorial(k) for k in range(s)])

    last_term = ((lam/mu)**s / math.factorial(s)) * (1/(1-rho))

    P0 = 1/(sum_terms + last_term)

    Lq = (P0*((lam/mu)**s)*rho)/(math.factorial(s)*(1-rho)**2)

    Wq = Lq/lam

    W = Wq + 1/mu

    return Wq, W


Wq2, W2 = mm2_metrics(lambda_rate, mu)

compare = pd.DataFrame({
    "Modelo": ["M/M/1", "M/M/2"],
    "Wq": [Wq, Wq2],
    "W": [W, W2]
})

st.table(compare)


st.header("7. Análisis económico")

cost_doctor = 40
cost_wait = 25

wait_cost_mm1 = Wq * lambda_rate * cost_wait
wait_cost_mm2 = Wq2 * lambda_rate * cost_wait

cost_total_mm1 = wait_cost_mm1
cost_total_mm2 = wait_cost_mm2 + cost_doctor

cost_df = pd.DataFrame({
    "Sistema": ["M/M/1", "M/M/2"],
    "Costo Espera": [wait_cost_mm1, wait_cost_mm2],
    "Costo Médico": [0, cost_doctor],
    "Costo Total": [cost_total_mm1, cost_total_mm2]
})

st.table(cost_df)


st.header("8. Explicación teórica")

st.write("""
Dos sistemas pueden tener el mismo tiempo promedio de servicio pero diferentes
varianzas. En sistemas de colas, la variabilidad afecta directamente el tiempo
promedio de espera.

La fórmula de Pollaczek–Khinchine muestra que Wq depende de E[S^2], no solo
E[S]. Si la varianza aumenta, E[S^2] aumenta y el tiempo de espera crece.

Por esta razón, dos sistemas con la misma media pueden producir colas
radicalmente distintas.
""")
