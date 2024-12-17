import requests

def download_image_from_url(image_url, output_path):
    # 이미지 URL로부터 데이터 다운로드
    response = requests.get(image_url)
    response.raise_for_status()
    # 이미지 데이터 로드 및 저장
    with open(output_path, 'wb') as file:
        file.write(response.content)

