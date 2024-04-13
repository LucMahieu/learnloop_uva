import time
import random
import streamlit as st
from dotenv import load_dotenv
import os
import json
from openai import AzureOpenAI
from pymongo import MongoClient
import certifi
import base64
import pandas as pd
import matplotlib as plt

# Must be called first
st.set_page_config(page_title="LearnLoop", layout="wide")

# Settings
st.session_state.currently_testing = False # Turn on to reset db every time the webapp is loaded and minimize openai costs
running_on_premise = True # Set to true if IP adres is allowed by Gerrit

load_dotenv()

# Database connection
if running_on_premise:
    COSMOS_URI = os.getenv('COSMOS_URI')
    db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
else:
    MONGO_URI = os.getenv('MONGO_DB')
    db_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

openai_client = AzureOpenAI(
   api_key=os.getenv("OPENAI_API_KEY"),  
   api_version="2024-03-01-preview",
   azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

db = db_client.LearnLoop

# Ping database to check if it's connected
try:
    db.command("ping")
    print("Connected to database")
except Exception as e:
    print(f"Error: {e}")


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


def determine_phase_length():
    if st.session_state.selected_phase == 'practice':
        return len(st.session_state.ordered_segment_sequence)
    else:
        return len(st.session_state.page_content["segments"])


def render_explanation():
    with st.expander("Antwoordmodel"):
        st.markdown(st.session_state.segment_content['answer'])


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
        st.button('Generate', use_container_width=True, on_click=set_submitted_true)
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
    

def render_question():
    """Function to render the question and textbox for the students answer."""
    st.title(st.session_state.segment_content['question'])


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


def reset_progress():
    """Resets the progress of the user in the current phase to the database."""
    db.users.update_one(
        {"username": st.session_state.username},
        {"$set": {f"progress.{st.session_state.selected_module}.{st.session_state.selected_phase}.segment_index": -1}}
    )


def generate_insights():
    """
    Aggregates the feedback from all users into percentages for 
    each score type (0.0, 0.5, 1.0).
    """
    module = st.session_state.selected_module
    question = st.session_state.segment_content['question']

    feedback_path = f"progress.{module}.feedback.{question}"
    st.write(feedback_path)

    # A feedback cursor is not a JSON object, but a collection of JSON objects
    feedback_cursor = db.users.find(
        {
            feedback_path: {"$exists": True, "$not": {"$size":  0}} # Check if the path exists and has a value other then 0
        },
        {
            feedback_path: 1 # Boolean to tell that you want to project (output) this path
        }
    )

    # Put all feedback data in a list
    flat_feedback_list = []
    for feedback_doc in feedback_cursor:
        st.write(feedback_doc)
        feedback_items = feedback_doc['progress'][module]['feedback'][question]
        for i, item in enumerate(feedback_items):
            flat_feedback_list.append({'feedback_item': i+1, 'score': item['score'], 'feedback': item['feedback']})

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
    st.write(perc_df)

    return perc_df


def extract_score(index, score_type, perc_df):
    """
    Extract the occurrence of the score type from df and convert 
    percentage to the right ratio of the bar graph.
    """
    total_bar_length = 6
    return int(perc_df.loc[index, score_type].item()) * total_bar_length / 100


def parse_answer_items():
    """Parses the parts of the answer into a list format"""
    answer_items = st.session_state.segment_content['answer'].split(' (1 punt)')
    return answer_items


def render_insights(perc_df):
    bar_segments = []
    for index in perc_df.index:
        # Define the segments of each bar
        # Each tuple consists of (length, color)
        bar_segments.append(
            [
                (extract_score(index, '0.0 score', perc_df), '#c0e7c0'),
                (extract_score(index, '0.5 score', perc_df), '#f7d4b6'), 
                (extract_score(index, '1.0 score', perc_df), '#e5bbbb')
            ]
        )

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(6, 3))

    # Starting position of first bar
    bottom_bar_pos = 3
    bar_height = 0.5 # Thickness

    # Create each bar with its bar segments
    for bar in bar_segments:
        left = 0  # Starting left position for each bar
        for i, segment in enumerate(bar):
            length, color = segment
            # Draw each segment
            rect = plt.Rectangle((left, bottom_bar_pos), length, bar_height, color=color)

            ax.text(y=0.65 + i * 1.5, # The spacing between the answer items
                    x=0, 
                    s=f"{parse_answer_items()[-(i+1)]}", # Reversed walk through answer items
                    fontsize=10
            )

            ax.add_patch(rect)
            # Update the left position for the next segment
            left += length
        # Update the starting bottom position for the next bar
        bottom_bar_pos -= 1.5

    total_bar_length = 6
    ax.set_xlim(0, total_bar_length)
    ax.set_ylim(0, 4)
    ax.axis('off') # Remove axes

    # Show the plot
    st.pyplot(fig)


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
        if st.session_state.submitted:
            # Render image if present in the feedback
            image_path = fetch_image_path()
            if image_path:
                render_image(image_path)

            render_question()
            perc_df = generate_insights()
            render_insights(perc_df)

            render_navigation_buttons()
        else:
            image_path = fetch_image_path()
            if image_path:
                render_image(image_path)
            
            render_question()            
            render_check_and_nav_buttons()


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
        render_learning_page()


def initialise_session_states():
    if 'info_page' not in st.session_state:
        st.session_state.info_page = False
    
    if 'feedback_submitted' not in st.session_state:
        st.session_state.feedback_submitted = False

    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'old_page' not in st.session_state:
        st.session_state.old_page = None

    if 'current_page' not in st.session_state:
        st.session_state.current_page = None

    if 'selected_phase' not in st.session_state:
        st.session_state.selected_phase = None

    if 'page_content' not in st.session_state:
        st.session_state.page_content = None

    if 'segment_index' not in st.session_state:
        st.session_state.segment_index = 0

    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = None
    
    if 'modules' not in st.session_state:
        st.session_state.modules = []

    if 'segment_content' not in st.session_state:
        st.session_state.segment_content = None

    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
        
    if 'score' not in st.session_state:
        st.session_state.score = ""

    if 'feedback' not in st.session_state:
        st.session_state.feedback = ""


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
                if st.button('Oefenfase 📝', key=module + ' practice'):
                    st.session_state.selected_module = module
                    st.session_state.selected_phase = 'practice'
                    st.session_state.info_page = False
                    track_visits()
                if st.button('Theorie 📚', key=module + ' theory'):
                    st.session_state.selected_module = module
                    st.session_state.selected_phase = 'theory'
                    st.session_state.info_page = False
                    track_visits()

        render_feedback_form()

        st.sidebar.subheader("Extra info")
        st.button("Uitleg mogelijkheden & limitaties LLM's", on_click=set_info_page_true, use_container_width=True, key="info_button_sidebar")


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
            initialise_module_in_database(module)
            return


def convert_image_base64(image_path):
    """Converts image in working dir to base64 format so it is 
    compatible with html."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


if __name__ == "__main__":
    # Create a mid column with margins in which everything one a 
    # page is displayed (referenced to mid_col in functions)
    left_col, mid_col, right_col = st.columns([1, 3, 1])
    
    initialise_session_states()

    if not running_on_premise:
        st.session_state.username = "test_user"

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

            select_page_type()
