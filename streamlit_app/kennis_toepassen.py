from openai import OpenAI
import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

class KennisToepassen:
    def __init__(self):
        load_dotenv()
        st.set_page_config(page_title="Beeckestijn", page_icon="🔵", layout='centered', initial_sidebar_state='auto')
        self.client = self.connect_to_openai()
        self.default_vraag = "Leg uit welk model je zou kiezen (bijv. COBIT of ITIL) en hoe dit model zal bijdragen aan betere controle en efficiëntie binnen het bedrijf."
        self.default_rubric = "Ik zou het [gekozen IT Governance model, bijvoorbeeld COBIT of ITIL] kiezen omdat het duidelijke richtlijnen en principes biedt voor IT Governance (1 punt). De implementatiestappen omvatten het definiëren van governance-doelen, het in kaart brengen van huidige processen, en het toewijzen van verantwoordelijkheden (1 punt). Rollen zoals [specifieke rollen, bijvoorbeeld IT Governance Board en Risk Manager] zorgen voor een duidelijke verdeling van verantwoordelijkheden (1 punt). De effectiviteit wordt gemeten door KPI’s zoals [specifieke KPI’s, bijvoorbeeld IT-prestatiemetingen, compliance rates] (1 punt)."
        self.setup_sidebar()
        self.setup_session_state()
        self.render_app()

    def connect_to_openai(self):
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY_2"))

    def setup_sidebar(self):
        with st.sidebar:
            st.title('Fases')
            for phase in ["1\. Probleemstelling bepalen", "2\. College kijken", "3\. Kennis toepassen", "4\. Doel stellen", "5\. Implementeren"]:
                st.button(phase, use_container_width=True)

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

    def user_input(self):
        st.text_input("Wil je een andere vraag stellen? Vul die hier in.", key="nieuwe_vraag")
        st.text_input("Wat is de rubric voor die nieuwe vraag?", key="nieuwe_rubric")
        
        cols = st.columns(2)
        cols[0].button("Stel **nieuwe vraag** in", on_click=self.set_new_question, use_container_width=True)
        cols[1].button("Gebruik **standaard vraag**", on_click=self.set_default_question, use_container_width=True)

    def reset_chat(self):
        st.session_state.messages = []
        self.start_conversation()

    def render_app(self):
        # self.render_title()
        # self.user_input()
        st.title("IT governance modellen")
        st.write("""**Context**\n\n Stel je voor dat je werkt als IT-manager bij een middelgroot bedrijf dat recentelijk een significante groei heeft doorgemaakt. Het management heeft geconstateerd dat de huidige IT-processen en -structuren niet langer effectief zijn en vraagt jou om een IT Governance model te implementeren dat kan helpen bij het verbeteren van de efficiëntie en controle over IT-activiteiten.""")
        # st.success(f"\n\nDe huidige vraag is: **{st.session_state.vraag}** \n\n De rubric voor de vraag is: **{st.session_state.rubric}**")
        
        # st.button("Reset chat", on_click=self.reset_chat, use_container_width=True)

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
        with open("kennis_toepassen_prompt.txt", "r", encoding='utf-8') as file:
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
    
    def set_new_question(self):
        st.session_state.vraag = st.session_state.nieuwe_vraag
        st.session_state.rubric = st.session_state.nieuwe_rubric

    def set_default_question(self):
        st.session_state.vraag = self.default_vraag
        st.session_state.rubric = self.default_rubric
    

if __name__ == "__main__":
    KennisToepassen()
