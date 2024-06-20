import json
import streamlit as st


def toggle_button(segment_id):
    if st.session_state['button_state'+segment_id] == 'no':
        st.session_state['button_state'+segment_id] = 'yes'
    else:
        st.session_state['button_state'+segment_id] = 'no'



def save_st_change(key1,key2):
    st.session_state[key1] = st.session_state[key2]

def list_to_enumeration(list_input):
    enumeration_output = ""
    for count, elem in enumerate(list_input):
        enumeration_output+= f"{str(count+1)}) {elem}\n"
    return enumeration_output

def enumeration_to_list(enumeration_input):
    list_output = enumeration_input.split("\n")
    list_output = [ x.split(')', 1)[1].strip() for x in list_output if x!="" ]
    return list_output

def original_topics(module) -> list:
    with open(f'src/data/modules/topics/{module}_topics.json') as f:
        data_modules = json.load(f)
    topics = data_modules['topics']
    return topics

def original_segments(module) -> list:
    with open(f'src/data/modules/{module}.json') as f:
        data_modules = json.load(f)
    segments = data_modules['segments']
    return segments

def key_func(k):
    return k["segment_id"]

def preprocessed_segments(module) -> list:
    # outputs a list of dictionaries with detele:yes or delete:no tags.
    original_segments_list = original_segments(module)
    segments_list = []
    session_state_dict = {k: v for k, v in st.session_state.items()}
    for key, value in session_state_dict.items():
        composite_key = key.split("-")
        if composite_key[0]=="new":
            segment_id = int(composite_key[1])
            segment = {}
            segment["segment_id"] = segment_id
            static_segment = original_segments_list[segment_id] 
            if static_segment["type"]== "theory":
                segment["text"] = value
            elif static_segment["type"] == "question" and len(composite_key)==2:
                segment["question"] = value
            elif static_segment["type"] == "question" and len(composite_key)==3:
                segment["answer"] = value
            elif static_segment["type"] == "question" and len(composite_key)==4:
                segment["answers"] = {}
                if composite_key[3] == "correct_answer":
                    segment["answers"]["correct_answer"] = value
                elif composite_key[3] == "wrong_answers":
                    segment["answers"]["wrong_answers"] = enumeration_to_list(value)
            segments_list.append(segment)
    segments_list  = sorted(segments_list, key=key_func)
    new_segments_list =  original_segments_list
    for segment_id, segment in enumerate(new_segments_list):
        if segment["type"]== "theory":
            new_segments_list[segment_id]["text"] = [ x for x in segments_list if x["segment_id"] == segment_id ][0]["text"]
        elif segment["type"] == "question":
            new_segments_list[segment_id]["question"] = [x for x in segments_list if x["segment_id"] == segment_id and "question" in x][0]["question"]
            if "answer" in segment:
                new_segments_list[segment_id]["answer"] = [x for x in segments_list if x["segment_id"] == segment_id and "answer" in x][0]["answer"]
            elif "answers" in segment:
                new_segments_list[segment_id]["correct_answer"] = [x for x in segments_list if x["segment_id"] == segment_id and x.get("answers") is not None and "correct_answer" in x.get("answers")][0]["answers"]["correct_answer"]
                new_segments_list[segment_id]["wrong_answers"] = [x for x in segments_list if x["segment_id"] == segment_id and  x.get("answers") is not None and "wrong_answers" in x.get("answers")][0]["answers"]["wrong_answers"]
        
        new_segments_list[segment_id]["delete"] = session_state_dict["button_state"+str(segment_id)]
    return new_segments_list



def upload_modules_json(module, segments_list) -> None:
    modules_data = {"module_name": "NAF_1", "updated":"yes"}
    modules_segments_list = []

    for segment in segments_list:
        if segment["delete"] == "no":
            modules_segment = segment.copy()
            del modules_segment["delete"]
            modules_segments_list.append(modules_segment)
    
    modules_data["segments"] = modules_segments_list
    with open(f"src/data/modules/{module}_updated.json",'w', encoding='utf-8') as f:
        json.dump( modules_data , f, ensure_ascii=False, indent=4)
    

def upload_modules_topics_json(module, segments_list) -> None:
    modules_topics_data = { "module_name": "NAF_1", "updated":"yes"}
    modules_topics_topics_list= []

    with open(f'src/data/modules/topics/{module}_topics.json') as g:
        data_modules_topics = json.load(g)

    topics = data_modules_topics['topics']
    topic_id = 0
    topic_segment_id = 0
    topic_segment_id_new = 0
    topic_segment_id_list= []

    for segment in segments_list:
        topic_title = topics[topic_id]["topic_title"]
        if segment["delete"] == "no":
            topic_segment_id_list.append(topic_segment_id_new)
            topic_segment_id_new += 1

        if topic_segment_id == len(topics[topic_id]["segment_indexes"])-1:
            modules_topics_topics_list.append( 
                {"topic_title":topic_title,
                 "segment_indexes":  topic_segment_id_list} )
            topic_id += 1
            topic_segment_id = 0
            topic_segment_id_list = []
        else:
            topic_segment_id += 1

    modules_topics_data["topics"] = modules_topics_topics_list
    with open(f"src/data/modules/topics/{module}_updated.json",'w', encoding='utf-8') as f:
        json.dump( modules_topics_data, f, ensure_ascii=False, indent=4)
