import os
from uuid import uuid4
import base64
from AnalyzeMeeting.lda_model import TopicModel
from AnalyzeMeeting.stt import stt
from AnalyzeMeeting.text_organize import remove_stopwords, tokenize_text
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils.upload_s3 import upload_file_to_s3
from AnalyzeMeeting.embedding_vector_model import EmbeddingVectorModel

# 환경변수 로드
load_dotenv()

# FastAPI와 템플릿 설정
app = FastAPI()
templates = Jinja2Templates(directory="./templates")

# embedding_model 생성
embedding_vector_model = EmbeddingVectorModel()

# 토큰 저장소
tokens = {}

# 텍스트 답변 처리 엔드포인트
class TextResponse(BaseModel):
    surveyQuestion: str
    textResponse: str
    userId: int
    meetingId: int
    corpId: int

@app.post("/submit-text-response")
async def submit_text_response(response: TextResponse):
    if response.corpId not in tokens:
        tokens[response.corpId] = {response.meetingId: []}
    tokens[response.corpId][response.meetingId].extend(remove_stopwords(tokenize_text(response.textResponse)))
    return {"result": f"{response.textResponse}"}

# 음성 답변 처리 엔드포인트 (음성 파일을 STT로 변환)
class VoiceResponse(BaseModel):
    surveyQuestion: str 
    voiceResponse: str
    userId: int 
    meetingId: int 
    corpId: int 
@app.post("/submit-voice-response")
async def submit_voice_response(response: VoiceResponse):
    try:
        voice_data = base64.b64decode(response.voiceResponse)
        text_response = stt(voice_data)
        if response.corpId not in tokens:
            tokens[response.corpId] = {response.meetingId: []}
        tokens[response.corpId][response.meetingId].extend(remove_stopwords(tokenize_text(text_response)))
        return {"result": f"{text_response}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error processing voice response: {e}')

# 설문 선택 답변 처리 엔드포인트
class ChoiceResponse(BaseModel):
    surveyQuestion: str
    choiceResponse: str
    userId: int
    meetingId: int
    corpId: int
    
@app.post("/submit-choice-response")
async def submit_choice_response(response: ChoiceResponse):
    # 선택형 설문 데이터를 저장
    return {"result": "Choice response received"}

# 최종 분석 처리 엔드포인트
class AnalyzeResponse(BaseModel):
    corpId: int
    meetingId: int

@app.post("/analyze-responses")
async def analyze_responses(response: AnalyzeResponse):
    try:
        topic_model = TopicModel(tokens[response.corpId][response.meetingId], response.corpId, response.meetingId)
        json_result = topic_model.make_lda_json()
        
        embedding_vector_model.make_embeddings(tokens[response.corpId][response.meetingId], response.corpId, response.meetingId)
        embedding_vector_model.make_checkpoint()
        embedding_vector_model.run_tensorboard('0.0.0.0', '7779')
        return json_result
    except KeyError:
        if response.corpId not in tokens:
            raise HTTPException(status_code=404, detail="corpId에 해당하는 데이터가 존재하지 않습니다.")
        elif response.meetingId not in tokens[response.corpId]:
            raise HTTPException(status_code=404, detail='meetingId에 해당하는 데이터가 존재하지 않습니다.')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"error: {e}")

# FastAPI로 HTML 파일을 서빙
@app.get("/index.html", response_class=HTMLResponse)
async def serve_html():
    try:
        with open("./index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found.")

# LDA 시각화 처리 엔드포인트
@app.post("/lda-visualization")
async def lda_visualization(request: Request, response: AnalyzeResponse):
    try:
        topic_model = TopicModel(tokens[response.corpId][response.meetingId], response.corpId, response.meetingId)
        json_result = topic_model.make_lda_json()

        # 템플릿에 데이터를 전달하여 렌더링
        return templates.TemplateResponse("lda_visualization.html", {
            "request": request,
            "lda_data": json_result
        })
    except KeyError:
        raise HTTPException(status_code=404, detail="No data found for the given corpId and meetingId.")

# Video Ad 생성 요청에 필요한 이미지 파일과 프롬프트 받기
@app.post("/generate-videoad")
async def generate_videoad(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    corpId: int = Form(...),
    type: str = Form(...)
):
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    try:
        # 이미지 파일 저장 경로 설정
        image_path = f"/tmp/{image.filename}"

        # 이미지 파일을 저장
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

        # S3 버킷에 업로드
        bucket = 'jurassic-park'
        key = str(uuid4()) + '.jpg'
        file_url = f"https://{bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{key}"
        await upload_file_to_s3(image_path, key)

        # 실행 결과 확인
        return {"result": file_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')

@app.post("generate-background")
async def generate_background(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    corpId: int = Form(...),
    type: str = Form(...)
):
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    try:
        # 이미지 파일 저장 경로 설정
        image_path = f"/tmp/{image.filename}"

        # 이미지 파일을 저장
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())

        # S3 버킷에 업로드
        bucket = 'jurassic-park'
        key = str(uuid4()) + '.jpg'
        file_url = f"https://{bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{key}"
        await upload_file_to_s3(image_path, key)

        # 실행 결과 확인
        return {"result": file_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Error: {e}')