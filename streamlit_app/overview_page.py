import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import json
import db_config
from data_access_layer import DatabaseAccess, ContentAccess

class OverviewPage:
    def __init__(self, module_title) -> None:
        self.db = db_config.connect_db() # database connection
        self.db_dal = DatabaseAccess()
        self.cont_dal = ContentAccess()
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


    def start_learning_page(self, topic_index):
        """
        Updates the segment index and calls the function to render the correct page
        corresponding to the selected topic.
        """
        # Determine which segment has to be displayed for the selected topic
        segment_index = self.cont_dal.get_index_first_segment_in_topic(topic_index)

        # Change the segment index to the index corresponding to the selected topic
        self.db.users_2.update_one(
            {"username": st.session_state.username},
            {"$set": {f"progress.{st.session_state.selected_module}.learning.segment_index": segment_index}}
        )
        # Change the 'phase' from overview to learning to render the learning page
        st.session_state.selected_phase = 'learning'
    
    
    def is_topic_completed(self, topic_index, module):
        """
        Checks if the user made all segments for this topic.
        """
        topic_segment_indexes = self.cont_dal.get_topic_segment_indexes(module, topic_index)
        user_doc = self.db_dal.find_user_doc()
        progress_count = self.db_dal.fetch_progress_counter(module, user_doc)
        
        for index in topic_segment_indexes:
            print(index)
            print(f"Hier begint de progress count: {progress_count}")
            print(f"De waarde voor deze index {progress_count.get(index, None)}")
            if progress_count.get(index, None) == None:
                return False
        
        return True
    

    def render_topic_containers(self):
        """
        Renders the container that contains the topic title, start button,
        and theory and questions for one topic of the lecture.
        """
        module_name_underscored = st.session_state.selected_module.replace(' ', '_')        
        self.cont_dal.get_topics_list(module_name_underscored)

        for topic_index, topic in enumerate(self.cont_dal.topics_list):
            container = st.container(border=True)
            cols = container.columns([0.02, 6, 2])

            with cols[1]:
                # Check if user made all segments in topic
                if self.is_topic_completed(topic_index, module_name_underscored):
                    topic_status = '✅'
                else:
                    topic_status = '⬜'
                
                topic_title = topic['topic_title']
                st.subheader(f"{topic_index + 1}. {topic_title} {topic_status}")

            with cols[2]:
                # Button that starts the learning phase at the first segment of this topic
                st.button("Start", key=f"start_{topic_index + 1}", on_click=self.start_learning_page, args=(topic_index, ), use_container_width=True)


            with container.expander("Theorie & vragen"):
                for st.session_state.segment_index in topic['segment_indexes']:

                    self.cont_dal.get_segments_list(module_name_underscored)
                    if self.cont_dal.get_segment_type() == "theory":

                        # Create invisible container to cluster each infosegment with the corresponding question segment(s) and image
                        content_container = st.container()
                        content_cols = content_container.columns([1, 1])

                        with content_cols[0]:
                            title = self.cont_dal.get_segment_title()
                            text = self.cont_dal.get_segment_text()
                            # Write the theory contents
                            st.markdown(f'<p class="size-4">{title}</p>', unsafe_allow_html=True)
                            st.write(text)

                        with content_cols[1]:
                            self.cont_dal.get_segment_image_file_name()
                            if self.cont_dal.image_file_name != None:
                                image_path = self.cont_dal.get_image_path()
                                image_base64 = self.convert_image_base64(image_path)
                                image_html = f"""
                                    <div style='text-align: center; margin: 10px;'>
                                        <img src='data:image/png;base64,{image_base64}' alt='image can't load' style='max-width: 100%; max-height: 500px'>
                                    </div>"""
                                st.markdown(image_html, unsafe_allow_html=True)
                    
                    elif self.cont_dal.get_segment_type() == "question":
                        with content_cols[0]:
                            question = self.cont_dal.get_segment_question()
                            st.markdown(f'<p class="size-4-question">{question}</p>', unsafe_allow_html=True)
                            
                            # Render normal or MC answer
                            answer = self.cont_dal.get_segment_answer()
                            if answer != None:
                                st.write(f"_{answer}_")
                            else:
                                answers = self.cont_dal.get_segment_mc_answers()
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