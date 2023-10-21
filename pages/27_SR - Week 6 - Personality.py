import streamlit as st
questions = ['Wat is persoonlijkheid?', 'Wat is een persoonlijkheidstrek?', 'Wat zijn temperamenten?', 'Wat is de vijffactorentheorie?', 'Wat zijn trait-benaderingen?', 'Wat is het Behavioral Approach System (BAS)?', 'Wat is het Behavioral Inhibition System (BIS)?', 'Wat is het Fight-Flight-Freeze System (FFFS)?', 'Wat zijn humanistische benaderingen in persoonlijkheidsstudies?', 'Wat is de locus of control?', 'Wat is wederkerig determinisme (reciprocal determinism)?', 'Wat is ‘Need of cognition’?', 'Wat is situationisme?', 'Wat is interactionisme?', 'Wat zijn idiografische benaderingen?', 'Wat zijn nomothetische benaderingen?', 'Wat zijn projective measures?', 'Wat is een self-schema?', 'Wat is zelfwaardering of self-esteem?', 'Wat is de Sociometer theory?', 'Wat is sociale vergelijking?', 'Wat is self-serving bias?', 'Wat houdt de psychodynamische benadering in?', 'Wat is catharsis in een psychodynamische context?', "Wat is Freud's theorie van persoonlijkheid?", "Wat betekent de term 'inhibited children'?", 'Wie was de meest prominente humanistische psycholoog en wat was zijn bijdrage?', "Wat is 'unconditional positive regard'?", "Wat is de betekenis van 'internal locus of control'?", 'Wat betekent het als mensen een externe locus of control hebben?', 'Wat zijn persoonlijke constructen volgens George Kelly?', 'Wat betekent persoon-situatie interactie?', 'Wat zijn sterke situaties?', 'Wat zijn zwakke situaties?', 'Wat is rank-order stabiliteit?', 'Wat zijn mean-level veranderingen?', 'Wat betekent evaluatief in de context van persoonlijkheidsonderzoek?']
answers = ['Persoonlijkheid verwijst naar de kenmerkende patronen van gedachten, emotionele reacties en gedragingen die stabiel zijn in de tijd en over verschillende situaties. Het is wat ons uniek maakt als individuen.', 'Een persoonlijkheidstrek is een stabiel patroon van denken, voelen en gedrag. Voorbeelden zijn eerlijkheid, optimisme of agressiviteit.', 'Temperamenten zijn biologisch gebaseerde neigingen om op specifieke manieren te handelen of te voelen. Een voorbeeld hiervan is een persoon die van nature uitbundig en energiek is.', 'De vijffactorentheorie stelt voor dat persoonlijkheid kan worden gedefinieerd door vijf factoren: openheid, nauwkeurigheid, extraversie, vriendelijkheid en neuroticisme. Dit wordt ook wel het Big Five-model genoemd.', 'Het elaboration likelihood model is een theorie die suggereert dat overtuigende berichten leiden tot veranderingen in attitudes via ofwel de centrale of perifere route. Dit hangt af van de mate waarin het individu nadenkt over de inhoud van de boodschap. Is de individu gemotiveerd en in de mogelijk om dit te doen, dan gaat het via de centrale route. Is een individu niet gemotiveerd of niet in de mogelijkheid, dan gaat het via de perifere route.', 'Het Behavioral Approach System (BAS) is een hersensysteem dat gedrag stimuleert in reactie op kansen voor beloningen of prikkels. Het is betrokken bij motivatie en het nastreven van aangename ervaringen. Dit is het ‘gaan’ centrum en is onderdeel van de Revised reinforcement sensitivity theory.', 'Het Behavioral Inhibition System (BIS) is een hersensysteem dat de omgeving in de gaten houdt voor potentiële bedreigingen en gedrag remt dat pijn of gevaar kan riskeren. Het is betrokken bij angst en vermijdend gedrag. Dit is het ‘slow down’ centrum en is onderdeel van de Revised reinforcement sensitivity theory.', 'Het Fight-Flight-Freeze System (FFFS) is een hersensysteem dat reageert op bedreigingen door defensief gedrag te initiëren: bevriezen, ontsnappen, of vechten. Het is een fundamenteel onderdeel van onze overlevingsreactie.', 'Humanistische benaderingen leggen de nadruk op zelfactualisatie en zelfbegrip om persoonlijkheid te bestuderen. Ze kijken naar hoe individuen hun volledig potentieel kunnen bereiken en begrijpen. Verschillen in persoonlijkheid kunnen verklaard worden door waar ze staan in de Maslow’s piramide: ‘the hierarchy of needs’. ', 'De locus of control verwijst naar de overtuigingen over de mate van controle die iemand heeft over de uitkomsten in zijn of haar leven. Bijvoorbeeld, iemand met een interne locus of control gelooft dat zij controle hebben over hun eigen leven.', 'Wederkerig determinisme is een theorie die stelt dat iemands gedragingen worden beïnvloed door drie factoren: de omgeving, verschillende persoonlijke factoren (zoals verwachtingen, eigenschappen, zelfvertrouwen) en het gedrag zelf. ', '‘Need of cognition’ is de neiging om complexe cognitieve activiteiten te ondernemen en ervan te genieten, zoals het oplossen van puzzels of kritisch denken.', 'Situationisme is de theorie dat situationele factoren, meer dan persoonlijkheidstrekken, gedrag bepalen. Dit betekent dat de omgeving waarin iemand zich bevindt, een grotere invloed kan hebben op hun gedrag dan hun persoonlijkheid.', 'Interactionisme is de theorie dat zowel situaties als persoonlijkheidstrekken gezamenlijk gedrag bepalen. Het stelt dat gedrag het resultaat is van de interactie tussen persoonlijke kenmerken en de omgeving.', 'Idiografische benaderingen richten zich op het begrijpen van de complexiteit van de individuele persoonlijkheid, waarbij ze meer kijken naar de unieke aspecten van een persoon dan naar algemene kenmerken. Hierbij zou de onderzoeker bijvoorbeeld tien mensen vragen om persoonlijkheidstrekken op te schrijven die ze bij zichzelf vinden passen. ', 'Nomothetische benaderingen richten zich op algemene persoonlijkheidskenmerken die over individuen heen kunnen worden gezien, zoals de neiging om extravert of introvert te zijn. Hierbij zou de onderzoeker mensen een vragenlijst geven met honderd persoonlijkheidstrekken waar ze zichzelf op kunnen scoren tussen de één en tien.', 'Projective measures zijn persoonlijkheidstests die reageren op dubbelzinnige prikkels, vaak gebruikt om onbewuste processen te beoordelen. Bijvoorbeeld de Rorschach-inktvlektest, waarbij individuen hun interpretaties van ongestructureerde inktvlekken geven.', 'Een self-schema is een cognitieve structuur die kennis, overtuigingen en herinneringen over jezelf organiseert. Het helpt bijvoorbeeld bij het snel verwerken van informatie die relevant is voor onszelf.', 'Self-esteem is een evaluatief aspect van zelfperceptie waarbij individuen zich waardevol of niet kunnen voelen. Het is nauw verbonden met hoe we ons voelen over onze prestaties en capaciteiten.', 'De sociometer theory stelt dat zelfvertrouwen dient als een sociometer: een interne meter die het niveau van sociale acceptatie of afwijzing monitort. Het helpt ons te bepalen hoe goed we passen in onze sociale omgeving en of we risico lopen op uitsluiting.', "Sociale vergelijking is het proces van het evalueren van je eigen vaardigheden, acties en overtuigingen door ze te contrasteren met die van anderen. Bijvoorbeeld, iemand kan zijn loopbaanvoortgang beoordelen door deze te vergelijken met collega's.", 'Self-serving bias is de neiging om successen toe te schrijven aan zichzelf en mislukkingen aan externe factoren. Bijvoorbeeld, als we slagen voor een test, kan het zijn omdat we slim zijn. Maar als we falen, is het misschien omdat de test te moeilijk was.', 'De psychodynamische benadering stelt dat persoonlijkheid voortkomt uit onbewuste conflicten en verlangens, die veelal hun oorsprong hebben in vroege kinderervaringen. Om iemand echt te kennen, moet je de onderliggende dynamiek begrijpen.', 'Catharsis is het vrijmaken van onderdrukte herinneringen, een belangrijk doel van psychodynamische behandelingen. Het kan moeilijk zijn omdat er weerstand is; deze herinneringen veroorzaken vaak angst, daarom zijn ze in eerste instantie onderdrukt.', "Freud's persoonlijkheidstheorie verdeelt de menselijke persoonlijkheid in drie subsystemen: het ID, dat biologische driften bevat; het ego, dat voortkomt uit het ID wanneer het wordt geconfronteerd met de realiteit; en het superego, dat afgeleid is van het ego en fungeert als een geïnternaliseerde gedragscode.", "'Inhibited children' verwijst naar de persoonsgerichte benadering in de psychologie.", 'Carl Rogers was de meest prominente humanistische psycholoog. Hij introduceerde de mensgerichte benadering van persoonlijkheid en menselijke relaties, waarbij hij de subjectieve ervaringen van mensen benadrukte.', "'Unconditional positive regard' is een concept geïntroduceerd door Carl Rogers, waarbij ouders hun kinderen accepteren en waarderen, ongeacht hun gedrag. Volgens Rogers zou een kind dat op deze manier wordt opgevoed, een gezond gevoel van eigenwaarde ontwikkelen en een volledig functionerend persoon worden.", "Mensen met een 'internal locus of control' geloven dat ze hun eigen beloningen creëren. Dit staat in contrast met een 'external locus of control', waar men gelooft dat externe factoren verantwoordelijk zijn voor de uitkomst van gebeurtenissen.", 'Personen met een externe locus of control geloven dat beloningen en dus hun persoonlijke lot, het resultaat zijn van krachten buiten hun controle. Deze overtuigingen beïnvloeden het gedrag van individuen en hun psychologische aanpassingsniveau.', 'Persoonlijke constructen zijn de persoonlijke theorieën die individuen hebben over hoe de wereld werkt. Kelly geloofde dat mensen de wereld zien als wetenschappers, die hun theorieën constant testen door lopende gebeurtenissen te observeren en deze theorieën te herzien op basis van wat ze waarnemen.', 'De kern van deze theorie is dat mensen op voorspelbare manieren reageren op specifieke omstandigheden. Als er bijvoorbeeld een beloning is, dan ben ik enthousiast om die na te streven. Als de uitkomst onzeker is, dan maak ik me daar zorgen over.', 'Sterke situaties, zoals vliegtuigen, religieuze diensten, sollicitatiegesprekken, hebben de neiging om verschillen in persoonlijkheid te verbloemen vanwege de kracht van de sociale omgeving.', 'Zwakke situaties, zoals parken, bars of iemands huis, neigen ertoe om verschillen in persoonlijkheid te onthullen.', 'Rank-order stabiliteit verwijst naar de stabiliteit in persoonlijkheid die betrekking heeft op het gebrek aan verandering in iemands positie op een eigenschap ten opzichte van andere mensen. Bijvoorbeeld, de relatieve rangschikking van individuen op elk van de Big Five-persoonlijkheidstrekken blijft stabiel over vele jaren.', 'Mean-level veranderingen verwijzen naar veranderingen in persoonlijkheid die veel mensen ervaren op dezelfde levensfasen, ook al blijft hun rangorde stabiel. Bijvoorbeeld, mensen worden doorgaans minder neurotisch, minder open voor nieuwe ervaringen; meer aangenaam en meer gewetensvol.', 'Evaluatieve eigenschappen verwijzen naar aspecten van iemands persoonlijkheid waarover men blind is omdat men zichzelf graag in een positief licht ziet. Dit is vooral waar voor eigenschappen die zeer gewaardeerd worden in de samenleving, zoals creativiteit.']


def change_card_index(index):
    # Select first element and re-insert at index
    st.session_state.questions.insert(index, st.session_state.questions[0])
    st.session_state.answers.insert(index, st.session_state.answers[0])

    # Delete the first duplicate card
    del st.session_state.questions[0]
    del st.session_state.answers[0]

    return


def evaluate_graduation(current_card):
    if current_card in st.session_state.easy_count:
        st.session_state.easy_count[current_card] += 1
    else:
        st.session_state.easy_count[current_card] = 1

    # Delete card if graduated
    if st.session_state.easy_count[current_card] >= 2:
        del st.session_state.questions[0]
        del st.session_state.answers[0]
    else:
        change_card_index(20)

    return


def reset_easy_count(current_card):
    st.session_state.easy_count[current_card] = 0


# -------------------------SESSION STATES----------------------------- #

if 'easy_count' not in st.session_state:
    st.session_state.easy_count = {}

if 'questions' not in st.session_state:
    st.session_state.questions = None

if 'answers' not in st.session_state:
    st.session_state.answers = None

if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

if 'previous_page_name' not in st.session_state:
    st.session_state.previous_page_name = None

if 'current_page_name' not in st.session_state:
    st.session_state.current_page_name = __file__

# -------------------------------MAIN---------------------------------- #


def initialise_new_page():
    st.session_state.questions = questions.copy()
    st.session_state.answers = answers.copy()
    st.session_state.easy_count = {}
    return


# Read and store current file name
st.session_state.current_page_name = __file__

# Check if a new page is opened
if st.session_state.current_page_name != st.session_state.previous_page_name:
    # Change lists in session state with current week lists
    initialise_new_page()
    st.session_state.previous_page_name = st.session_state.current_page_name


card_progress = st.progress(0)
main_container = st.container()

with main_container:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Easy', use_container_width=True):
            # Count executive times the user found current card easy
            evaluate_graduation(st.session_state.questions[0])
            st.session_state.show_answer = False

    with col2:
        if st.button('Medium', use_container_width=True):
            st.session_state.show_answer = False
            reset_easy_count(st.session_state.questions[0])
            change_card_index(5)

    with col3:
        if st.button('Hard', use_container_width=True):
            st.session_state.show_answer = False
            reset_easy_count(st.session_state.questions[0])
            change_card_index(2)


if st.button('Show Answer', use_container_width=True):
    st.session_state.show_answer = not st.session_state.show_answer

if len(st.session_state.questions) == 0:
    st.session_state.questions = questions.copy()
    st.session_state.answers = answers.copy()
    st.session_state.easy_count = {}

st.subheader(st.session_state.questions[0])
if st.session_state.show_answer:
    st.write(st.session_state.answers[0])

card_progress.progress(int(sum(st.session_state.easy_count.values()) / (2 * len(questions)) * 100))