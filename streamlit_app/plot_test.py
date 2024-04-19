import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go


# Voorbeeld data
data = {
    'Naam': ['Alice', 'Bob', 'Charlie'],
    'Score': [75, 85, 65],
    'Leeftijd': [25, 30, 35]
}
df = pd.DataFrame(data)

# Maak de tabel
colors = ['rgb(245,245,245)', 'rgb(255,160,122)']
colorscale = [[0, colors[0]], [1, colors[1]]]
fig = ff.create_table(df, colorscale=colorscale)

# Toon de grafiek in Streamlit
st.plotly_chart(fig)


# Voorbeeld data
data = {
    'Naam': ['Naam van rij 1', 'Naam van rij 2', 'Naam van rij 3', 'Anterograde tracers: gebruik om de invloed van een gebied op de rest van het brein in kaart te brengen.'],
    'Rood Segment': [20, 30, 10, 10],
    'Oranje Segment': [30, 20, 40, 10],
    'Groen Segment': [50, 50, 50, 30],
}
df = pd.DataFrame(data)


def wrap_text(text, width):
    """
    Een functie om tekst te wrappen (omloop) door het toevoegen van nieuwe regels.
    
    :param text: De tekst om te wrappen.
    :param width: De breedte waarop de tekst moet wrappen.
    """
    if len(text) <= width:
        return text
    else:
        return '<br>'.join(text[i:i+width] for i in range(0, len(text), width))

# Pas deze functie toe op je y-labels
df['Wrapped Naam'] = df['Naam'].apply(lambda x: wrap_text(x, width=30))  # pas width aan naar behoefte


# Maak de Plotly figuur
fig = go.Figure()

fig.add_trace(go.Bar(
    y=df['Wrapped Naam'],
    x=df['Rood Segment'],
    name='Rood Segment',
    orientation='h',
    marker_color='red'
))

fig.add_trace(go.Bar(
    y=df['Wrapped Naam'],
    x=df['Oranje Segment'],
    orientation='h',
    marker_color='orange'
))

fig.add_trace(go.Bar(
    y=df['Wrapped Naam'],
    x=df['Groen Segment'],
    orientation='h',
    marker_color='green'
))

# Update de layout voor een duidelijke weergave
fig.update_layout(
    barmode='stack',
    xaxis=dict(title='Percentage'),
    yaxis=dict(autorange='reversed'),  # Dit zorgt ervoor dat de labels op de juiste manier worden weergegeven
    margin=dict(l=100, r=20, t=20, b=20),
)

# Toon de grafiek in Streamlit
st.plotly_chart(fig)
