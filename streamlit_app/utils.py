import streamlit as st
import json

class Utils:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def selected_module_json_name():
        return st.session_state.selected_module.replace(" ", "_")