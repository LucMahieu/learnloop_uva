from openai import OpenAI
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

class KennisToepassen:
    def __init__(self, vraag, rubric):
        load_dotenv()
        self.client = self.connect_to_openai()
        self.default_vraag = vraag
        self.default_rubric = rubric
        self.setup_session_state()
        self.render_question_chat()

    def connect_to_openai(self):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY_2"))
    
    def setup_session_state(self):
        if "openai_model" not in st.session_state:
            st.session_state["openai_model"] = "gpt-4o"
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "vraag" not in st.session_state:
            st.session_state.vraag = self.default_vraag
        if "rubric" not in st.session_state:
            st.session_state.rubric = self.default_rubric

    def render_title(self):
        st.title("Kennis toepassen")

    def reset_chat(self):
        st.session_state.messages = []
        self.start_conversation()

    def render_question_chat(self):
        if not st.session_state.messages:
            self.start_conversation()

        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar='🔵' if message["role"] == "assistant" else '🔘'):
                st.markdown(message["content"])

        if prompt := st.chat_input("Jouw antwoord"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar='🔘'):
                st.markdown(f"{prompt}")

            with st.chat_message("assistant", avatar='🔵'):
                response = self.get_response()
            st.session_state.messages.append({"role": "assistant", "content": response})

    def start_conversation(self):
        welcome_message = f"**{st.session_state.vraag}**"
        st.session_state.messages.append({"role": "assistant", "content": welcome_message})

    def get_response(self):
        with open("./src/utils/kennis_toepassen_prompt.txt", "r", encoding='utf-8') as file:
            role_prompt = file.read()

        role_prompt += f"\nDe vraag: {st.session_state.vraag}" + f"\nDe antwoordrubric voor de vraag: {st.session_state.rubric}"

        stream = self.client.chat.completions.create(
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

        return response
    

if __name__ == "__main__":
    KennisToepassen()
