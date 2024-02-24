import streamlit as st
import re
from dotenv import load_dotenv
import os
import database as database
import json
from openai import OpenAI
from pymongo import MongoClient
import certifi

# Must be called first
st.set_page_config(page_title="LearnLoop", layout="wide")

# Create openai instance
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # TODO: Clear the streamlit cache because currently the old api key is used
openai_client = OpenAI()

COSMOS_URI = os.getenv('COSMOS_URI')
db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())

db = db_client.LearnLoop
user_doc = db.users.find_one({"username": "flower2960"})


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


def evaluate_answer():
    """Evaluates the answer of the student and returns a score and feedback."""
    if st.session_state.currently_testing != True:
        
        # Create user prompt with the question, correct answer and student answer
        prompt = f"""Input:\n
        Vraag: {st.session_state.segment_content['question']}\n
        Antwoord student: {st.session_state.student_answer}\n
        Beoordelingsrubriek: {st.session_state.segment_content['answer']}\n
        Output:\n"""

        # Read the role prompt from a file
        with open("./prompts/feedback_prompt.txt", "r") as f:
            role_prompt = f.read()

        response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
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


def render_feedback():
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

    # Feedback with bullet points and bold scores
    feedback_items = [f"<li style='font-size: 17px; margin: 15px 0;'>{line}</li>" for line in st.session_state.feedback if line.strip()]
    feedback_html = f"<ul style='padding-left: 20px;'>{''.join(feedback_items)}</ul>"

    result_html = f"""
    <div style='background-color: {color}; padding: 25px; margin-bottom: 15px; border-radius: 8px;'>
        <h1 style='font-size: 40px; margin: 10px;'>{st.session_state.score}</h1>
        {feedback_html}
    </div>
    """

    st.markdown(result_html, unsafe_allow_html=True)

    st.warning("Let op: de scores worden automatisch gegenereerd en kunnen soms afwijken.")


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
        st.button('Previous', use_container_width=True, on_click=lambda: change_segment_index(-1))
    with col1:
        st.button('Repeat quickly ↩️', use_container_width=True, on_click=re_insert_question, args=(10,))
    with col2:
        st.button('Repeat later 🕒', use_container_width=True, on_click=re_insert_question, args=(15,))
    with col3:
        st.button('Got it ✅', use_container_width=True, on_click=lambda: change_segment_index(1))
    with col_next:
        st.button('Next', use_container_width=True, on_click=lambda: change_segment_index(1))


def render_explanation():
    with st.expander("Explanation"):
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

    if st.session_state.segment_index + step_direction in range(phase_length):
        st.session_state.segment_index += step_direction
    elif st.session_state.segment_index == phase_length - 1:
        st.session_state.segment_index = 0
    else:
        st.session_state.segment_index = phase_length - 1

    # Prevent evaluating aswer when navigating to the next or previous segment 
    st.session_state.submitted = False
    
    # Update database with new index
    upload_progress()


def render_navigation_buttons():
    """Render the navigation buttons that allows users to move between segments."""
    prev_col, next_col = st.columns(2)
    with prev_col:
        st.button("Previous", on_click=change_segment_index, args=(-1,), use_container_width=True)
    with next_col:
        st.button("Next", on_click=change_segment_index, args=(1,), use_container_width=True)


def set_submitted_true():
    """Whithout this helper function the user will have to press "check" button twice before submitting"""
    st.session_state.submitted = True


def render_check_and_nav_buttons():
    """Renders the previous, check and next buttons when a question is displayed."""
    col_prev_question, col_check, col_next_question = st.columns([1, 4, 1])
    with col_prev_question:
        st.button('Previous', use_container_width=True, on_click=change_segment_index, args=(-1,))
    with col_check:
        st.button('Check', use_container_width=True, on_click=set_submitted_true)
    with col_next_question:
        st.button('Next', use_container_width=True, on_click=change_segment_index, args=(1,))


def render_info():
    """Renders the info segment with title and text."""
    st.subheader(st.session_state.segment_content['title'])
    st.write(st.session_state.segment_content['text'])


def render_answerbox():
    """Render a textbox in which the student can type their answer."""
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
    """Adds the current segment to the practice phase in the database if the score is lower than 100."""
    # Store in variable for clarity
    segment_index = st.session_state.segment_index
    
    if score_to_percentage() < 100:
        fetch_ordered_segment_sequence()
        # Store in variable for clarity
        ordered_segment_sequence = st.session_state.ordered_segment_sequence

        if segment_index not in ordered_segment_sequence:
            ordered_segment_sequence.append(segment_index)

        # Update practice segments in db
        update_ordered_segment_sequence(ordered_segment_sequence)


def render_student_answer():
    """Renders the student's answer."""
    st.write('Your answer:')
    st.write(st.session_state.student_answer)


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
        st.markdown('<p style="font-size: 30px;"><strong>Learning phase 📖</strong></p>', unsafe_allow_html=True)
        st.write("The learning phase **guides you through the concepts of a lecture** in an interactive way with **personalized feedback**. Incorrectly answered questions are automatically added to the practice phase.")
        render_start_button()
    exit()


def initialise_learning_page():
    """Sets all session states to correspond with database."""
    # Fetch the last segment index from db
    st.session_state.segment_index = fetch_segment_index()

    if st.session_state.segment_index == -1: # If user never started this phase
        render_learning_explanation()
    else:
        # Select the segment (with contents) that corresponds to the saved index where the user left off
        st.session_state.segment_content = st.session_state.page_content['segments'][st.session_state.segment_index]
        reset_submitted_if_page_changed()


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

        if st.session_state.segment_content['type'] == 'question':
            render_question()
            if st.session_state.submitted:
                # Spinner that displays during evaluating answer
                with st.spinner("Een Large Language Model checkt je antwoord met het antwoordmodel. Twijfel je? Check de 'explanation' voor de juiste vergelijking."): 
                    evaluate_answer()
                render_student_answer()
                render_feedback()
                add_to_practice_phase()
                render_explanation()
                render_navigation_buttons()
            else:
                render_answerbox()
                if st.session_state.student_answer:
                    set_submitted_true()
                    st.rerun()
                render_check_and_nav_buttons()


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
        st.markdown('<p style="font-size: 30px;"><strong>Practice phase 📝</strong></p>', unsafe_allow_html=True)
        st.write("The practice phase is where you can practice the concepts you've learned in the learning phase. It uses **spaced repetition** to reinforce your memory and **improve retention.**")
        if st.session_state.ordered_segment_sequence == []:
            st.info("Nothing here. First walk through the learning phase to collect difficult questions.")
        else:
            render_start_button()
    exit()


def initialise_practice_page():
    """Update all session states with database data and render practice explanation 
    if it's the first time."""
    # Fetch the last segment index from db
    st.session_state.segment_index = fetch_segment_index()

    if st.session_state.segment_index == -1:
        fetch_ordered_segment_sequence()
        render_practice_explanation()
    else:
        fetch_ordered_segment_sequence()

        # Use the segment index to lookup the json index in the ordered_segment_sequence
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
        if st.session_state.segment_content['type'] == 'info':
            render_info()
            render_navigation_buttons()

        elif st.session_state.segment_content['type'] == 'question':
            render_question()
            if st.session_state.submitted:
                # Spinner that displays during evaluating answer
                with st.spinner('Evaluating your answer 🔄'):
                    evaluate_answer()
                render_student_answer()
                render_feedback()
                render_explanation()
                render_SR_nav_buttons()
            else:
                render_answerbox()
                 # Becomes True if user presses ctrl + enter to evaluate answer (instead of pressing "check")
                if st.session_state.student_answer:
                    set_submitted_true()
                    st.rerun()
                render_check_and_nav_buttons()


def select_page_type():
    """
    Determines what type of page to display based on which module the user selected.
    """
    # For convenience, store the selected module name in a variable
    module = st.session_state.selected_module

    # Make module name lowercase and replace spaces and with underscores and cuts off at the first
    module_json_name = module.lower().replace(" ", "_")

    # Load the json content for this module
    with open(f"./modules/{module_json_name}.json", "r") as f:
        st.session_state.page_content = json.load(f)

    # Determine what type of page to display
    if st.session_state.selected_phase == 'learning':
        render_learning_page()
    if st.session_state.selected_phase == 'practice':
        render_practice_page()


def initialise_session_states():
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


def render_logo():
    """
    Place logo in horizontal centre of sidebar with spacer column
    """
    spacer, image_col = st.columns([0.4, 1])
    with image_col:
        st.image('./images/logo.png', width=100)


def determine_modules(): #TODO: change the way the sequence of the modules is determined so it corresponds to the sequence of the course
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
        # Capitalize the first letter of each module
        modules = [module.capitalize() for module in modules]
        st.session_state.modules = modules


def render_sidebar():
    """	
    Function to render the sidebar with the modules and login module.	
    """
    with st.sidebar:
        render_logo()
        st.sidebar.title("Modules")

        # Display the modules in expanders in the sidebar
        for module in st.session_state.modules:
            with st.expander(module):
                # Display buttons for the two types of phases per module
                if st.button('Learning phase 📖', key=module + ' learning'):
                    st.session_state.selected_module = module
                    st.session_state.selected_phase = 'learning'
                if st.button('Practice phase 📝', key=module + ' practice'):
                    st.session_state.selected_module = module
                    st.session_state.selected_phase = 'practice'


def initialise_database():
    """
    Initialise the progress object with the modules and phases in the database.
    """
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": {"authenticated": True}}
    )

    for module in st.session_state.modules:
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

    if st.session_state.currently_testing:
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
            initialise_database()
            return


def fetch_username():
    user_doc = db.users.find_one({'nonce': st.query_params.nonce})
    st.session_state.username = user_doc['username']


def invalidate_nonce():
    db.users.update_one({'username': st.session_state.username}, {'$set': {'nonce': None}})


if __name__ == "__main__":
    # Create a mid column with margins in which everything one a 
    # page is displayed (referenced to mid_col in functions)
    left_col, mid_col, right_col = st.columns([1, 6, 1])
    
    initialise_session_states()

    # Check if user is logged in and if not, go to surfconext log on
    nonce = st.query_params.get('nonce', None)
    if nonce is None: # TODO: refactor all these if statements into more modular design
        st.markdown("Klik [hier](http://localhost:3000/) om in te loggen.")
    else:
        if st.session_state.username is None:
            fetch_username()
            invalidate_nonce()

        # Determine the modules of the current course
        if st.session_state.modules == []:
            determine_modules()
        
        render_sidebar()

        if st.session_state.selected_module is None:         
            # Automatically start the first module if no module is selected           
            st.session_state.selected_module = st.session_state.modules[0] # TODO: this should start at the module where the student left off instead of the first module
            st.session_state.selected_phase = 'learning'
            
            # Rerun to make sure the page is displayed directly after start button is clicked
            st.rerun()
        else:
            # Turn on to reset db every time the webapp is loaded
            # and to prevent openai calls (reduce cost & time to develop)
            st.session_state.currently_testing = False

            # Only (re-)initialise if user is new or when testing is on
            determine_if_to_initialise_database()

            select_page_type()