import streamlit as st
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
from pymongo import MongoClient
import certifi
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv()

running_on_premise = False # Set to true if IP adres is allowed by Gerrit

# Database connection
if running_on_premise:
    COSMOS_URI = os.getenv('COSMOS_URI')
    db_client = MongoClient(COSMOS_URI, tlsCAFile=certifi.where())
else:
    MONGO_URI = os.getenv('MONGO_DB')
    db_client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

db = db_client.LearnLoop


def generate_insights(module, question):
    """
    Aggregates the feedback from all users into percentages for 
    each score type (0.0, 0.5, 1.0).
    """
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
    st.write("hello")

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


def parse_answer_items(module, question):
    """Parses the parts of the answer into a list format"""
    answer_items = [
    "Actief transport vereist energie, zoals ATP (1 punt)",
    "om stoffen tegen de concentratiegradi\u00ebnt in te transporteren (1 punt)",
    "terwijl passief transport geen energie vereist (1 punt)"
    ]
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
                    s=f"{parse_answer_items(module, question)[-(i+1)]}", # Reversed walk through answer items
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


if __name__ == "__main__":
    question = "Iets met planten 5" #TODO: make the current_question a session_state attribute in main because use it a lot
    module = "College 1 - Transport"

    perc_df = generate_insights(module, question)
    render_insights(perc_df)