import streamlit as st
import requests
from openai import OpenAI

# Configurazione della sidebar per le chiavi API
st.sidebar.title("Configurazione API")
openai_api_key = st.sidebar.text_input("Inserisci la chiave API di OpenAI", type="password")
openapi_api_key = st.sidebar.text_input("Inserisci la chiave API di OpenAPI", type="password")

# Inizializzazione del client OpenAI nel session state
if "openai_client" not in st.session_state:
    st.session_state.openai_client = None

if openai_api_key and st.session_state.openai_client is None:
    st.session_state.openai_client = OpenAI(api_key=openai_api_key)

def search_companies(ateco, fatturato_min, fatturato_max, provincia, num_risultati):
    url = "https://company.openapi.com/IT-search"
    headers = {"Authorization": f"Bearer {openapi_api_key}"}
    params = {
        "atecoCode": ateco,
        "minTurnover": fatturato_min,
        "maxTurnover": fatturato_max,
        "province": provincia,
        "limit": min(num_risultati, 1000)
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json().get('data', [])

def process_with_gpt4(data) -> str:
    if st.session_state.openai_client is None:
        st.error("Client OpenAI non inizializzato. Controlla la chiave API.")
        return ""

    prompt = f"Analizza e riassumi i seguenti dati sulle aziende in una tabella markdown: {data}"
    response = st.session_state.openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto in analisi di dati aziendali."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

st.title("Ricerca Aziende per Codice ATECO")

ateco = st.text_input("Codice ATECO (senza punti)", max_chars=6)
fatturato_min = st.number_input("Fatturato minimo", min_value=0)
fatturato_max = st.number_input("Fatturato massimo", min_value=0)
provincia = st.text_input("Provincia")
num_risultati = st.number_input("Numero di risultati (max 1000)", min_value=1, max_value=1000, value=10)

if st.button("Cerca"):
    if not openai_api_key or not openapi_api_key:
        st.error("Per favore, inserisci entrambe le chiavi API nella sidebar prima di procedere.")
    elif st.session_state.openai_client is None:
        st.error("Errore nell'inizializzazione del client OpenAI. Controlla la chiave API.")
    else:
        with st.spinner("Ricerca in corso..."):
            # Ricerca delle aziende
            results = search_companies(ateco, fatturato_min, fatturato_max, provincia, num_risultati)
            
            if results:
                # Elaborazione con GPT-4
                analysis = process_with_gpt4(results)
                
                # Visualizzazione dei risultati
                st.subheader("Analisi dei risultati")
                st.markdown(analysis)
                
                st.subheader("Dati grezzi")
                st.json(results)
            else:
                st.warning("Nessun risultato trovato. Prova a modificare i parametri di ricerca.")