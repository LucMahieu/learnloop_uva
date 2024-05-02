import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import json
import db_config

class OverviewPage():
    def __init__(self, module_title) -> None:
        self.db = db_config.connect_db() # database connection
        self.module_title = module_title

        
    def convert_image_base64(self, image_path):
        """Converts image in working dir to base64 format so it is 
        compatible with html."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
        
    
    def set_styling(self):
        st.markdown("""
            <style>
            .size-4 {
                font-size:20px !important;
                font-weight: bold;
            }
            .size-4-question {
                font-size: 16px !important;
                font-weight: bold;
                font-style: bold;
            </style>
            """, unsafe_allow_html=True)

        
    def render_title(self):
        container = st.container(border=True)
        header_cols = container.columns([0.1, 40])

        with header_cols[1]:
            st.title(self.module_title)
            st.write("\n")


    def start_learning_page(self, topic_index):
        """
        Updates the segment index and calls the function to render the correct page
        corresponding to the selected topic.
        """
        # Set the topic index as global variable to be accessed easily
        st.session_state.topic_index = topic_index

        # update 
        self.db.users.update_one(
            {"username": st.session_state.username},
            {"$set": {f"progress.{st.session_state.selected_module}.{st.session_state.selected_phase}.topic_{topic_index}.segment_index": 1}}
        )
        import main
        # Change the 'phase' from overview to learning to render the learning page
        st.session_state.selected_phase = 'learning'
        main.render_selected_page()


    def render_topic_containers(self):
        """
        Renders the container that contains the topic title, start button,
        and theory and questions for one topic of the lecture.
        """
        for i, topic_content in enumerate(st.session_state.page_content['topics']):
            container = st.container(border=True)
            cols = container.columns([0.02, 6, 2])

            with cols[1]:
                st.subheader(f"{i + 1}. {topic_content['topic_title']} ✅")

            with cols[2]:
                # Button that starts the learning phase at the first segment of this topic
                st.button("Start", key=f"start_{i + 1}", on_click=self.start_learning_page, args=(i,), use_container_width=True)

            with container.expander("Theorie & vragen"):
                content_container = st.container()
                content_cols = content_container.columns([1, 1])

                with content_cols[0]:
                    st.markdown('<p class="size-4">Belang van eiwitlokalisatie en -transport</p>', unsafe_allow_html=True)
                    st.write("Voor het correct functioneren van cellen is het van belang dat eiwitten nauwkeurig worden gepositioneerd, want de functie van eiwitten is vaak locatie-afhankelijk. Dit wordt bereikt door processen die zorgen voor eiwitlokalisatie en -transport binnen de cel.")
                    st.markdown('<p class="size-4-question">Waarom is eiwitlokalisatie belangrijk binnen de cel?</p>', unsafe_allow_html=True)
                    # st.markdown("Belang van eiwitlokalisatie en -transport")
                    st.write("_Eiwitlokalisatie is belangrijk omdat eiwitten specifieke functies uitvoeren die afhankelijk zijn van hun locatie binnen de cel (1 punt)._")
                    st.markdown('<p class="size-4-question">Waarom is eiwitlokalisatie belangrijk binnen de cel?</p>', unsafe_allow_html=True)
                    # st.markdown("Belang van eiwitlokalisatie en -transport")
                    st.write("_Eiwitlokalisatie is belangrijk omdat eiwitten specifieke functies uitvoeren die afhankelijk zijn van hun locatie binnen de cel (1 punt)._")

                with content_cols[1]:
                    image_base64 = self.convert_image_base64("./images/cam_camk.png")
                    image_html = f"""
                        <div style='text-align: center; margin: 10px;'>
                            <img src='data:image/png;base64,{image_base64}' alt='image can't load' style='max-width: 100%; max-height: 500px'>
                        </div>"""
                    st.markdown(image_html, unsafe_allow_html=True)


        
    def render_page(self):
        """
        Renders the overview page with the lecture title and the topics from the 
        lecture in seperate containers that allow the user to look at the contents
        and to select the topics they want to learn.
        """
        self.set_styling() # for texts

        self.render_title()
        # Spacing
        st.write("\n")

        self.render_topic_containers()