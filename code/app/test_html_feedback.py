import streamlit as st
score = "0/2"
color = "#FFD6D6"

student_answer = f"""
<h1 style='font-size: 20px; margin: 15px 0 10px 10px; padding: 0;'>Jouw antwoord:</h1>
<div style='background-color: #F5F5F5; padding: 20px; border-radius: 7px; margin-bottom: 0px;'>
    <p style='color: #333; margin: 0px 0'>Uitleg over de natriumkalium pomp behoudt rustpotentiaal door <strong>3 Na+ naar buiten en 2 K+ naar binnen te pompen per ATP</p>
</div>
"""

st.markdown(student_answer, unsafe_allow_html=True)

feedback_content = [
    "✅ Correct: Uitleg over de natriumkalium pomp behoudt rustpotentiaal door <strong>3 Na+ naar buiten en 2 K+ naar binnen te pompen per ATP</strong> (0/1 punten).",
    "❌ Ontbreekt: Vermelding dat dit de <strong>elektrochemische gradiënt</strong> onderhoudt (0/1 punten).",
    "🟨 Deels correct: Basisbegrip aanwezig maar essentiële details missen, benoem <strong>homeostase</strong>."
]

feedback_items = [f"<li style='font-size: 17px; margin: 5px 0; margin-top: 10px'>{feedback}</li>" for feedback in feedback_content]
feedback_html = f"<ul style='padding-left: 0px; list-style-type: none;'>{''.join(feedback_items)}</ul>"

result_html = f"""
<h1 style='font-size: 20px; margin: 25px 0 10px 10px; padding: 0;'>Feedback:</h1>
{feedback_html}
<div style='background-color: {color}; padding: 10px; margin-bottom: 15px; margin-top: 28px; border-radius: 7px; display: flex; align-items: center;'> <!-- Verhoogd naar 50px voor meer ruimte -->
    <h1 style='font-size: 20px; margin: 8px 0 8px 10px; padding: 0;'>Score: {score}</h1>
    <p style='margin: -30px; padding: 0;'>⚠️ Kan afwijken</p>
</div>
"""

st.markdown(result_html, unsafe_allow_html=True)
