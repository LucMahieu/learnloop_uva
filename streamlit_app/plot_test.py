import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import textwrap

st.set_page_config(layout='wide')

data = {
    'answer_items': [item['item'] for item in st.session_state.segment_content['answer_items']],
    '0.0 score': perc_df['0.0 score'],
    '0.5 score': perc_df['0.5 score'],
    '1.0 score': perc_df['1.0 score']
}

df = pd.DataFrame(data)


# Pas deze functie toe op je y-labels
df['wrapped_items'] = df['answer_items'].apply(lambda text: '<br>'.join(textwrap.wrap(text, width=50)))  # pas width aan naar behoefte


# Maak de Plotly figuur
fig = go.Figure()
bar_width = 0.7

fig.add_trace(go.Bar(
    y=df['wrapped_items'],
    x=df['0.0 score'],
    name='Ontbreekt / Incorrect',
    orientation='h',
    marker_color='red',
    width=bar_width,
))

fig.add_trace(go.Bar(
    y=df['wrapped_items'],
    x=df['0.5 score'],
    name='Gedeeltelijk correct',
    orientation='h',
    marker_color='orange',
    textposition='inside',
    width=bar_width
))

fig.add_trace(go.Bar(
    y=df['wrapped_items'],
    x=df['1.0 score'],
    name='Correct',
    orientation='h',
    marker_color='green',
    textposition='inside',
    width=bar_width
))

# Update de layout voor een duidelijke weergave
fig.update_layout(
    barmode='stack',
    margin=dict(l=20, r=20, t=20, b=20),
    height=450,
    width=1200,
    xaxis=dict(
        tickfont=dict(size=18, color='black'),
    ),
    yaxis=dict(
        tickfont=dict(size=18, color='black'), autorange='reversed'
    )
)

# Toon de grafiek in Streamlit
st.plotly_chart(fig)
