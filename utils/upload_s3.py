import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
import os
import httpx
from fastapi import HTTPException

# .env 파일 로드
load_dotenv()

# 환경 변수에서 AWS 자격 증명 및 설정 불러오기
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")

client = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_DEFAULT_REGION
                      )

async def upload_file_to_s3(file_path, key):
    bucket = 'jurassic-park'
    
    try:
        # 파일 업로드
        client.upload_file(file_path, bucket, key)

    except FileNotFoundError:
        print("The file was not found")
        
    except NoCredentialsError:
        print("Credentials not available")

async def post_advertise_video(file_path, key, ad_id):   
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            with open(file_path, "rb") as file:
                files = {
                    "adVideo": (key, file, "video/mp4")
                }
                data = {
                    "adId": ad_id
                }
                response = await client.post(
                    "http://125.132.216.190:319/api/v1/ad/generated/video",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                print(response.text)
                return response.text
        
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except Exception as e:
            print(f"일반 에러 발생: {e}")
            return None
        
async def post_advertise_preview(file_path, key, ad_id):
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            with open(file_path, "rb") as file:
                files = {
                    "previewImage": (key, file, "image/jpeg")
                }
                data = {
                    "adId": ad_id
                }
                response = await client.post(
                    "http://125.132.216.190:319/api/v1/ad/generated/preview",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                # print(response.text)
 
                return response.text
        
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
        except Exception as e:
            print(f"일반 에러 발생: {e}")
            return None