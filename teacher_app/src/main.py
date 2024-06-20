import time
import random
import streamlit as st
from dotenv import load_dotenv
import os
import json
from openai import AzureOpenAI
from openai import OpenAI
from pymongo import MongoClient
import base64
from _pages.questions_overview import QuestionsFeedbackPage
from utils.openai_client import connect_to_openai
# import utils.db_config as db_config
# from data.data_access_layer import DatabaseAccess, ContentAccess
from datetime import datetime

# Must be called first
st.set_page_config(page_title="LearnLoop", layout="wide")

load_dotenv()


def render_overview_page():
    """
    Renders the page that shows all the subjects in a lecture, which gives the 
    student insight into their progress.
    """
    module_title = ' '.join(st.session_state.selected_module.split(' ')[1:])
    overview_page = QuestionsFeedbackPage(module_title)
    overview_page.render_page()

if __name__ == "__main__":
    st.session_state.selected_module = "1 Embryonale ontwikkeling"
    st.session_state.use_mongodb = True
    st.session_state.username = 'test_user_6'
    st.session_state.openai_client = connect_to_openai()
    render_overview_page()