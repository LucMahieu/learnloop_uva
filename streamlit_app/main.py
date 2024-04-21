import time
import random
import base64
import streamlit as st
import json

from dotenv import load_dotenv
import os

from openai import AzureOpenAI

from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

import pandas as pd
# import matplotlib.pyplot as plt # No longer needed (only for old render insights function) # TODO: remove this and function when no longer needed
import plotly.graph_objects as go
import textwrap

# Used to mitigate rate limit errors for OpenAI calls
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception


# Must be called first
st.set_page_config(page_title="LearnLoop", layout="wide")
load_dotenv()


def connect_to_openai():
    return AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  
    api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )


def connect_to_database():
    """
    Connect to either MongoDB or CosmosDB and ping to check connection.
    """
    if not use_mongodb:
        COSMOS_URI = os.getenv('COSMOS_URI')
        db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
    else:
        MONGO_URI = os.getenv('MONGO_DB')
        db_client = MongoClient(MONGO_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    db = db_client.LearnLoop

    # Ping database to check if it's connected
    try:
        db.command("ping")
        print("Connected to database")
    except Exception as e:
        print(f"Error: {e}")

    return db


def upload_progress():
    """
    Uploads the progress of the user in the current phase to the database.
    """
    # Store path and data in variables for clarity
    path = f"progress.{st.session_state.selected_module}.{st.session_state.selected_phase}"
    data = {f"{path}.segment_index": st.session_state.segment_index}

    # Also upload the ordered_segment_sequence if the practice session if active
    if st.session_state.selected_phase == 'practice':
        data[f"{path}.ordered_segment_sequence"] = st.session_state.ordered_segment_sequence
    
    # The data dict contains the paths and data
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": data}
    )


def notify_user_about_retry(retry_state):
    """
    When the OpenAI call results in an error, the user is notified with a
    message.
    """
    st.warning(f"Het evalueren is niet goed gelukt, maar de LLM probeert binnen een paar seconden poging {retry_state.attempt_number + 1}.")


@retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(lambda ex: True),
        before_sleep=notify_user_about_retry
    )
def evaluate_answer():
    """Evaluates the answer of the student and returns a score and feedback."""
    if use_dummy_openai_calls != True:
        
        # Create user prompt with the question, correct answer and student answer
        prompt = f"""Input:\n
        Vraag: {st.session_state.segment_content['question']}\n
        Studentantwoord: {st.session_state.student_answer}\n
        Correcte antwoord: {st.session_state.segment_content['answer']}
        Antwoordmodel: {st.session_state.segment_content['answer_items']}\n
        Output:\n"""

        # Read the role prompt from a file
        with open("./direct_feedback_prompt_5.txt", "r", encoding="utf-8") as f:
            role_prompt = f.read()

        response = openai_client.chat.completions.create(
            model="learnloop",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=6000
        )

        response = response.choices[0].message.content

        json_response = json.loads(response)
    
    else:
        question = st.session_state.segment_content['question'].replace('.', '')
        # Create dummy response for current question to test
        json_response = {
            f"{question}": [
                {
                    "score": 1.0,
                    "feedback": "✅ Correct: fotosynthese is een <strong>proces waarbij planten zonlicht omzetten in energie</strong>."
                },
                {
                    "score": 0.0,
                    "feedback": "❌ Onvolledig: vermeld dat <strong>koolstofdioxide en water omgezet worden in glucose en zuurstof</strong>."
                }
            ]
        }

    # Turn into JSON and select the current question
    question = st.session_state.segment_content['question']
    feedback_response = json_response[question]

    # Reset the session states
    st.session_state.feedback = []
    st.session_state.score = []

    # Add each item to the feedback and score lists
    for feedback_item in feedback_response:
        st.session_state.score.append(feedback_item['score'])
        st.session_state.feedback.append(feedback_item['feedback'])

    return feedback_response


def render_feedback():
    """Renders the feedback box with the score and feedback."""
    part = sum(st.session_state.score)
    total = len(st.session_state.score)
    score_percentage = int(part / total * 100)

    st.session_state.score_percentage = score_percentage

    # Determine color of box based on score percentage
    if score_percentage > 75:
        color = 'rgba(0, 128, 0, 0.2)'  # Green
    elif score_percentage > 49:
        color = 'rgba(255, 165, 0, 0.2)'  # Orange
    else:
        color = 'rgba(255, 0, 0, 0.2)'  # Red

    feedback_items = [f"<li style='font-size: 17px; margin: 5px 0; margin-top: 10px'>{feedback}</li>" for feedback in st.session_state.feedback]
    feedback_html = f"<ul style='padding-left: 0px; list-style-type: none;'>{''.join(feedback_items)}</ul>"

    result_html = f"""
    <h1 style='font-size: 20px; margin: 25px 0 10px 10px; padding: 0;'>Feedback:</h1>
    {feedback_html}
    <div style='background-color: {color}; padding: 10px; margin-bottom: 15px; margin-top: 28px; border-radius: 7px; display: flex; align-items: center;'> <!-- Verhoogd naar 50px voor meer ruimte -->
        <h1 style='font-size: 20px; margin: 8px 0 8px 10px; padding: 0;'>Score: {int(part)}/{total}</h1>
        <p style='margin: -30px; padding: 0;'>⚠️ Kan afwijken</p>
    </div>
    """
    st.markdown(result_html, unsafe_allow_html=True)


def render_progress_bar():
    # Change style of progressbar
    progress_bar_style = """
    <style>
    /* Change main container */
    .stProgress > div > div > div {
        height: 20px;
        border-radius: 30px;
    }
    /* Change moving part of progress bar */
    .stProgress .st-bo {
        height: 20px;
        border-radius: 30px;
    }
    </style>
    """
    st.markdown(progress_bar_style, unsafe_allow_html=True)

    phase_length = determine_phase_length()
    # Initialise progress bar or update progress that indicates the relative segment index
    if phase_length > 0:
        progress = int(((st.session_state.segment_index + 1) / phase_length * 100))
    else:
        progress = 0

    # Update the progress bar
    st.progress(progress)
    st.session_state.progress = progress


def re_insert_question(interval):
    """Copies a question that the user wants to repeat and re-insert it
    in the list that contains the segment sequence. The interval determines
    how many other questions it takes for the question to be displayed again."""
    new_pos = st.session_state.segment_index + interval

    # Make sure the new position fits in the segment sequence list
    list_length = len(st.session_state.ordered_segment_sequence)
    if new_pos > list_length:
        new_pos = list_length

    # Read value of current index that corresponds to the json index
    json_index = st.session_state.ordered_segment_sequence[st.session_state.segment_index]

    # Insert the segment in new position
    st.session_state.ordered_segment_sequence.insert(new_pos, json_index)

    change_segment_index(1)    


def render_SR_nav_buttons():
    col_prev, col1, col2, col3, col_next = st.columns([1.8, 3, 3, 3, 1.8])
    with col_prev:
        st.button('Vorige', use_container_width=True, on_click=lambda: change_segment_index(-1))
    with col1:
        st.button('Herhaal snel ↩️', use_container_width=True, on_click=re_insert_question, args=(5,))
    with col2:
        st.button('Herhaal later 🕒', use_container_width=True, on_click=re_insert_question, args=(15,))
    with col3:
        st.button('Got it ✅', use_container_width=True, on_click=lambda: change_segment_index(1))
    with col_next:
        st.button('Volgende', use_container_width=True, on_click=lambda: change_segment_index(1))


def render_explanation():
    with st.expander("Antwoordmodel"):
        st.markdown(st.session_state.segment_content['answer'])


def determine_phase_length():
    if st.session_state.selected_phase == 'practice':
        return len(st.session_state.ordered_segment_sequence)
    else:
        return len(st.session_state.page_content["segments"])


def change_segment_index(step_direction):
    """Change the segment index based on the direction of step (previous or next)."""
    # Determine total length of module
    phase_length = determine_phase_length()
    # 
    if st.session_state.segment_index + step_direction in range(phase_length):
        st.session_state.segment_index += step_direction
    # If we are at the last page, we need to go to the final screen.
    elif st.session_state.segment_index == phase_length - 1:
        st.session_state.segment_index = 100_000
    else:
        st.session_state.segment_index = phase_length - 1

    # Prevent evaluating aswer when navigating to the next or previous segment
    st.session_state.submitted = False
    
    # Set the shuffled answers to None in case a new multiple choice question comes up
    st.session_state.shuffled_answers = None

    # Update database with new index
    upload_progress()


def render_navigation_buttons():
    """Render the navigation buttons that allows users to move between segments."""
    prev_col, next_col = st.columns(2)
    if st.session_state.segment_index != 0:
        with prev_col:
            st.button("Vorige", on_click=change_segment_index, args=(-1,), use_container_width=True)
    with next_col:
        st.button("Volgende", on_click=change_segment_index, args=(1,), use_container_width=True)


def set_submitted_true():
    """Whithout this helper function the user will have to press "check" button twice before submitting"""
    st.session_state.submitted = True


def render_check_and_nav_buttons():
    """Renders the previous, check and next buttons when a question is displayed."""
    col_prev_question, col_check, col_next_question = st.columns([1, 3, 1])
    if st.session_state.segment_index != 0:
        with col_prev_question:
            st.button('Vorige', use_container_width=True, on_click=change_segment_index, args=(-1,))
    with col_check:
        if st.session_state.user_type == 'student':
            st.button('Controleer', use_container_width=True, on_click=set_submitted_true)
        else:
            st.button('Genereer inzicht', use_container_width=True, on_click=set_submitted_true)
    with col_next_question:
        st.button('Volgende', use_container_width=True, on_click=change_segment_index, args=(1,))


def render_image(image_path):
    image_base64 = convert_image_base64(image_path)
    image_html = f"""
    <div style='text-align: center; margin: 10px;'>
        <img src='data:image/png;base64,{image_base64}' alt='image can't load' style='max-width: 100%; max-height: 500px'>
    </div>"""
    st.markdown(image_html, unsafe_allow_html=True)


def fetch_image_path():
    if 'image' in st.session_state.segment_content:
        image_path = st.session_state.segment_content['image']
        if image_path is None:
            return None
        else:
            return f"./images/{image_path}"


def render_info():
    """Renders the info segment with title and text."""
    # if the image directory is present in the JSON for this segment, then display the image
    image_path = fetch_image_path()
    if image_path:
        render_image(image_path)

    st.subheader(st.session_state.segment_content['title'])
    st.write(st.session_state.segment_content['text'])


def render_answerbox():
    # if the image directory is present in the JSON for this segment, then display the image
    # Render a textbox in which the student can type their answer.
    st.text_area(label='Your answer', label_visibility='hidden', 
                placeholder="Type your answer",
                key='student_answer'
    )
    

def render_question():
    """Function to render the question and textbox for the students answer."""
    st.subheader(st.session_state.segment_content['question'])


def fetch_ordered_segment_sequence():
    """Fetches the practice segments from the database."""
    user_doc = db.users.find_one({"username": st.session_state.username})
    st.session_state.ordered_segment_sequence = user_doc["progress"][st.session_state.selected_module]["practice"]["ordered_segment_sequence"]


def update_ordered_segment_sequence(ordered_segment_sequence):
    """Updates the practice segments in the database."""
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": {f"progress.{st.session_state.selected_module}.practice.ordered_segment_sequence": ordered_segment_sequence}}
    )


def add_to_practice_phase():
    """
    Adds the current segment to the practice phase in the database if the score is lower than 100.
    """
    if st.session_state.score_percentage < 100:
        fetch_ordered_segment_sequence()
        # Store in variable for clarity
        ordered_segment_sequence = st.session_state.ordered_segment_sequence
        segment_index = st.session_state.segment_index

        if segment_index not in ordered_segment_sequence:
            ordered_segment_sequence.append(segment_index)

        # Update practice segments in db
        update_ordered_segment_sequence(ordered_segment_sequence)


def render_student_answer():
    student_answer = f"""
    <h1 style='font-size: 20px; margin: 15px 0 10px 10px; padding: 0;'>Jouw antwoord:</h1>
    <div style='background-color: #F5F5F5; padding: 20px; border-radius: 7px; margin-bottom: 0px;'>
        <p style='color: #333; margin: 0px 0'>{st.session_state.student_answer}</p>
    </div>
    """
    st.markdown(student_answer, unsafe_allow_html=True)


def fetch_segment_index():
    """Fetch the last segment index from db"""
    user_doc = db.users.find_one({"username": st.session_state.username})
    return user_doc["progress"][st.session_state.selected_module][st.session_state.selected_phase]["segment_index"]


def render_start_button():
    """Start button at the beginning of a phase that the user never started."""
    st.button("Start", use_container_width=True, on_click=change_segment_index, args=(1,))


def render_learning_explanation():
    """Renders explanation of learning phase if the user hasn't started with
    the current phase."""
    with mid_col:
        st.markdown('<p style="font-size: 30px;"><strong>Leerfase 📖</strong></p>', unsafe_allow_html=True)
        # st.write("The learning phase **guides you through the concepts of a lecture** in an interactive way with **personalized feedback**. Incorrectly answered questions are automatically added to the practice phase.")
        st.write("In de leerfase word je op een interactieve manier door de concepten van een college heen geleid en krijg je **direct persoonlijke feedback** op open vragen. Vragen die je niet goed hebt, komen automatisch terug in de oefenfase.")
        render_start_button()
    exit()


def initialise_learning_page():
    """
    Sets all session states to correspond with database.
    """
    # Fetch the last segment index from db
    st.session_state.segment_index = fetch_segment_index()

    if st.session_state.segment_index == -1: # If user never started this phase
        render_learning_explanation()
    elif st.session_state.segment_index == 100_000: # if we are at the final screen
        render_final_page()
    else:
        # Select the segment (with contents) that corresponds to the saved index where the user left off
        st.session_state.segment_content = st.session_state.page_content['segments'][st.session_state.segment_index]
        reset_submitted_if_page_changed()


def reset_segment_index():
    st.session_state.segment_index = 0
    upload_progress()
    

# render the page at the end of the learning phase (after the last question)
def render_final_page():
    
    with mid_col:
        if st.session_state.selected_phase == 'practice':
            st.markdown('<p style="font-size: 30px;"><strong>Einde van de oefenfase 📝</strong></p>', unsafe_allow_html=True)
            st.write("Hoe ging het? Als je het gevoel hebt dat je nog wat meer wilt oefenen met de vragen, kun je altijd terugkeren naar het begin van de oefenfase.")
        else:
            st.markdown('<p style="font-size: 30px;"><strong>Einde van de leerfase 📖</strong></p>', unsafe_allow_html=True)
            st.write("Lekker bezig! Als je nog een keer alle vragen en infostukjes wilt doorlopen, kun je terug naar het begin van de leerfase. Als je verder wilt naar de **oefenfase** waarin je kan gaan oefenen met de vragen waarmee je moeite had, kan je deze selecteren aan de linkerkant van het scherm.")

        st.button("Terug naar begin", on_click=reset_segment_index)
    
    # otherwise the progress bar and everything will get rendered
    exit()


def set_warned_true():
    """Callback function for a button that turns of the LLM warning message."""
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": {"warned": True}}
    )
    st.session_state.warned = True


def reset_progress():
    """Resets the progress of the user in the current phase to the database."""
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": {f"progress.{st.session_state.selected_module}.{st.session_state.selected_phase}.segment_index": -1}}
    )


def render_warning():
    st.markdown("""
        <div style="color: #987c37; background-color: #fffced; padding: 20px; margin-bottom: 20px; border-radius: 10px;">
            Door zometeen op <strong>'controleer'</strong> te klikken, laat je het antwoord dat je ingevuld hebt controleren door een large language model (LLM). Weet je zeker dat je door wil gaan?
        </div>
        """,
        unsafe_allow_html=True
    )
    st.button("Nee", on_click=reset_progress, use_container_width=True)
    st.button("Ja", use_container_width=True, on_click=set_warned_true)
    st.button("Leer meer over mogelijkheden & limitaties van LLM's", on_click=set_info_page_true, use_container_width=True)


def feedback_is_in_correct_format(feedback_items):
    """
    The format of the feedback needs to correspond to the answermodel. 
    Otherwise it can't be aggregated for the feedback insights.
    """
    # Count number of points to be scored
    answer_item_count = len(st.session_state.segment_content['answer_items'])
    feedback_item_count = len(feedback_items)

    # Compare elemnent counts
    if answer_item_count != feedback_item_count:
        st.warning("De feedback kan niet worden opgeslagen door een systeemfout en zal daarom ook niet gebruikt worden voor het inzicht op het collegescherm. Dat gaan we nog fixen ;)")
        return False
    else:
        return True


def save_feedback_to_db(feedback_items):
    """
    After submitting an answer, the student recieves LLM feedback.
    This function saves that feedback to the database and is 
    tied to the question and module.
    """
    module = st.session_state.selected_module
    # Remove dots because db query is dot sensitive
    question = st.session_state.segment_content['question'].replace('.', '')

    if feedback_is_in_correct_format(feedback_items):
        feedback_path = f"progress.{module}.feedback.{question}"
        db.users.update_one(
            {"username": st.session_state.username},
            {"$set": {feedback_path: feedback_items}}
        )


def render_learning_page():
    """
    Renders the page that takes the student through the concepts of the lecture
    with info segments and questions. The student can navigate between segments
    and will get personalized feedback on their answers. Incorrectly answered
    questions are added to the practice phase.
    """
    initialise_learning_page()

    # Display the info or question in the middle column
    with mid_col:
        render_progress_bar()

        # Determine what type of segment to display and render interface accordingly
        if st.session_state.segment_content['type'] == 'info':
            render_info()
            render_navigation_buttons()

        # Open question
        if (st.session_state.segment_content['type'] == 'question' and 
        'answer' in st.session_state.segment_content):
            if st.session_state.submitted:

                # Render image if present
                image_path = fetch_image_path()
                if image_path:
                    render_image(image_path)

                render_question()

                # Spinner that displays during evaluating answer
                with st.spinner(f"Een large language model (LLM) checkt je antwoord met het antwoordmodel. \
                                Check zelf het antwoordmodel als je twijfelt. \n\n Leer meer over het gebruik \
                                van LLM's op de pagina **'Uitleg mogelijkheden & limitaties LLM's'** onder \
                                het kopje 'Extra info' in de sidebar."):
                    render_student_answer()
                    feedback_response = evaluate_answer()
                                        
                render_feedback()
                save_feedback_to_db(feedback_response)
                add_to_practice_phase()
                render_explanation()
                render_navigation_buttons()
            else:
                image_path = fetch_image_path()
                if image_path:
                    render_image(image_path)
                
                render_question()

                if st.session_state.warned == False:
                    render_warning()
                else:
                    render_answerbox()
                
                # Becomes True if user presses ctrl + enter to evaluate answer (instead of pressing "check")
                if st.session_state.student_answer:
                    set_submitted_true()
                    st.rerun()
                
                if st.session_state.warned == True:
                    render_check_and_nav_buttons()
            
        
        # Multiple choice question
        if (st.session_state.segment_content['type'] == 'question' and
             'answers' in st.session_state.segment_content):
            render_question()

            correct_answer = st.session_state.segment_content['answers']['correct_answer']
            wrong_answers = st.session_state.segment_content['answers']['wrong_answers']
            
            # Check if the answers have already been shuffled and stored
            if st.session_state.shuffled_answers == None:
                answers = [correct_answer] + wrong_answers
                random.shuffle(answers)
                st.session_state.shuffled_answers = answers
            else:
                answers = st.session_state.shuffled_answers
                
            if 'choosen_answer' not in st.session_state:
                st.session_state.choosen_answer = None
                
            # Create a button for each answer
            for i, answer in enumerate(answers):
                st.button(answer, key=f"button{i}", use_container_width=True, on_click=set_submitted_answer, args=(answer,))
            
            if st.session_state.choosen_answer == correct_answer and st.session_state.submitted:
                st.success("✅ Correct!")
                st.session_state.score = '1/1'
            # if the score is not correct, the questions is added to the practice phase
            elif st.session_state.submitted:
                st.error("❌ Incorrect. Try again.")
                st.session_state.score = '0/1'
                add_to_practice_phase()

            #render the nav buttons
            render_navigation_buttons()


def render_teacher_learning_page():
    """
    Renders the page that takes the student through the concepts of the lecture
    with info segments and questions. The student can navigate between segments
    and will get personalized feedback on their answers. Incorrectly answered
    questions are added to the practice phase.
    """
    initialise_learning_page()

    # Display the info or question in the middle column
    if st.session_state.submitted:
        with mid_col:
            render_progress_bar()

            # Render image if present in the feedback
            image_path = fetch_image_path()
            if image_path:
                render_image(image_path)

            render_question()
            perc_df = generate_insights()
        
        columns = st.columns([1, 12, 1])
        with columns[1]:
            render_insights(perc_df)
            render_navigation_buttons()
    else:
        with mid_col:
            render_progress_bar()

            image_path = fetch_image_path()
            if image_path:
                render_image(image_path)
            
            render_question()            
            render_check_and_nav_buttons()


def rerun_if_no_docs_for_feedback_path(feedback_path):
    """
    Check if there is any feedback to aggregate (only if users made the current question). 
    Displays warning and reruns program (sort of return) if there isn't any feedback in the db.
    """
    feedback_count = db.users.count_documents(
        { 
            feedback_path: {"$exists": True, "$ne": {}}
        }
    )

    if feedback_count == 0:
        st.warning("No feedback to aggregate into insights. Try again in 3 seconds.")
        time.sleep(3)
        st.session_state.submitted = False
        st.rerun()


def flatten_db_cursor(cursor):
    """
    Puts all data from db cursor in a flat list format.
    """
    flat_list = []
    for doc in cursor:
        module = st.session_state.selected_module
        question = st.session_state.segment_content['question'].replace('.', '')
        feedback_items = doc['progress'][module]['feedback'][question]
        for i, item in enumerate(feedback_items):
            flat_list.append({'feedback_item': i+1, 'score': item['score'], 'feedback': item['feedback']})
    
    return flat_list


def create_score_percentages_df(flat_feedback_list):
    df = pd.DataFrame(flat_feedback_list, columns=['feedback_item', 'score', 'feedback'])

    # Each user has feedback items for the same parts of the answers, all with their own score
    # Use size() to count how many times a score is given for one of the feedback items for each score type (0, 0.5, 1)
    size_df = df.groupby(['feedback_item', 'score']).size()

    # Group the scores together and calculate the percentage for each type of score for each feedback item
    perc_df = size_df.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

    # Reorganize scores logically by making new columns for each score type
    perc_df = perc_df.unstack()

    # Fill empty cells with 0
    perc_df = perc_df.fillna(0)

    # Rename the columns to be more intuitive
    perc_df.columns = [f"{col} score" for col in perc_df.columns]

    return perc_df


def find_docs_for_path(path):
    """
    Finds the documents in a db for a certain path and returns a cursor.
    """
    # A feedback cursor is not a JSON object, but a collection of JSON objects
    cursor = db.users.find(
        {
            path: {"$exists": True, "$not": {"$size":  0}} # Check if the path exists and has a value other then 0
        },
        {
            path: 1 # Boolean to tell that you want to project (output) this path
        }
    )

    return cursor


def generate_insights():
    """
    Aggregates the feedback from all users into percentages for 
    each score type (0.0, 0.5, 1.0).
    """
    module = st.session_state.selected_module
    # Remove dots to prevent interference with querying db because of the dot notation in path
    question = st.session_state.segment_content['question'].replace('.', '')

    feedback_path = f"progress.{module}.feedback.{question}"

    rerun_if_no_docs_for_feedback_path(feedback_path)

    feedback_cursor = find_docs_for_path(feedback_path)

    flat_feedback_list = flatten_db_cursor(feedback_cursor)

    perc_df = create_score_percentages_df(flat_feedback_list)

    return perc_df


def extract_score(index, score_type, perc_df):
    """
    Extract the occurrence of the score type from df and convert
    percentage to the right ratio of the bar graph.
    """
    if score_type in perc_df.columns:
        total_bar_length = 6
        score_percentage = int(perc_df.loc[index, score_type].item()) * total_bar_length / 100
        return score_percentage
    else:
        return float(0)


def render_insights(perc_df):
    """
    Plots the aggregated insights and displays it on streamlit. Each answer item gets
    its own bar that consists of three colors, corresponding to the three possible scores.
    """
    # Extract the relevant data from the aggregated feedback dataframe
    data = {
        'answer_items': [item['item'] for item in st.session_state.segment_content['answer_items']],
        '0.0 score': perc_df.get('0.0 score', 0),
        '0.5 score': perc_df.get('0.5 score', 0),
        '1.0 score': perc_df.get('1.0 score', 0)
    }

    df = pd.DataFrame(data)

    # Wrap the text so long sentences fit on the left side of graph
    df['wrapped_items'] = df['answer_items'].apply(lambda text: '<br>'.join(textwrap.wrap(text, width=50))) # Adjust width of box

    # Create new figure
    fig = go.Figure()

    # Settings for the names and colors of the figure
    fig_layout = {
        'score_names': ['Ontbreekt / Incorrect', 'Gedeeltelijk correct', 'Incorrect'],
        'scores': ['0.0 score', '0.5 score', '1.0 score'],
        'bar_colors': ['red', 'orange', 'green']
    }

    # Create a bar for each score with a color and name and the corresponding answer item
    for i in range(len(fig_layout['scores'])):
        fig.add_trace(go.Bar(
            y=df['wrapped_items'],
            x=df[fig_layout['scores'][i]],
            name=fig_layout['score_names'][i],
            orientation='h',
            marker_color=fig_layout['bar_colors'][i],
            width=0.7
        ))

    fig.update_layout(
        barmode='stack',
        margin=dict(l=20, r=20, t=20, b=20),
        height=90 + 85 * len(df['answer_items']), # Height of figure is sort of adaptive
        width=1200, # Width of whole figure
        xaxis=dict(tickfont=dict(size=18, color='black')),
        yaxis=dict(tickfont=dict(size=18, color='black'), autorange='reversed')
    )

    st.plotly_chart(fig)


# def render_insights_old(perc_df):
#     st.write(perc_df)
#     bar_segments = []
#     for index in perc_df.index:
#         # Define the segments of each bar
#         # Each tuple consists of (length, color)
#         bar_segments.append(
#             [
#                 (extract_score(index, '1.0 score', perc_df), '#c0e7c0'), # 0.0
#                 (extract_score(index, '0.5 score', perc_df), '#f7d4b6'), # 0.5
#                 (extract_score(index, '0.0 score', perc_df), '#e5bbbb')  # 1.0
#             ]
#         )

#     st.write(bar_segments)
    

#     bottom_bar_pos = 0 # Starting position of first bar
#     bar_height = 0.2 # Thickness
#     total_width = 6

#     answer_items = [item['item'] for item in st.session_state.segment_content['answer_items']]

#     # Create each bar with its bar segments
#     for i, bar in enumerate(bar_segments):
#         text_column = st.columns([1, 50, 1])[1]
#         with text_column:
#             st.write(answer_items[i])

#         left_pos = 0  # Starting left position for each bar
#         # Create the figure and axis
#         fig, ax = plt.subplots(figsize=(total_width, bar_height))
#         fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

#         ax.set_xlim(0, total_width)
#         ax.set_ylim(0, bar_height)
#         ax.axis('off') # Remove axes

#         for segment in bar:

#             # Draw each segment
#             bar_length, color = segment
#             rect = plt.Rectangle((left_pos, bottom_bar_pos), bar_length, bar_height, color=color)

#             # Draw actual bar graphics
#             ax.add_patch(rect)

#             # Update the left position for the next segment
#             left_pos += bar_length

#         # Plot one bar
#         st.pyplot(fig)


def set_submitted_answer(answer):
    st.session_state.submitted = True
    st.session_state.choosen_answer = answer
    return

    
def reset_submitted_if_page_changed():
    """Checks if the page changed and if so, resets submitted to false in 
    order to prevent the question from being evaluated directly when opening
    a page that starts with a question."""
    st.session_state.current_page = (st.session_state.selected_module, st.session_state.selected_phase)
    if st.session_state.old_page != st.session_state.current_page:
        st.session_state.submitted = False
        st.session_state.old_page = (st.session_state.selected_module, st.session_state.selected_phase)


def render_theory_page():
    """
    Renders the page that contains the theory of the lecture.
    """
    with mid_col:
        for segment in st.session_state.page_content["segments"]:
            if segment['type'] == 'info':
                st.session_state.segment_content = segment
                render_info()


def select_page_type():
    """
    Determines what type of page to display based on which module the user selected.
    """
    # For convenience, store the selected module name in a variable
    module = st.session_state.selected_module

    # Make module name lowercase and replace spaces and with underscores and cuts off at the first
    module_json_name = module.replace(" ", "_")

    # Load the json content for this module
    with open(f"./modules/{module_json_name}.json", "r") as f:
        st.session_state.page_content = json.load(f)

    # Determine what type of page to display
    if st.session_state.selected_phase == 'learning':
        if st.session_state.user_type == 'student':
            render_learning_page()
        if st.session_state.user_type == 'teacher':
            render_teacher_learning_page()


def initialise_session_states():
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None

    if 'info_page' not in st.session_state:
        st.session_state.info_page = False

    if 'warned' not in st.session_state:
        st.session_state.warned = None

    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False

    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'old_page' not in st.session_state:
        st.session_state.old_page = None

    if 'current_page' not in st.session_state:
        st.session_state.current_page = None

    if 'ordered_segment_sequence' not in st.session_state:
        st.session_state.ordered_segment_sequence = []

    if 'ordered_segment_sequence' not in st.session_state:
        st.session_state.ordered_segment_sequence = []

    if 'selected_phase' not in st.session_state:
        st.session_state.selected_phase = None

    if 'easy_count' not in st.session_state:
        st.session_state.easy_count = {}

    if 'page_content' not in st.session_state:
        st.session_state.page_content = None

    if 'indices' not in st.session_state:
        st.session_state.indices = []

    if 'segment_index' not in st.session_state:
        st.session_state.segment_index = 0

    if 'authentication_status' not in st.session_state:
        st.session_state.authentication_status = None

    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = None
    
    if 'modules' not in st.session_state:
        st.session_state.modules = []

    if 'segments' not in st.session_state:
        st.session_state.segments = None
    
    if 'segment_content' not in st.session_state:
        st.session_state.segment_content = None

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    
    if 'student_answer' not in st.session_state:
        st.session_state.student_answer = ""
        
    if 'score' not in st.session_state:
        st.session_state.score = ""

    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""

    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = ""

    if 'shuffled_answers' not in st.session_state:
        st.session_state.shuffled_answers = None


def render_logo():
    st.image('./images/logo.png', width=100)


def determine_modules():
    """	
    Function to determine which names of modules to display in the sidebar 
    based on the JSON module files.	
    """
    # Determine the modules to display in the sidebar
    if st.session_state.modules == []:
        # Read the modules from the modules directory
        modules = os.listdir("./modules")
        # Remove the json extension and replace the underscores with spaces
        modules = [module.replace(".json", "").replace("_", " ") for module in modules]
        # Sort the modules in correct order based on the college number
        modules.sort(key=lambda module: int(module.split(" ")[1]))
        st.session_state.modules = modules


def upload_feedback():
    """Uploads feedback to the database."""
    db.feedback.insert_one({"feedback": st.session_state.feedback_box})
    st.session_state.feedback_submitted = True


def render_feedback_form():
    """Feedback form in the sidebar."""
    st.write("\n\n")
    st.write("\n\n")
    st.sidebar.subheader("Denk je mee? (anoniem)")  
    st.sidebar.text_area(
        label='Wat vind je handig? Wat kan beter? etc. Voer geen persoonlijke of herkenbare gegevens in.',
        key='feedback_box',
    )

    st.sidebar.button("Verstuur", on_click=upload_feedback, use_container_width=True)

    if st.session_state.feedback_submitted:
        st.sidebar.success("Bedankt voor je feedback!")
        st.balloons()
        time.sleep(2)
        st.session_state.feedback_submitted = False
        st.rerun()


def render_info_page():
    """Renders the info page that contains the explanation of the learning and practice phases."""
    with open("./uitleg_llms.txt", "r") as f:
        info_page = f.read()
    with mid_col:
        st.markdown(info_page, unsafe_allow_html=True)
    return


def set_info_page_true():
    """Sets the info page to true."""
    st.session_state.info_page = True


def track_visits():
    """Tracks the visits to the modules."""
    db.users.update_one(
        {"username": st.session_state.username},
        {"$inc": {f"progress.{st.session_state.selected_module}.visits.{st.session_state.selected_phase}": 1}}
    )


def determine_user_type():
    """Sets the user as teacher or student, depending on current setting"""
    teacher_on = st.toggle("Zet docent modus aan")
    if teacher_on:
        st.text_input("Vul de toegangscode in", type='password', key='teacher_code')
        if st.session_state.teacher_code == 'brainloop':
            st.session_state.user_type = 'teacher'
        else:
            st.warning('Toegangscode is onjuist')
    else:
        st.session_state.user_type = 'student'
    
    

def render_sidebar():
    """	
    Function to render the sidebar with the modules and login module.	
    """
    with st.sidebar:
        spacer, image_col = st.columns([0.4, 1])
        with image_col:
            render_logo()
        st.sidebar.title("Colleges")

        # Display the modules in expanders in the sidebar
        for module in st.session_state.modules:
            with st.expander(module):
                # Display buttons for the two types of phases per module
                if st.button('Leerfase 📖', key=module + ' learning'):
                    st.session_state.selected_module = module
                    st.session_state.selected_phase = 'learning'
                    st.session_state.info_page = False
                    track_visits()

        render_feedback_form()

        st.sidebar.subheader("Extra info")
        st.button("Uitleg mogelijkheden & limitaties LLM's", on_click=set_info_page_true, use_container_width=True, key="info_button_sidebar")

        st.subheader("Docent modus")
        determine_user_type()


def initialise_database():
    """
    Initialise the progress object with the modules and phases in the database.
    """
    for module in st.session_state.modules:
        db.users.update_one(
            {"username": st.session_state.username},
            {"$set":
             {"warned": False,
              f"progress.{module}": {
                    "learning": {"segment_index": -1}, # Set to -1 so an explanation displays when phase is first opened
                    "practice": {"segment_index": -1,
                                 "ordered_segment_sequence": [],
                                }}
            }}
        )


def initialise_module_in_database(module):
    """
    Adds a new module to the database without resetting the rest of the database.
    """
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set":
         {f"progress.{module}": {
                "learning": {"segment_index": -1}, # Set to -1 so an explanation displays when phase is first opened
                "practice": {"segment_index": -1,
                                "ordered_segment_sequence": [],
                            }}
        }}
    )


def determine_if_to_initialise_database():
    """
    Determine if currently testing, if the progress is saved, or if all modules are included
    and if so, reset db when reloading webapp.
    """
    user_exists = db.users.find_one({"username": st.session_state.username})

    if not user_exists:
        db.users.insert_one({"username": st.session_state.username})

    if reset_user_doc:
        if 'reset_db' not in st.session_state:
            st.session_state.reset_db = True
        
        if st.session_state.reset_db:
            st.session_state.reset_db = False
            initialise_database()
            return


    user = db.users.find_one({"username": st.session_state.username})
    
    if "progress" not in user:
        initialise_database()
        return
    
    for module in st.session_state.modules:
        if module not in user["progress"]:
            initialise_module_in_database(module)
            return


def fetch_username():
    user_doc = db.users.find_one({'nonce': st.session_state.nonce})
    st.session_state.username = user_doc['username']


def invalidate_nonce():
    db.users.update_one({'username': st.session_state.username}, {'$set': {'nonce': None}})
    st.session_state.nonce = None


def convert_image_base64(image_path):
    """Converts image in working dir to base64 format so it is 
    compatible with html."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


def render_login_page():
    """This is the first page the user sees when visiting the website and 
    prompts the user to login via SURFconext."""
    columns = st.columns([1, 0.9, 1])
    with columns[1]:
        welcome_title = "Celbiologie - deel 2"
        logo_base64 = convert_image_base64("./images/logo.png")

        if surf_test_env:
            href = "http://localhost:3000/"
        else:
            href = "https://learnloop.datanose.nl/"
        
        html_content = f"""
        <div style='text-align: center; margin: 20px;'>
            <img src='data:image/png;base64,{logo_base64}' alt='Logo' style='max-width: 25%; height: auto; margin-bottom: 40px'>
            <h1 style='color: #333; margin-bottom: 20px'>{welcome_title}</h1>
            <a href={href} style="text-decoration: none;">
                <button style='font-size:20px; border: none; color: white; padding: 10px 20px; \
                text-align: center; text-decoration: none; display: block; width: 100%; margin: \
                4px 0px; cursor: pointer; background-color: #4CAF50; border-radius: 12px;'>UvA Login</button>
            </a>
        </div>"""

        st.markdown(html_content, unsafe_allow_html=True)


def fetch_if_warned():
    """Fetches from database if the user has been warned about LLM."""
    user_doc = db.users.find_one({"username": st.session_state.username})
    return user_doc["warned"]


def fetch_and_remove_nonce():
    if 'nonce' not in st.session_state:
        st.session_state.nonce = st.query_params.get('nonce', None)
        st.query_params.pop('nonce', None) # Remove the nonce from the url


# def determine_user_type():
#     """
#     Determines if current account is from teacher (Luc) or student.
#     This is used to determine which interface to show.
#     """
#     lucs_username = ("4def1a90c9aa237c857bc530766d0feb6d831415", "flower2960", "3385ec9a01b87268772cdfb30801734dcec5a7e1")
#     if st.session_state.username in lucs_username:
#         st.session_state.user_type = 'teacher'
#     else:
#         st.session_state.user_type = 'student'


if __name__ == "__main__":
    # ---------------------------------------------------------
    # SETTINGS FOR TESTING:

    # Turn on 'testing' to use localhost instead of learnloop.datanose.nl for authentication
    surf_test_env = False

    # Reset db for current user every time the webapp is loaded
    reset_user_doc = False

    # Your current IP has to be accepted by Gerrit to use CosmosDB (Gerrit controls this)
    use_mongodb = False

    # Use dummy LLM feedback as response to save openai costs and time during testing
    use_dummy_openai_calls = False

    no_login_page = False

    # Bypass authentication when testing so flask app doesnt have to run
    skip_authentication = False
    if skip_authentication:
        no_login_page = True
        st.session_state.username = "test_user_2"
    # ---------------------------------------------------------

    # Create a mid column with margins in which everything one a 
    # page is displayed (referenced to mid_col in functions)
    left_col, mid_col, right_col = st.columns([1, 3, 1])
    
    initialise_session_states()
    db = connect_to_database()
    openai_client = connect_to_openai()

    fetch_and_remove_nonce()

    # Only render login page if not testing
    if no_login_page == False \
        and st.session_state.nonce is None \
        and not use_mongodb \
        and not st.session_state.username:
        render_login_page()

    # Fetch username through query param and invalidate nonce
    elif st.session_state.username is None:
        fetch_username()
        invalidate_nonce()
        st.rerun() # Needed, else it seems to get stuck here

    # Render the actual app
    else:
        # Determine the modules of the current course
        if st.session_state.modules == []:
            determine_modules()
        
        render_sidebar()

        if st.session_state.info_page:
            render_info_page()
            exit()
        elif st.session_state.selected_module is None:         
            # Automatically start the first module if no module is selected           
            st.session_state.selected_module = st.session_state.modules[0]
            st.session_state.selected_phase = 'learning'
            
            # Rerun to make sure the page is displayed directly after start button is clicked
            st.rerun()
        else:
            # Only (re-)initialise if user is new or when testing is on
            determine_if_to_initialise_database()

            if st.session_state.warned == None:
                st.session_state.warned = fetch_if_warned()

            select_page_type()
