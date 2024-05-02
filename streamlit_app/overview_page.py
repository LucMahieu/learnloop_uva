import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import json
import db_config
from utils import Utils

class OverviewPage:
    def __init__(self, module_title) -> None:
        self.db = db_config.connect_db() # database connection
        self.module_title = module_title

        
    def convert_image_base64(self, image_path):
        """
        Converts image in working dir to base64 format so it is 
        compatible with html.
        """
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


    def start_learning_page(self):
        """
        Updates the segment index and calls the function to render the correct page
        corresponding to the selected topic.
        """
        # Determine which segment has to be displayed for the selected topic
        segment_index = self.get_index_first_segment_in_topic()

        # Change the segment index to the index corresponding to the selected topic
        self.db.users.update_one(
            {"username": st.session_state.username},
            {"$set": {f"progress.{st.session_state.selected_module}.learning.segment_index": segment_index}}
        )
        # Change the 'phase' from overview to learning to render the learning page
        st.session_state.selected_phase = 'learning'
    

    def get_index_first_segment_in_topic(self):
        """
        Takes in the json index of a topic and extracts the first segment in the list of 
        segments that belong to that topic.
        """
        topics = self.get_topics()
        return topics[self.topic_index]['segment_indexes'][0]

    def get_segment_type(self):
        return self.segments_json['segments'][self.segment_index].get('type', None)

    def get_segment_question(self):
        return self.segments_json['segments'][self.segment_index].get('question', None)
        
    def get_segment_answer(self):
        return self.segments_json['segments'][self.segment_index].get('answer', None)

    def get_segment_title(self):
        return self.segments_json['segments'][self.segment_index]['title']
    
    def get_topics(self):
        return self.topics_json['topics']

    def get_segment_text(self):
        return self.segments_json['segments'][self.segment_index]['text']

    def get_segment_image_file_name(self):
        self.image_file_name= self.segments_json['segments'][self.segment_index].get('image', None)
        
    def get_image_path(self):
        return f"./images/{self.image_file_name}"

    def get_segment_mc_answers(self):
        return self.segments_json['segments'][self.segment_index]['answers']


    def render_topic_containers(self):
        """
        Renders the container that contains the topic title, start button,
        and theory and questions for one topic of the lecture.
        """
        module_json_name = Utils.selected_module_json_name()
        topics_json_path = f"./modules/{module_json_name}_topics.json"
        self.topics_json = Utils.load_json_content(topics_json_path)

        content_json_path = f"./modules/{module_json_name}.json"
        self.segments_json = Utils.load_json_content(content_json_path)

        for self.topic_index, topic in enumerate(self.get_topics()):
            container = st.container(border=True)
            cols = container.columns([0.02, 6, 2])

            with cols[1]:
                st.subheader(f"{self.topic_index + 1}. {topic['topic_title']} ✅") #TODO: now check is hardcoded, but this should be coupled to the progress of user.

            with cols[2]:
                # Button that starts the learning phase at the first segment of this topic
                st.button("Start", key=f"start_{self.topic_index + 1}", on_click=self.start_learning_page, use_container_width=True)

            with container.expander("Theorie & vragen"):
                for self.segment_index in topic['segment_indexes']:
                    print(self.segment_index)

                    if self.get_segment_type() == "info":

                        # Create invisible container to cluster each infosegment with the corresponding question segment(s) and image
                        content_container = st.container()
                        content_cols = content_container.columns([1, 1])

                        with content_cols[0]:
                            title = self.get_segment_title()
                            text = self.get_segment_text()
                            # Write the theory contents
                            st.markdown(f'<p class="size-4">{title}</p>', unsafe_allow_html=True)
                            st.write(text)

                        with content_cols[1]:
                            self.get_segment_image_file_name()
                            if self.image_file_name != None:
                                image_path = self.get_image_path()
                                image_base64 = self.convert_image_base64(image_path)
                                image_html = f"""
                                    <div style='text-align: center; margin: 10px;'>
                                        <img src='data:image/png;base64,{image_base64}' alt='image can't load' style='max-width: 100%; max-height: 500px'>
                                    </div>"""
                                st.markdown(image_html, unsafe_allow_html=True)
                    
                    elif self.get_segment_type() == "question":
                        with content_cols[0]:
                            question = self.get_segment_question()
                            st.markdown(f'<p class="size-4-question">{question}</p>', unsafe_allow_html=True)
                            
                            # Render normal or MC answer
                            answer = self.get_segment_answer()
                            if answer != None:
                                st.write(f"_{answer}_")
                            else:
                                answers = self.get_segment_mc_answers()
                                st.write(f"_{answers['correct_answer']}._")

        
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