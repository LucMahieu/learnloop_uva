import openai
from PyPDF2 import PdfReader
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import (SystemMessagePromptTemplate, HumanMessagePromptTemplate,
                               ChatPromptTemplate)
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks import get_openai_callback
from langchain.chains.openai_functions.extraction import create_extraction_chain
from dotenv import load_dotenv
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("Learnloop")
"""
Met Learnloop kun je de onderwerpen uit hoorcolleges op een effectievere manier leren doordat Learnloop automatisch de 
onderwerpen uit het hoorcollege haalt, deze aanvult en fact-checked met het boek en over die kennis flashcards maakt.

Stappen:
1. Upload je slides van een hoorcollege
2. Upload het boek dat hoort bij het vak
3. De slides worden automatisch omgezet tot flashcards. ***De verwerking hiervan kan enkele minuten duren.***
"""

main_container = st.container()
sub_container = st.container()

slide_upload = st.file_uploader("Upload hoorcollegeslides", type='pdf')
book_upload = st.file_uploader("Upload boek", type='pdf')
llm3 = ChatOpenAI(model_name="gpt-3.5-turbo")


def pdf_reader(uploaded_pdf):
    reader = PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


@st.cache_data
def embed_book(book_upload):
    book_text = pdf_reader(book_upload)
    book_chunks = create_chunks(book_text)
    vector_store = embed_chunks(book_chunks)
    return vector_store


def create_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400, length_function=len)
    chunks = text_splitter.create_documents([text])
    # st.write(f"The document was divided into {len(chunks)} chunks.")
    return chunks


@st.cache_resource
def embed_chunks(_chunks):
    with get_openai_callback() as cb:
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(documents=_chunks, embedding=embeddings)
    # st.write("Vector Store successfully created")
    print(cb)
    return vector_store


@st.cache_resource
def extract_topics(_chunks):
    # map_template = """
    #            De gegeven tekst is geëxtraheerd uit de collegeslides van een hoorcollege. Jouw doel is om te bepalen wat
    #            de onderwerpen en subonderwerpen zijn van dit hoorcollege. Vervolgens moet je bij elk onderwerp en
    #            subonderwerp context geven van één of twee zinnen. Geef je antwoord in het volgende format:
    #
    #            % BEGIN VOORBEELDFORMAT
    #
    #            > Hoofdonderwerp: context
    #            > 1. Onderwerp: context
    #            > > 1.1 Onderwerp: context
    #            > > > 1.1.1 Subonderwerp: context
    #            > > 1.2 Onderwerp: context
    #            > 2 Onderwerp: context
    #            > > 2.1 Onderwerp: context
    #            > > 2.2 Onderwerp: context
    #            > > > 2.2.1 Subonderwerp: context
    #            > > 2.3 Onderwerp: context
    #            > 3 Onderwerp: context
    #
    #            % EINDE VOORBEELDFORMAT
    #        """
    map_template = """
               De gegeven tekst is geëxtraheerd uit hoorcollegeslides. Jouw doel is om de onderwerpen en 
               subonderwerpen te extraheren en organiseren op basis van hun abstractieniveau in een lijst vorm zoals 
               in het voorbeeld hieronder:

#BEGIN VOORBEELD

Input:

Neuromechanics & Motor control
(BM41040)
Lecture 10: Sensory Integration
25-03-2022
Winfred Mugge, BioMechanical Engineering

Poll!
What is your current association with the term
"Sensory Integration"?

4 |

Challenges in Human Movement Control
• How do we control our limbs?
• Sensory Integration!
Franklin and Wolpert (2011)
Scott, 2004

5 |

Challenges in Human Movement Control
• Redundancy
• 600 muscles controlling 200 joints
• Noise
• Sensor and motor noise
• Delays
• Neural transportation and processing
• Uncertainty
• Incomplete knowledge of environment
• Nonstationarity
• Growth, fatigue, and aging
• Nonlinearity
• Mapping between muscles vs. endpoint
And what about
robot control?

6 |

Redundancy
• Muscle redundancy
• More muscles than DoF
• Kinematic redundancy
• Multiple paths to same position
• Postures with same hand position
• Sensor redundancy
• Multiple sensors measure same
variable

7|

output:

Neuromechanics & Motor control

>Sensory Integration
>>Challenges in Human Movement Control
>>>Redundancy: 600 muscles controlling 200 joints
>>>Noise: Sensor and motor noise
>>>Delays: Neural transportation and processing
>>>Uncertainty: Incomplete knowledge of environment
>>>Nonstationarity: Growth, fatigue, and aging
>>>Nonlinearity: Mapping between muscles vs. endpoint
>>>>Redundancy
>>>>>Muscle redundancy: more muscles than DoF
>>>>>Kinematic redundancy: 
>>>>>>Multiple paths to same position
>>>>>>Postures with same hand position
>>>>>Sensor redundancy: multiple sensors measure same variable

#EINDE VOORBEELD

input:
"""

    system_message_map_prompt = SystemMessagePromptTemplate.from_template(map_template)

    human_template = "Hoorcollegeslides: {text}"
    human_message_map_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_map_prompt = ChatPromptTemplate.from_messages(
        messages=[system_message_map_prompt, human_message_map_prompt])

    # Combine messages and prompts
    # combine_template = """
    #            De gegeven tekst is geëxtraheerd uit de collegeslides van een hoorcollege. Jouw doel is om te bepalen wat
    #            de onderwerpen en subonderwerpen van dit hoorcollege zijn en de daarbij horende content om deze vervolgens
    #            in het onderstaande format te formatteren. Verwijder onderwerpen die dubbel voorkomen.
    #
    #            % BEGIN VOORBEELDFORMAT
    #
    #            > Hoofdonderwerp: context
    #            > 1. Onderwerp: context
    #            > > 1.1 Onderwerp: context
    #            > > > 1.1.1 Subonderwerp: context
    #            > > 1.2 Onderwerp: context
    #            > 2 Onderwerp: context
    #            > > 2.1 Onderwerp: context
    #            > > 2.2 Onderwerp: context
    #            > > > 2.2.1 Subonderwerp: context
    #            > > 2.3 Onderwerp: context
    #            > 3 Onderwerp: context
    #
    #            % EINDE VOORBEELDFORMAT
    #        """
    combine_template = """
                       De gegeven tekst is geëxtraheerd uit hoorcollegeslides. Jouw doel is om de onderwerpen en 
                       subonderwerpen te extraheren en organiseren op basis van hun abstractieniveau in een lijst vorm zoals 
                       in het voorbeeld hieronder:

                        #BEGIN VOORBEELD

                        Input:

                        Neuromechanics & Motor control
                        (BM41040)
                        Lecture 10: Sensory Integration
                        25-03-2022
                        Winfred Mugge, BioMechanical Engineering

                        Poll!
                        What is your current association with the term
                        "Sensory Integration"?

                        4 |

                        Challenges in Human Movement Control
                        • How do we control our limbs?
                        • Sensory Integration!
                        Franklin and Wolpert (2011)
                        Scott, 2004

                        5 |

                        Challenges in Human Movement Control
                        • Redundancy
                        • 600 muscles controlling 200 joints
                        • Noise
                        • Sensor and motor noise
                        • Delays
                        • Neural transportation and processing
                        • Uncertainty
                        • Incomplete knowledge of environment
                        • Nonstationarity
                        • Growth, fatigue, and aging
                        • Nonlinearity
                        • Mapping between muscles vs. endpoint
                        And what about
                        robot control?

                        6 |

                        Redundancy
                        • Muscle redundancy
                        • More muscles than DoF
                        • Kinematic redundancy
                        • Multiple paths to same position
                        • Postures with same hand position
                        • Sensor redundancy
                        • Multiple sensors measure same
                        variable

                        7|

                        output:

                        Neuromechanics & Motor control

                        >Sensory Integration
                        >>Challenges in Human Movement Control
                        >>>Redundancy: 600 muscles controlling 200 joints
                        >>>Noise: Sensor and motor noise
                        >>>Delays: Neural transportation and processing
                        >>>Uncertainty: Incomplete knowledge of environment
                        >>>Nonstationarity: Growth, fatigue, and aging
                        >>>Nonlinearity: Mapping between muscles vs. endpoint
                        >>>>Redundancy
                        >>>>>Muscle redundancy: more muscles than DoF
                        >>>>>Kinematic redundancy: 
                        >>>>>>Multiple paths to same position
                        >>>>>>Postures with same hand position
                        >>>>>Sensor redundancy: multiple sensors measure same variable

                        #EINDE VOORBEELD

                        input:
                        """

    system_message_combine_prompt = SystemMessagePromptTemplate.from_template(combine_template)

    human_template = "Hoorcollegeslides: {text}"
    human_message_combine_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_combine_prompt = ChatPromptTemplate.from_messages(
        messages=[system_message_combine_prompt, human_message_combine_prompt])

    chain = load_summarize_chain(
        llm3, chain_type="map_reduce", map_prompt=chat_map_prompt,
        combine_prompt=chat_combine_prompt, reduce_llm=llm3)

    with get_openai_callback() as cb:
        topics_found = chain.run({"input_documents": _chunks})
    print(cb)

    return topics_found


@st.cache_resource
def structure_topics(_topics_found):
    with get_openai_callback() as cb:
        structure = {
            "properties": {
                "topic_naam": {
                    "type": 'string',
                    "description": "onderwerp weergegeven in één of een aantal woorden"
                },
                "lijst_nummer": {
                    "type": 'string',
                    "description": """nummer van het (sub)onderwerp in de lijst  in één van de volgende formats:
                    x
                    x.x
                    x.x.x
                    x.x.x.x
                    """
                }
            },
            "required": ["topic_naam", "index"],
        }
        chain = create_extraction_chain(structure, llm3)
        topics_structured = chain.run(_topics_found)
    print(cb)
    return topics_structured


@st.cache_resource
def expand_topics(_topics_structured, _vector_store):
    system_template = """
    Je krijgt een tekst waarin meerdere onderwerpen besproken worden en een vraag van de gebruiker over één van die onderwerpen.
    Jouw doel is om met de informatie uit de tekst een samenvatting te schrijven over het onderwerp waar gebruiker naar vraagt.
    De samenvatting mag maximaal 2 zinnen lang zijn.
    Reageer alleen met informatie die direct betrekking heeft op het onderwerp en niet meer.
    ------------------
    {context}
    """

    messages = [SystemMessagePromptTemplate.from_template(system_template),
                HumanMessagePromptTemplate.from_template("{question}")]
    chat_prompt = ChatPromptTemplate.from_messages(messages=messages)

    expand_chain = RetrievalQA.from_chain_type(llm3, chain_type="stuff", retriever=_vector_store.as_retriever(),
                                               chain_type_kwargs={'verbose': False, 'prompt': chat_prompt})
    expanded_topics = []

    for topic in _topics_structured:
        query = f"""{topic["topic_naam"]}"""
        with get_openai_callback() as cb:
            topic_expanded = expand_chain.run(query)
        print(cb)
        expanded_topics.append(topic_expanded)

    return expanded_topics


@st.cache_resource
def generate_flashcards(_topics, _topics_expanded):
    flashcard_count = 1
    generated_flashcards = []
    for topic_en_lijstnummer, topic_context in zip(_topics, _topics_expanded):
        if flashcard_count > 1:
            s = "s"
        else:
            s = ''
        st.write(f"{flashcard_count} flashcard{s} generated from the {len(_topics)}")
        topic = f"""{topic_en_lijstnummer["topic_naam"]}"""
        messages = [
            {"role": "system", "content": f"""
                Creëer 1 vraag en antwoord die specifiek en uitsluitend gaan over {topic} binnen de gegeven context {topic_context} in een flashcard format waarbij je eerst de vraag op de voorkant van de flashcard schrijft, gevolgd door een puntkomma (;) en daarna het antwoord op de vraag aan de achterkant van de flashcard.

    Input:

    1. Rol van ouders bij het aanleren van migratiegedrag: Bij sommige vogelsoorten leren jongen van hun ouders hoe ze moeten migreren, inclusief de route en bestemming. Ouders spelen een cruciale rol bij het doorgeven van deze informatie aan hun nakomelingen.
    2. Genetische aanleg en instinct: Er is een genetische basis voor migratiegedrag bij vogels, wat impliceert dat het deels instinctief is en vastgelegd in hun genen. Sommige vogels hebben van nature de neiging om te migreren, terwijl andere binnen dezelfde soort dit gedrag niet vertonen.
    3. Voordelen van migratie voor individuen en fitheid: Vogels migreren omdat het hen in staat stelt hun overlevingskansen en reproductief succes te vergroten. Migratie stelt individuen in staat om gunstige broedplaatsen te vinden, voedselbronnen te exploiteren en de risico's van extreme omstandigheden te vermijden.
    4. Vragen van Tinbergen over verklaringen in de biologie: Niko Tinbergen stelde vier vragen die worden gebruikt om gedrag te analyseren en te verklaren: 1) Wat is de causale basis van het gedrag? 2) Wat is de functie of het evolutionaire voordeel ervan? 3) Hoe ontwikkelt het gedrag zich binnen het individu? 4) Hoe beïnvloedt het gedrag de interacties tussen individuen en de populatie als geheel? Deze vragen helpen onderzoekers bij het begrijpen van gedrag en migratie in de context van evolutionaire biologie.

    Output:
    Hoe leren vogels migreren?; Ouders geven informatie over de migratieroute en bestemming door aan hun nakomelingen.
    Wat is de rol van genetica bij vogelmigratie?; Migratiegedrag bij vogels is deels instinctief door bepaalde genen en deels aangeleerd gedrag.
    Waarom migreren vogels?; Om broedplaatsen en voedselbronnen te vinden en om extreme omstandigheden te vermijden.
    Welke aspecten van gedrag onderzocht Niko Tinbergen om gedrag te analyseren?; 1) Causale basis van het gedrag 2) De functie of het evolutionaire voordeel ervan 3) Ontwikkeling van het gedrag binnen een individu 4) De invloed van het gedrag op interacties met andere individuën.
    Welke factoren spelen een rol in de causale basis van gedrag?; Interne factoren, zoals genetica en fysiologie en externe factoren, zoals stimuli uit de omgeving.
    Hoe bepaal je de functie of het evolutionaire voordeel van gedrag?; Gedrag en de voordelen daarvan observeren in termen van overleving, voortplanting en fitness.

    Input:
    <topic>
                """},
            {"role": "user", "content": f"""
                Maak 1 Anki flashcard die specifiek en uitsluitend gaat over {topic} binnen de gegeven context {topic_context}
                """}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=messages
        )
        flashcard_response = response['choices'][0]['message']['content']
        generated_flashcards.append(flashcard_response)
        flashcard_count += 1
        # st.write(topic)
        # st.write(flashcard_response)

    # Split list with flashcards into two separate lists with questions and answers
    flashcard_questions = []
    flashcard_answers = []
    for cards in generated_flashcards:
        side = cards.split(";")
        flashcard_questions.append(side[0])
        flashcard_answers.append(side[1])
    return flashcard_questions, flashcard_answers


if __name__ == '__main__':
    if slide_upload is not None:
        current_pdf_name = slide_upload.name[:-4]
        if 'previous_pdf_name' not in st.session_state:
            st.session_state.previous_pdf_name = current_pdf_name
        else:
            if st.session_state.previous_pdf_name == current_pdf_name:
                pass
            else:
                st.cache_resource.clear()
                st.session_state.previous_pdf_name = current_pdf_name

        slide_texts = pdf_reader(slide_upload)
        slide_chunks = create_chunks(slide_texts)
        slide_topics = extract_topics(slide_chunks)
        # st.title("Knowledge Tree")
        # st.write(slide_topics)
        slide_topics_structured = structure_topics(slide_topics)
        # st.write(slide_topics_structured)

        if book_upload is not None:
            book_vectors = embed_book(book_upload)
            slide_topics_expanded = expand_topics(slide_topics_structured, book_vectors)
            # st.write(slide_topics_expanded)
            flashcards = generate_flashcards(slide_topics_structured, slide_topics_expanded)
            flashcards_questions = flashcards[0]
            flashcards_answers = flashcards[1]
            # st.write(flashcards)
            # st.write(flashcards_questions)
            # st.write(flashcards_answers)

            if 'count' not in st.session_state:
                st.session_state.count = 0


            # st.write(st.session_state.count)

            def increment_counter(increment_value):

                if increment_value > 0:
                    if st.session_state.count < len(flashcards_questions) - 1:
                        st.session_state.count += increment_value
                    else:
                        st.session_state.count = 0
                else:
                    if st.session_state.count <= 0:
                        st.session_state.count = len(flashcards_questions) - 1
                    else:
                        st.session_state.count += increment_value


            def answer():
                main_container.write(flashcards_answers[st.session_state.count])


            main_container.write("\n\n" + "\n----------------------\n" + "\n\n")
            main_container.header(slide_topics_structured[0]["topic_naam"])

            main_container.write(flashcards_questions[st.session_state.count])

            col1, col2, col3 = sub_container.columns(3)

            with col1:
                previous_question = st.button("Previous", on_click=increment_counter, args=(-1,))

            with col2:
                answer_button = st.button("Show Answer", on_click=answer)

            with col3:
                next_button = st.button("Next", on_click=increment_counter, args=(1,))
