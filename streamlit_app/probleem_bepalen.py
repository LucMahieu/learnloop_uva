from openai import OpenAI
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Beeckestijn", page_icon="🔵", layout='centered', initial_sidebar_state='auto')

with st.sidebar:
    st.title('Fases')
    for phase in ["1\. Probleemstelling bepalen", "2\. College kijken", "3\. Kennis toepassen", "4\. Doel stellen", "5\. Implementeren"]:
        st.button(phase, use_container_width=True, )

def connect_to_openai():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY_2")
    )

client = connect_to_openai()

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Probleemstelling bepalen")
bedrijfsnaam = 'LearnLoop'
cursus = 'AI en data in business'

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
        st.markdown(message["content"])

if st.session_state.messages == []:
    intro_text = f"Laten we samen de probleemstelling bepalen. Wat is het probleem waar je tegenaan loopt met betrekking tot {cursus} bij {bedrijfsnaam}?"
    st.session_state.messages.append({"role": "assistant", "content": intro_text})
    with st.chat_message("assistant", avatar='🔵'):
        st.markdown(intro_text)

if prompt := st.chat_input("Jouw antwoord"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🔘'):
        st.markdown(f"{prompt}")


    with st.chat_message("assistant", avatar='🔵'):
        role_prompt = open("probleemstelling_prompt.txt").read() + f"\nBedrijf van persoon: {bedrijfsnaam}" + f"\nCursus van persoon: {cursus}"
        stream = client.chat.completions.create(
            model=st.session_state.openai_model,
            messages=[
                {"role": "system", "content": role_prompt},
                *({"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages)
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})