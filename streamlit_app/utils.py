import streamlit as st
import json

class Utils:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def selected_module_json_name():
        return st.session_state.selected_module.replace(" ", "_")

    @staticmethod
    def load_json_content(path): #TODO: This might result in a lot of memory usage, which is costly and slow
        """
        Load all the contents from the current JSON into memory.
        """
        with open(path, "r") as f:
            return json.load(f)