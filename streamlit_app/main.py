import time
import random
import streamlit as st
from dotenv import load_dotenv
import os
import json
from openai import AzureOpenAI
from pymongo import MongoClient
import base64
from overview_page import OverviewPage
import db_config
from data_access_layer import DatabaseAccess, ContentAccess
from datetime import datetime

# Must be called first
st.set_page_config(page_title="LearnLoop", layout="wide")

load_dotenv()

def connect_to_openai():
    return AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  
    api_version="2024-03-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

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
    db.users_2.update_one(
        {"username": st.session_state.username},
        {"$set": data}
    )


def evaluate_answer():
    """Evaluates the answer of the student and returns a score and feedback."""
    if use_dummy_openai_calls != True:
        
        # Create user prompt with the question, correct answer and student answer
        prompt = f"""Input:\n
        Vraag: {st.session_state.segment_content['question']}\n
        Antwoord student: {st.session_state.student_answer}\n
        Beoordelingsrubriek: {st.session_state.segment_content['answer']}\n
        Output:\n"""

        # Read the role prompt from a file
        with open("./direct_feedback_prompt.txt", "r", encoding="utf-8") as f:
            role_prompt = f.read()


        response = openai_client.chat.completions.create(
            model="learnloop",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        split_response = response.choices[0].message.content.split(";;")

        if len(split_response) != 2:
            raise ValueError("Server response is not in the correct format. Please retry.")

        st.session_state.feedback = split_response[0].split(">>")
        st.session_state.score = split_response[1]
    else:
        st.session_state.feedback = "O"
        st.session_state.score = "0/2"


def score_to_percentage():
    """Converts a score in the form of a string to a percentage."""
    try:
        # Calculate the score percentage
        part, total = st.session_state.score.split('/')
        if total == '0':
            score_percentage = 0
        else:
            # If there is a comma (e.g. 1,5), change it to a dot
            if ',' in part:
                part = part.replace(',', '.')
            score_percentage = int(float(part) / float(total) * 100)
    except Exception as e:
        st.error(f"Error calculating score: {e}")
        return  # Early exit on error
    
    return score_percentage

def render_mc_feedback(question):
    if question['student_answer'] == question['correct_answer']: # antwoord is goed
        result_html = f"""
        <div style='background-color: rgba(0, 128, 0, 0.2); padding: 10px; margin-bottom: 15px; margin-top: 28px; border-radius: 7px; display: flex; align-items: center;'> <!-- Verhoogd naar 50px voor meer ruimte -->
            <p style='font-size: 16px; margin: 8px 0 8px 10px; padding: 0;'>✅  {question['student_answer']}</p>
        </div>
        """
    else: # antwoord is fout
        result_html = f"""
        <div style='background-color: rgba(255, 0, 0, 0.2); padding: 10px; margin-bottom: 15px; margin-top: 28px; border-radius: 7px; display: flex; align-items: center;'> <!-- Verhoogd naar 50px voor meer ruimte -->
            <p style='font-size: 16px; margin: 8px 0 8px 10px; padding: 0;'>❌  {question['student_answer']}</p>
        </div>
        <div>
        <p> Goede antwoord: {question['correct_answer']} </p>
        </div>
        """
        
    st.markdown(result_html, unsafe_allow_html=True)

def render_feedback(feedback_field):
    """Renders the feedback box with the score and feedback."""
    # Calculate the score percentage
    score_percentage = score_to_percentage()

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
        <h1 style='font-size: 20px; margin: 8px 0 8px 10px; padding: 0;'>Score: {st.session_state.score}</h1>
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
    phase_length = determine_phase_length()

    while True:
        # Update segment index based on direction
        st.session_state.segment_index += step_direction

        # Ensure segment index stays within valid range
        if st.session_state.segment_index < 0:
            st.session_state.segment_index = 0
            break
        if st.session_state.segment_index >= phase_length:
            st.session_state.segment_index = phase_length - 1
            break
        if st.session_state.segment_index == phase_length - 1:
            st.session_state.segment_index = 100_000
            break

        # Load new segment content
        st.session_state.segment_content = st.session_state.page_content['segments'][st.session_state.segment_index]

        # Skip theory segments if questions_only is enabled
        if not st.session_state.questions_only or st.session_state.segment_content['type'] != 'theory':
            break

    # Prevent evaluating answer when navigating to the next or previous segment
    st.session_state.submitted = False
    st.session_state.shuffled_answers = None
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
        st.button('Controleer', use_container_width=True, on_click=set_submitted_true)
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
            return f"./content/images/{image_path}"


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
    if 'answers' in st.session_state.segment_content:
        st.subheader(st.session_state.segment_content['question']) 
    else:
        number_of_points = st.session_state.segment_content['answer'].count('(1 punt)')
        if number_of_points == 0:
            st.subheader(st.session_state.segment_content['question']) 
        elif number_of_points == 1:    
            st.subheader(st.session_state.segment_content['question']  + f' ({number_of_points} punt)')
        else:
            st.subheader(st.session_state.segment_content['question']  + f' ({number_of_points} punten)')


def fetch_ordered_segment_sequence():
    """Fetches the practice segments from the database."""
    user_doc = db.users_2.find_one({"username": st.session_state.username})
    st.session_state.ordered_segment_sequence = user_doc["progress"][st.session_state.selected_module]["practice"]["ordered_segment_sequence"]


def update_ordered_segment_sequence(ordered_segment_sequence):
    """Updates the practice segments in the database."""
    db.users_2.update_one(
        {"username": st.session_state.username},
        {"$set": {f"progress.{st.session_state.selected_module}.practice.ordered_segment_sequence": ordered_segment_sequence}}
    )


def add_to_practice_phase():
    """
    Adds the current segment to the practice phase in the database if the score is lower than 100.
    """
    if score_to_percentage() < 100:
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


def render_start_button():
    """Start button at the beginning of a phase that the user never started."""
    st.button("Start", use_container_width=True, on_click=change_segment_index, args=(1,))


def render_learning_explanation():
    """Renders explanation of learning phase if the user hasn't started with
    the current phase."""
    with mid_col:
        st.markdown('<p style="font-size: 30px;"><strong>Leren 📖</strong></p>', unsafe_allow_html=True)
        # st.write("The learning phase **guides you through the concepts of a lecture** in an interactive way with **personalized feedback**. Incorrectly answered questions are automatically added to the practice phase.")
        st.write("In de leerfase word je op een interactieve manier door de concepten van een college heen geleid en krijg je **direct persoonlijke feedback** op open vragen. Vragen die je niet goed hebt, komen automatisch terug in 'Herhalen' 🔄.")
        render_start_button()
    exit()

def render_oefententamen_explanation():
    with mid_col:
        st.markdown('<p style="font-size: 30px;"><strong>Oefententamen ✍🏽</strong></p>', unsafe_allow_html=True)
        # st.write("The learning phase **guides you through the concepts of a lecture** in an interactive way with **personalized feedback**. Incorrectly answered questions are automatically added to the practice phase.")
        st.write("Dit oefententamen bevat een willekeurige selectie aan tentamenvragen over de stof uit de colleges.")
        render_start_button()
    exit()


def initialise_learning_page():
    """
    Sets all session states to correspond with database.
    """
    # Fetch the last segment index from db
    st.session_state.segment_index = cont_dal.fetch_segment_index()

    if st.session_state.segment_index == -1: # If user never started this phase
        if st.session_state.selected_module.startswith("Oefententamen"):
            render_oefententamen_explanation()
        else:
            render_learning_explanation()
    elif st.session_state.segment_index == 100_000: # if we are at the final screen
            render_final_page()
    else:
        # Select the segment (with contents) that corresponds to the saved index where the user left off
        st.session_state.segment_content = st.session_state.page_content['segments'][st.session_state.segment_index]
        reset_submitted_if_page_changed()


def reset_segment_index_and_feedback():
    """
    When the user wants to go back to the beginning of the phase, the feedback progress
    is reset.
    """
    st.session_state.segment_index = 0
    upload_progress()
    user_query = {"username": st.session_state.username}
    set_empty_array = {
        "$set": {
            f"progress.{st.session_state.selected_module}.feedback.questions": []
        }
    }
    result = db.users.update_one(user_query, set_empty_array)
    

# render the page at the end of the learning phase (after the last question)
def render_final_page():
    questions = get_feedback_questions_from_db()
    if len(questions) == 0:
        with mid_col:
            st.subheader("Feedbackoverzicht")
            st.write("Voor een overzicht van je gemaakte vragen moet je eerst vragen maken 🙃")
            st.button("Terug naar begin", on_click=reset_segment_index_and_feedback, use_container_width=True)
        exit()

    else:
        total_score, possible_score = calculate_score()
        score_percentage = int(total_score / possible_score * 100)
        st.balloons()
        with mid_col:
            st.title('Feedbackoverzicht')
            st.markdown(f'<p style="font-size: 30px;"><strong>Eindscore: {total_score}/{possible_score} ({score_percentage} %) </strong></p>', unsafe_allow_html=True)
            st.markdown('---')
            show_feedback_overview()
            st.button("Terug naar begin en wis feedback", on_click=reset_segment_index_and_feedback, use_container_width=True)


        # otherwise the progress bar and everything will get rendered
        exit()

def calculate_score():
    questions = get_feedback_questions_from_db()
    total_score = 0
    possible_score = 0
    for question in questions:
        score_str = question.get('score', '0/1')  # Default to "0/1" if score is missing
        parts = score_str.split('/')
        total_score += int(parts[0])
        possible_score += int(parts[1])
    return total_score, possible_score

def get_feedback_questions_from_db():
    query = {"username": st.session_state.username}

    projection = {
        f"progress.{st.session_state.selected_module}.feedback.questions": 1,
        "_id": 0  
    }

    user_document = db.users.find_one(query, projection)

    questions = user_document.get('progress', {})\
                            .get(st.session_state.selected_module, {})\
                            .get('feedback', {})\
                            .get('questions', [])
                            
    return questions


def show_feedback_overview():
    questions = get_feedback_questions_from_db()
    for question in questions:
        st.subheader(f"{question['question']}")
        if 'feedback' in question:
            render_feedback(question['feedback'])            
        else:
            render_mc_feedback(question)
        st.markdown("---")


def render_oefententamen_final_page():
    with mid_col:
        st.markdown('<p style="font-size: 30px;"><strong>Einde oefententamen 🎓 </strong></p>', unsafe_allow_html=True)
        st.write("Klaar! Hoe ging het?")
        st.button("Terug naar begin", on_click=reset_segment_index_and_feedback, use_container_width=True)
    exit()


def set_warned_true():
    """Callback function for a button that turns of the LLM warning message."""
    db.users_2.update_one(
        {"username": st.session_state.username},
        {"$set": {"warned": True}}
    )
    st.session_state.warned = True


def reset_progress():
    """Resets the progress of the user in the current phase to the database."""
    db.users_2.update_one(
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


def progress_date_tracking_format():
    """
    The date format for the progress counter that counts the number of times
    a user visited a segment or answered a question, through dates as entries.
    It also adds the first entry directly.
    """
    date = datetime.utcnow().date()
    return {"type": cont_dal.get_segment_type(), "entries": [date.isoformat()]}


def add_date_to_progress_counter():
    """
    Counts how many times a person answered the current question and updates database.
    """
    module = st.session_state.selected_module.replace('_', ' ')
    user_doc = db_dal.find_user_doc()
    segment_progress_count = db_dal.fetch_progress_counter(module, user_doc)[str(st.session_state.segment_index)]
    
    # Initialise or update date format
    if segment_progress_count is None:
        segment_progress_count = progress_date_tracking_format()
    else:
        date = datetime.utcnow().date()
        segment_progress_count['entries'].append(date.isoformat())

    db_dal.update_progress_counter_for_segment(module, segment_progress_count)


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

        # Skip theory segment
        if st.session_state.questions_only and st.session_state.segment_content['type'] == 'theory':
            change_segment_index(1)
            initialise_learning_page()
        # Determine what type of segment to display and render interface accordingly
        if st.session_state.segment_content['type'] == 'theory':
            render_info()
            add_date_to_progress_counter()
            render_navigation_buttons()


        # Open question
        if (st.session_state.segment_content['type'] == 'question' and 
        'answer' in st.session_state.segment_content):
                
            if st.session_state.submitted:
                
                # Render image if present in the feedback
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
                    evaluate_answer()
                    add_date_to_progress_counter()
                                
                render_feedback(st.session_state.feedback)
                save_feedback_on_open_question()
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
                save_feedback_on_mc_question()
            # if the score is not correct, the questions is added to the practice phase
            elif st.session_state.submitted:
                st.error("❌ Incorrect. Try again.")
                st.session_state.score = '0/1'
                add_to_practice_phase()
                save_feedback_on_mc_question()

            #render the nav buttons
            render_navigation_buttons()


def set_submitted_answer(answer):
    st.session_state.submitted = True
    st.session_state.choosen_answer = answer
    return

def save_feedback_on_open_question():
    """
    Makes sure that the feedback to the question is saved to the database. First it checks if
    there does not already exists a feedback entry in the database. If it does, it overwrites this one,
    if it doesn't it makes a new one.
    """
    user_query = {"username": st.session_state.username}

    # First, pull the existing question if it exists
    pull_query = {
        "$pull": {
            f"progress.{st.session_state.selected_module}.feedback.questions": {
                "question": st.session_state.segment_content['question']
            }
        }
    }

    # Execute the pull operation
    db.users.update_one(user_query, pull_query)

    # Prepare the new question data to be pushed
    new_question_data = {
        'question': st.session_state.segment_content['question'],
        'student_answer': st.session_state.student_answer,
        'feedback': st.session_state.feedback,
        'score': st.session_state.score
    }

    # Push the new question data
    push_query = {
        "$push": {
            f"progress.{st.session_state.selected_module}.feedback.questions": new_question_data
        }
    }

    # Execute the push operation
    db.users.update_one(user_query, push_query)

def save_feedback_on_mc_question():
    """
    Makes sure that the feedback to a MC question is saved to the database. First it checks if
    there does not already exists a feedback entry in the database. If it does, it overwrites this one,
    if it doesn't it makes a new one.
    """
    user_query = {"username": st.session_state.username}

    # First, pull the existing question if it exists
    pull_query = {
        "$pull": {
            f"progress.{st.session_state.selected_module}.feedback.questions": {
                "question": st.session_state.segment_content['question']
            }
        }
    }

    # Execute the pull operation
    db.users.update_one(user_query, pull_query)

    # Prepare the new question data to be pushed
    new_question_data = {
        'question': st.session_state.segment_content['question'],
        'student_answer': st.session_state.choosen_answer,
        'correct_answer': st.session_state.segment_content['answers']['correct_answer'],
        'score': st.session_state.score
    }

    # Push the new question data
    push_query = {
        "$push": {
            f"progress.{st.session_state.selected_module}.feedback.questions": new_question_data
        }
    }

    # Execute the push operation
    db.users.update_one(user_query, push_query)

    
def reset_submitted_if_page_changed():
    """Checks if the page changed and if so, resets submitted to false in 
    order to prevent the question from being evaluated directly when opening
    a page that starts with a question."""
    st.session_state.current_page = (st.session_state.selected_module, st.session_state.selected_phase)
    if st.session_state.old_page != st.session_state.current_page:
        st.session_state.submitted = False
        st.session_state.old_page = (st.session_state.selected_module, st.session_state.selected_phase)


def render_practice_explanation():
    """Renders the explanation for the practice phase if the user hasn't started
    this phase in this module."""
    with mid_col:
        st.markdown('<p style="font-size: 30px;"><strong>Herhalen 🔄</strong></p>', unsafe_allow_html=True)
        # st.write("The practice phase is where you can practice the concepts you've learned in the learning phase. It uses **spaced repetition** to reinforce your memory and **improve retention.**")
        st.write("Herhaal de moeilijkste vragen uit de leerfase met **_spaced repetition_** om je geheugen te versterken zodat je beter de stof onthoudt.")
        if st.session_state.ordered_segment_sequence == []:
            st.info(" Nog geen moeilijke vragen verzameld. Maak daarvoor eerst vragen uit de leerfase.")
        else:
            render_start_button()
    exit()


def initialise_practice_page():
    """Update all session states with database data and render practice explanation 
    if it's the first time."""

    # Fetch the last segment index from db
    st.session_state.segment_index = cont_dal.fetch_segment_index()

    if st.session_state.segment_index == -1:
        fetch_ordered_segment_sequence()
        render_practice_explanation()
    elif st.session_state.segment_index == 100_000:
        render_final_page()
    else:
        fetch_ordered_segment_sequence()

        json_index = st.session_state.ordered_segment_sequence[st.session_state.segment_index]
        
        # Select the segment (with contents) that corresponds to the saved json index where the user left off
        st.session_state.segment_content = st.session_state.page_content['segments'][json_index]
        
        reset_submitted_if_page_changed()



def render_practice_page():
    """
    Renders the page that contains the practice questions and 
    answers without the info segments and with the spaced repetition buttons.
    This phase allows the student to practice the concepts they've learned
    during the learning phase and which they found difficult.
    """
    initialise_practice_page()

    # Display the info or question in the middle column
    with mid_col:
        render_progress_bar()

        # Determine what type of segment to display and render interface accordingly
        # info_question
        if st.session_state.segment_content['type'] == 'theory':
            render_info()
            render_navigation_buttons()

        # Open question
        if (st.session_state.segment_content['type'] == 'question' and 
        'answer' in st.session_state.segment_content):
            
            # Render image if present in the feedback
            image_path = fetch_image_path()
            if image_path:
                render_image(image_path)

            render_question()
            if st.session_state.submitted:
                # Spinner that displays during evaluating answer
                with st.spinner(f"Een large language model (LLM) checkt je antwoord met het antwoordmodel. \
                                Check zelf het antwoordmodel als je twijfelt. \n\n Leer meer over het gebruik \
                                van LLM's op de pagina **'Uitleg mogelijkheden & limitaties LLM's'** onder \
                                het kopje 'Extra info' in de sidebar."):
                    render_student_answer()
                    evaluate_answer()
                
                render_feedback()
                render_explanation()
                render_SR_nav_buttons()
            else:
                if st.session_state.warned == False:
                    render_warning()
                else:
                    render_answerbox()
                    # Becomes True if user presses ctrl + enter to evaluate answer (instead of pressing "check")
                    if st.session_state.student_answer:
                        set_submitted_true()
                        st.rerun()
                    render_check_and_nav_buttons()

        # MC Question
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
            # if the score is not correct, the questions is added to the practice phase
            elif st.session_state.submitted:
                st.error("❌ Incorrect. Try again.")

            #render the nav buttons
            render_navigation_buttons()


def render_overview_page():
    """
    Renders the page that shows all the subjects in a lecture, which gives the 
    student insight into their progress.
    """
    overview_page = OverviewPage(st.session_state.selected_module)
    overview_page.render_page()


def render_selected_page():
    """
    Determines what type of page to display based on which module the user selected.
    """
    cont_dal.load_page_content_of_module_in_session_state(st.session_state.selected_module)
    
    # Determine what type of page to display
    if st.session_state.selected_phase == 'overview':
        render_overview_page()
    if st.session_state.selected_phase == 'learning':
        render_learning_page()
    if st.session_state.selected_phase == 'practice':
        render_practice_page()


def initialise_session_states():
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

    if 'questions_only' not in st.session_state:
        st.session_state.questions_only = False


def render_logo():
    st.image('./content/images/logo.png', width=100)


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
    db.users_2.update_one(
        {"username": st.session_state.username},
        {"$inc": {f"progress.{st.session_state.selected_module}.visits.{st.session_state.selected_phase}": 1}}
    )


def render_page_button(page_title, module, phase):
    """
    Renders the buttons that the users clicks to go to a certain page.
    """
    if st.button(page_title, key=f'{module} {phase}', use_container_width=True):
        st.session_state.selected_module = module
        st.session_state.selected_phase = phase
        st.session_state.info_page = False
        track_visits()
    

def render_sidebar():
    """	
    Function to render the sidebar with the modules and login module.	
    """
    with st.sidebar:
        spacer, image_col = st.columns([0.4, 1])
        with image_col:
            render_logo()
        st.sidebar.title("Colleges")
        practice_exam_count = 0
        # Display the modules in expanders in the sidebar
        for module in st.session_state.modules:
            # If the module is not a Oefententamen, then skip it
            if not module.startswith('Oefententamen'):
                with st.expander(module):
                    # Display buttons for the two types of phases per module
                    render_page_button('Leren 📖', module, phase='overview')
                    render_page_button('Herhalen 🔄', module, phase='practice')
            elif module.startswith('Oefententamen'):
                practice_exam_count += 1

        st.sidebar.title("Oefententamens")
        
        # Render the practice exam buttons
        for i in range(practice_exam_count):
            render_page_button(f'Oefententamen {i + 1} ✍🏽', f'Oefententamen {i + 1}', 'learning')
        st.session_state.questions_only = st.toggle("Alleen vragen displayen")
        # st.session_state.questions_only = st.checkbox("Alleen vragen displayen", value=st.session_state.questions_only)

        render_feedback_form() # So users can give feedback

        st.sidebar.subheader("Extra Info")
        st.button("Uitleg mogelijkheden & limitaties LLM's", on_click=set_info_page_true, use_container_width=True, key="info_button_sidebar")


def initialise_database():
    """
    Initialise the progress object with the modules and phases in the database.
    """
    for module in st.session_state.modules:
        db.users_2.update_one(
            {"username": st.session_state.username},
            {"$set":
             {"warned": False,
              f"progress.{module}": {
                    "learning": {"segment_index": -1}, # Set to -1 so an explanation displays when phase is first opened
                    "practice": {"segment_index": -1,
                                 "ordered_segment_sequence": [],
                                },
                    "feedback": {"questions": [] 
                                 }            
                    }
            }}
        )


def initialise_module_in_database(module):
    """
    Adds a new module to the database without resetting the rest of the database.
    """
    db.users_2.update_one(
        {"username": st.session_state.username},
        {"$set":
         {f"progress.{module}": {
                "learning": {"segment_index": -1}, # Set to -1 so an explanation displays when phase is first opened
                "practice": {"segment_index": -1,
                             "ordered_segment_sequence": [],
                            }}
        }}
    )


def create_empty_progress_dict(module):
    """
    Creates an empty dictionary that contains the JSON
    index of the segment as key and the number of times  
    the user answered a question.
    """
    empty_dict = {}

    cont_dal.load_page_content_of_module_in_session_state(module)

    number_of_segments = len(st.session_state.page_content['segments'])
    
    # Create a dictionary with indexes (strings) as key and None as value
    empty_dict = {str(i): None for i in range(number_of_segments)}
    
    return empty_dict


def determine_if_to_initialise_database():
    """
    Determine if currently testing, if the progress is saved, or if all modules are included
    and if so, reset db when reloading webapp.
    """
    user_exists = db.users_2.find_one({"username": st.session_state.username})

    if not user_exists:
        db.users_2.insert_one({"username": st.session_state.username})

    if reset_user_doc:
        if 'reset_db' not in st.session_state:
            st.session_state.reset_db = True
        
        if st.session_state.reset_db:
            st.session_state.reset_db = False
            initialise_database()
            return


    user = db.users_2.find_one({"username": st.session_state.username})
    
    if "progress" not in user:
        initialise_database()
        return
    
    for module in st.session_state.modules:
        if module not in user["progress"]:
            initialise_module_in_database(module)
            return

        # Check if the user doc contains the dict in which the
        # is saved how many times a question is made by user
        user_doc = db_dal.find_user_doc()
        if db_dal.fetch_progress_counter(module, user_doc) is None:
            empty_dict = create_empty_progress_dict(module)
            db_dal.add_progress_counter(module, empty_dict)


def fetch_username():
    user_doc = db.users_2.find_one({'nonce': st.session_state.nonce})
    st.session_state.username = user_doc['username']


def invalidate_nonce():
    db.users_2.update_one({'username': st.session_state.username}, {'$set': {'nonce': None}})
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
    user_doc = db.users_2.find_one({"username": st.session_state.username})
    return user_doc["warned"]


def fetch_and_remove_nonce():
    if 'nonce' not in st.session_state:
        st.session_state.nonce = st.query_params.get('nonce', None)
        st.query_params.pop('nonce', None) # Remove the nonce from the url


if __name__ == "__main__":
    # ---------------------------------------------------------
    # SETTINGS FOR TESTING:

    # Turn on 'testing' to use localhost instead of learnloop.datanose.nl for authentication
    surf_test_env = True

    # Reset db for current user every time the webapp is loaded
    reset_user_doc = False

    # Your current IP has to be accepted by Gerrit to use CosmosDB (Gerrit controls this)
    st.session_state.use_mongodb = True

    # Use dummy LLM feedback as response to save openai costs and time during testing
    use_dummy_openai_calls = False

    login_page = True

    # Bypass authentication when testing so flask app doesnt have to run
    skip_authentication = False
    if skip_authentication:
        login_page = True
        st.session_state.username = "test_user_2"
    # ---------------------------------------------------------

    # Create a mid column with margins in which everything one a 
    # page is displayed (referenced to mid_col in functions)
    left_col, mid_col, right_col = st.columns([1, 3, 1])
    
    db_dal = DatabaseAccess()
    cont_dal = ContentAccess()
    db = db_config.connect_db(st.session_state.use_mongodb)

    initialise_session_states()
    openai_client = connect_to_openai()

    fetch_and_remove_nonce()

    # Only render login page if not testing
    if login_page == True \
        and st.session_state.nonce is None \
        and st.session_state.use_mongodb == False \
        and st.session_state.username is None:
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
            cont_dal.determine_modules()
        
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

            render_selected_page()