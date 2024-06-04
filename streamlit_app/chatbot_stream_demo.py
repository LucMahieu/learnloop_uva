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

def connect_to_openai():
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY_2")
    )

client = connect_to_openai()

st.title("Probleemstelling bepalen")

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "learnloop"

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🔘'):
        st.markdown(f"{prompt}")


    with st.chat_message("assistant", avatar='🔵'):
        role_prompt = open("probleemstelling_prompt.txt").read()
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


