import json
import streamlit as st
import db_config

class ContentAccess:
    def __init__(self):
        pass

    def load_page_content_of_module_in_session_state(self, module):
        file_name = self.fetch_json_file_name_of_module(module)
        path = self.generate_json_path(file_name)
        st.session_state.page_content = self.load_json_content(path)

        return st.session_state.page_content

    def fetch_json_file_name_of_module(self, module):
        return module.replace(" ", "_") + ".json"

    def generate_json_path(self, json_name):
        return f"./content/modules/{json_name}"

    def load_json_content(self, path): #TODO: This might result in a lot of memory usage, which is costly and slow
        """Load all the contents from the current JSON into memory."""
        with open(path, "r") as f:
            return json.load(f)
    
    def get_topic_segment_indexes(self, module, topic_index):
        return self.get_topics_list(module)[topic_index]['segment_indexes']

    def get_topics_list(self, module):
        """
        Each module has two types of jsons. One with the content segments and
        one that stores how the segments are divided into topics. This function
        gets the last (topics) one.
        """
        topics_json_path = f"./content/topics/{module}_topics.json"
        return self.load_json_content(topics_json_path)['topics']


    def get_segments_list(self, module):
        """
        Each module has two types of jsons. One with the content segments and
        one that stores how the segments are divided into topics. This function
        gets the first (content segments) one.
        """
        content_json_path = f"./content/modules/{module}.json"
        return self.load_json_content(content_json_path)['segments']



class DatabaseAccess:
    def __init__(self):
        self.db = db_config.connect_db()

    def find_user_doc(self):
        return self.db.users_2.find_one({"username": st.session_state.username})

    def fetch_progress_counter(self, module):
        module = module.replace('_', ' ')
        user_doc = self.find_user_doc()
        progress_counter = user_doc.get('progress', {}).get(module, {}).get('learning', {}).get('progress_counter', None)
        return progress_counter
    
    def update_progress_counter(self, module, new_count):
        self.db.users_2.update_one(
            {"username": st.session_state.username},
            {"$set": {f"progress.{module}.learning.progress_counter.{st.session_state.segment_index}": new_count}}
        )

    def add_progress_counter(self, module, empty_dict):
        """
        Add the json to the database that contains the count of how
        many times the user answered a certain question.
        """
        self.db.users_2.update_one(
            {"username": st.session_state.username}, 
            {"$set": {f"progress.{module}.learning.progress_counter": empty_dict}}
        )  