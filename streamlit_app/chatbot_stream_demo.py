from openai import OpenAI
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# def connect_to_openai():
#     return AzureOpenAI(
#     api_key=os.getenv("OPENAI_API_KEY"),  
#     api_version="2024-03-01-preview",
#     azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
#     )

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

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "learnloop"

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Probleemstelling bepalen")

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
        st.markdown(message["content"])

if prompt := st.chat_input("Jouw antwoord"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🔘'):
        st.markdown(f"{prompt}")


    with st.chat_message("assistant", avatar='🔵'):
        # role_prompt = open("probleemstelling_prompt.txt").read()
        role_prompt = "Help de persoon met hun probleem."
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
    st.rerun()


