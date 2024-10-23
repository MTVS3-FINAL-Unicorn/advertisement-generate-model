import speech_recognition as sr
from io import BytesIO

r = sr.Recognizer()

def stt(voice_data):
    with sr.AudioFile(BytesIO(voice_data)) as source:
        audio = r.record(source)  # 전체 오디오를 읽음
    txt = r.recognize_google(audio, language='ko-KR')
    return txt
