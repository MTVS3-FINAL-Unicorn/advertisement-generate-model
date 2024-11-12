import os
from uuid import uuid4
import base64
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils.upload_s3 import upload_file_to_s3
# from comfyApi.epicrealizm_img2img_api import make_image
# from comfyApi.cogvideo_img2vid_api import make_video
from comfyUIApi import make_advertise
import logging

logging.basicConfig(
    filename='app.log',        # 로그 파일 이름
    filemode='a',               # 'a'는 기존 파일에 추가, 'w'는 파일을 덮어쓰기
    level=logging.INFO,         # 로그 레벨 설정
    encoding='utf-8-sig',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# FastAPI와 템플릿 설정
app = FastAPI(    
    title="광고 생성 API 문서",
    description="영상 광고 생성 기능",
    version="1.0.0"
    )

# Video Ad 생성 요청에 필요한 이미지 파일과 프롬프트 받기
@app.post("/generate-videoad")
async def generate_videoad(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    corpId: int = Form(...),
    ratioType: str = Form(...)
):   
    # try:
    logging.info(f"/generate-videoad : {image, prompt, corpId, ratioType}")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
    # 이미지 파일 저장 경로 설정
    image_path = f"/home/metaai1/jinjoo_work/unicorn/ComfyUI/input/{str(uuid4())}"

    # 이미지 파일을 저장
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())

    file_urls = []
    generated_video_name = str(uuid4()) + '.mp4'
    if ratioType == "가로형":
        video_paths = make_advertise(image_path, prompt, generated_video_name, False)
    elif ratioType == "세로형":
        video_paths = make_advertise(image_path, prompt, generated_video_name, True)

    for video_path in video_paths:
        # S3 버킷에 업로드
        bucket = 'jurassic-park'
        file_url = f"https://{bucket}.s3.{AWS_DEFAULT_REGION}.amazonaws.com/{generated_video_name}"
        await upload_file_to_s3(video_path, key)
        file_urls.append(file_url)
        
    # 실행 결과 확인
    return {"result": file_urls}

    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f'Error: {e}')

@app.post("/generate-background")
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