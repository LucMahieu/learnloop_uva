import streamlit as st
import sounddevice as sd
import numpy as np
import cv2
import mss
import threading
import wave
import time
import pyaudio

st.title("Screen and Audio Recorder")

if 'recording' not in st.session_state:
    st.session_state['recording'] = False

def record_audio(filename, duration):    
    format = pyaudio.paInt16
    channels = 2
    rate = 44100
    chunk = duration * rate
    
    p = pyaudio.PyAudio()

    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []

    data = stream.read(chunk)
    frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))
    wf.close()

def record_screen(filename, duration, fps=15):
    sct = mss.mss()
    monitor = sct.monitors[1]

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(filename, fourcc, fps, (monitor["width"], monitor["height"]))

    start_time = time.time()
    while time.time() - start_time < duration:
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        out.write(img)

    out.release()


def start_recording(duration):
    
    # Start audio and screen recording in separate threads
    audio_thread = threading.Thread(target=record_audio, args=("src/data/audio/output_audio.mp3", duration))
    screen_thread = threading.Thread(target=record_screen, args=("src/data/screen/output_screen.avi", duration))
    
    audio_thread.start()
    screen_thread.start()

    audio_thread.join()
    screen_thread.join()
    
    st.session_state['recording'] = False

def stop_recording():
    st.session_state['recording'] = False


duration_minutes = st.slider("Select duration (minutes)", min_value=1, max_value=120, value=60)
duration_seconds = 60 * duration_minutes

if st.button("Start recording"):
    st.session_state['recording'] = True
    start_recording(duration_seconds)


