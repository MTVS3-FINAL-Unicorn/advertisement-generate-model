from uuid import uuid4
from pydantic import BaseModel
from utils.upload_s3 import post_advertise_video, post_advertise_preview
from comfyApi.img2vid import make_video
from comfyApi.img2img import make_image
from utils.get_s3 import download_image_from_url
from fastapi import FastAPI
import logging


logging.basicConfig(
    filename='app.log',
    filemode='a',
    level=logging.INFO,
    encoding='utf-8-sig',
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# FastAPI 앱 초기화
app = FastAPI(
    title="광고 생성 API 문서",
    description="영상 광고 생성 기능",
    version="1.0"
)


# 광고 생성 요청
class GenerateVideoIn(BaseModel):
    image: str
    prompt: str
    adId: int


@app.post("/generate-videoad")
async def generate_videoad(response: GenerateVideoIn):
    # try:
    # 요청 데이터 가져오기
    image_url, prompt, ad_id = response.image, response.prompt, response.adId

    # 이미지 다운로드
    generated_id = str(uuid4())
    image_path = f"/tmp/{generated_id}_original.png"
    download_image_from_url(image_url, image_path)


    # 이미지 생성 및 프롬프트 반환
    modified_prompt = await make_image(image_path, prompt, f"{generated_id}.png", False)

    # 광고 미리보기 업로드
    preview_url = await post_advertise_preview(f"/home/metaai1/jinjoo_work/unicorn/tmp/{generated_id}.png", f"{generated_id}.png", ad_id)

    # 비디오 생성
    await make_video(f"/home/metaai1/jinjoo_work/unicorn/tmp/{generated_id}.png", modified_prompt, f"{generated_id}.mp4", False)


    # 비디오 업로드
    video_url = await post_advertise_video(f"/home/metaai1/jinjoo_work/unicorn/tmp/{generated_id}.mp4", f"{generated_id}.mp4", ad_id)

    # 작업 완료
    return {
        "result": "광고 생성이 성공적으로 완료되었습니다.",
        "preview_url": preview_url,
        "video_url": video_url
    }


    # except Exception as e:
    #     await send_status_update(generated_id, "Failed")
    #     logging.error(f"Task {generated_id} failed: {str(e)}")
    #     return {"task_id": generated_id, "status": "Failed", "error": str(e)}