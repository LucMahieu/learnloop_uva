import json
import streamlit as st
import db_config

class JsonDataAccess:
    def __init__(self, file_path):
        self.file_path = file_path
        self.response = self.load_response()


    def load_data(self):
        with open(self.file_path, 'r') as file:
            return json.load(file)

    def get_module_title(self):
        return self.data.get("module_name", "")

    def get_topics(self):
        return self.data.get("topics", [])

    def get_segments_for_topic(self, topic_index):
        topics = self.get_topics()
        if topic_index < len(topics):
            return topics[topic_index].get("segments", [])
        return []
    

class ContentAccess:
    def __init__(self):
        pass

    def load_json_content(self, path): #TODO: This might result in a lot of memory usage, which is costly and slow
        """
        Load all the contents from the current JSON into memory.
        """
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
        return self.db.users.find_one({"username": st.session_state.username})

    def fetch_progress_counter(self, module):
        user_doc = self.find_user_doc()
        progress_counter = user_doc.get('progress', {}).get(module, {}).get('learning', {}).get('progress_counter', None)
        print(f"Fetched progress_counter: {progress_counter}")
        return progress_counter
    
    def update_progress_counter(self, module, new_count):
        self.db.users.update_one(
            {"username": st.session_state.username},
            {"$set": {f"progress.{module}.learning.progress_counter.{st.session_state.segment_index}": new_count}}
        )

    def add_progress_counter(self, module, empty_dict):
        """
        Add the json to the database that contains the count of how
        many times the user answered a certain question.
        """
        self.db.users.update_one(
            {"username": st.session_state.username}, 
            {"$set": {f"progress.{module}.learning.progress_counter": empty_dict}}
        )  