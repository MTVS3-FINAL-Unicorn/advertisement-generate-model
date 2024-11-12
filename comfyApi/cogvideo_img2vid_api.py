import json
import random
import urllib.parse
import urllib.request
import uuid

import websocket
server_address = "127.0.0.1:8190"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_video(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_videos(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_videos = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            # # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            # bytesIO = BytesIO(out[8:])
            # preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      video_output = []
      if 'gifs' in node_output:
        for video in node_output['gifs']:
          video_data = get_video(video['filename'], video['subfolder'], video['type'])
          video_output.append(video_data)
      output_videos[node_id] = video_output
    return output_videos

prompt_text = """
  {
    "1": {
      "inputs": {
        "model": "THUDM/CogVideoX-5b-I2V",
        "precision": "bf16",
        "fp8_transformer": "disabled",
        "compile": "torch",
        "enable_sequential_cpu_offload": false
      },
      "class_type": "DownloadAndLoadCogVideoModel",
      "_meta": {
        "title": "(Down)load CogVideo Model"
      }
    },
    "20": {
      "inputs": {
        "clip_name": "t5xxl_fp8_e4m3fn.safetensors",
        "type": "sd3"
      },
      "class_type": "CLIPLoader",
      "_meta": {
        "title": "Load CLIP"
      }
    },
    "30": {
      "inputs": {
        "prompt": [
          "85",
          0
        ],
        "strength": 1,
        "force_offload": true,
        "clip": [
          "20",
          0
        ]
      },
      "class_type": "CogVideoTextEncode",
      "_meta": {
        "title": "CogVideo TextEncode"
      }
    },
    "31": {
      "inputs": {
        "prompt": "",
        "strength": 1,
        "force_offload": true,
        "clip": [
          "20",
          0
        ]
      },
      "class_type": "CogVideoTextEncode",
      "_meta": {
        "title": "CogVideo TextEncode"
      }
    },
    "36": {
      "inputs": {
        "image": "ad-3-img (1).png",
        "upload": "image"
      },
      "class_type": "LoadImage",
      "_meta": {
        "title": "Load Image"
      }
    },
    "37": {
      "inputs": {
        "width": 720,
        "height": 480,
        "upscale_method": "lanczos",
        "keep_proportion": false,
        "divisible_by": 16,
        "crop": "disabled",
        "image": [
          "36",
          0
        ]
      },
      "class_type": "ImageResizeKJ",
      "_meta": {
        "title": "Resize Image"
      }
    },
    "44": {
      "inputs": {
        "frame_rate": 16,
        "loop_count": 0,
        "filename_prefix": "CogVideoX-I2V",
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 19,
        "save_metadata": true,
        "pingpong": false,
        "save_output": true,
        "images": [
          "56",
          0
        ]
      },
      "class_type": "VHS_VideoCombine",
      "_meta": {
        "title": "Video Combine 🎥🅥🅗🅢"
      }
    },
    "56": {
      "inputs": {
        "enable_vae_tiling": false,
        "tile_sample_min_height": 96,
        "tile_sample_min_width": 96,
        "tile_overlap_factor_height": 0.083,
        "tile_overlap_factor_width": 0.083,
        "auto_tile_size": true,
        "pipeline": [
          "57",
          0
        ],
        "samples": [
          "57",
          1
        ]
      },
      "class_type": "CogVideoDecode",
      "_meta": {
        "title": "CogVideo Decode"
      }
    },
    "57": {
      "inputs": {
        "height": 480,
        "width": 720,
        "num_frames": 49,
        "steps": 25,
        "cfg": 6,
        "seed": 65334758276105,
        "scheduler": "CogVideoXDPMScheduler",
        "denoise_strength": 1,
        "pipeline": [
          "1",
          0
        ],
        "positive": [
          "30",
          0
        ],
        "negative": [
          "31",
          0
        ],
        "image_cond_latents": [
          "58",
          0
        ]
      },
      "class_type": "CogVideoSampler",
      "_meta": {
        "title": "CogVideo Sampler"
      }
    },
    "58": {
      "inputs": {
        "chunk_size": 8,
        "enable_tiling": true,
        "pipeline": [
          "1",
          0
        ],
        "image": [
          "37",
          0
        ]
      },
      "class_type": "CogVideoImageEncode",
      "_meta": {
        "title": "CogVideo ImageEncode"
      }
    },
    "84": {
      "inputs": {
        "prompt": "cherryblossom petals are scattering\\n",
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "llama3:latest",
        "system": "너는 똑똑한 AI 영상 생성형 프롬프트 작성자야. 입력받은 프롬프트를 기반으로 생성형 AI 영상 모델을 이용해 광고 영상을 생성하기 위한 프롬프트를 작성해줘. 프롬프트는 실제적으로 묘사해야 하고, 영어로 작성되어야해. 주제, 구도, 분위기, 색감, 조명 등을 각각의 문단 별로 최대한 자세히 서술해줘.답변은 생성된 영어 프롬프트만 해줘.",
        "seed": 1490097958,
        "top_k": 40,
        "top_p": 0.9,
        "temperature": 0.8,
        "num_predict": -1,
        "tfs_z": 1,
        "keep_alive": 5,
        "keep_context": false,
        "format": "text"
      },
      "class_type": "OllamaGenerateAdvance",
      "_meta": {
        "title": "Ollama Generate Advance"
      }
    },
    "85": {
      "inputs": {
        "prompt": [
          "84",
          0
        ],
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "qwen2m:latest",
        "system": "프롬프트를 한 문장으로 요약해줘. 프롬프트는 영어여야 해\\n답변은 오직 프롬프트만 보내줘.",
        "seed": 1113256843,
        "top_k": 40,
        "top_p": 0.9,
        "temperature": 0.8,
        "num_predict": -1,
        "tfs_z": 1,
        "keep_alive": 5,
        "keep_context": false,
        "format": "text"
      },
      "class_type": "OllamaGenerateAdvance",
      "_meta": {
        "title": "Ollama Generate Advance"
      }
    },
    "86": {
      "inputs": {
        "text": [
          "84",
          0
        ],
        "text2": "**Title:** Whispers of Spring: A Cherry Blossom Romance\\n\\n**Subject:** Romantic Drama\\n\\n**Scene Setting:** A tranquil Japanese garden on a warm spring morning, surrounded by blooming cherry blossom trees with delicate pink and white petals gently drifting to the ground.\\n\\n**Mood:** Soft, serene, and intimate, evoking feelings of nostalgia and longing.\\n\\n**Color Palette:**\\n\\n* Pastel shades of pink and white, reflecting the gentle hues of the cherry blossoms\\n* Earthy tones of green, representing the lush garden surroundings\\n* Warm beige and cream, symbolizing the tender moments between the protagonists\\n\\n**Lighting:** Soft, natural light filtering through the trees, casting dappled shadows across the scene. As the sun rises higher, the lighting becomes warmer and more golden, emphasizing the romance and intimacy.\\n\\n**Storyline:** The narrative follows two souls who find each other amidst the fleeting beauty of cherry blossom season. As they wander hand-in-hand through the garden, their whispers turn to sweet nothings, and their love story unfolds like a delicate petal unfolding from its stem."
      },
      "class_type": "ShowText|pysssss",
      "_meta": {
        "title": "Show Text 🐍"
      }
    },
    "87": {
      "inputs": {
        "text": [
          "85",
          0
        ],
        "text2": "The prompt describes \\"Whispers of Spring,\\" an AI-generated video set in a serene Japanese garden during a warm spring morning, featuring blooming cherry blossoms, soft sunlight, delicate petals falling, earthy tones, gentle music, and slow cinematography capturing the beauty of nature with a focus on intimacy and serenity."
      },
      "class_type": "ShowText|pysssss",
      "_meta": {
        "title": "Show Text 🐍"
      }
    }
  }
"""

def make_video(image_value, prompt_value, image_name, is_vertical=False):
  prompt = json.loads(prompt_text)
  prompt["36"]["inputs"]["image"] = image_value
  prompt["84"]["inputs"]["prompt"] = prompt_value
  
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  videos = get_videos(ws, prompt)
  ws.close()
  
  video_paths = []
  for node_id in videos.keys():
    if node_id == "44":
      for video_data in videos[node_id]:
          video_path = f'./tmp/{node_id}.mp4'
          video_paths.append(video_path)
          with open(video_path, 'wb') as f:
              f.write(video_data)
  return video_paths
        
if __name__ == "__main__":
  image_value = "ad_3.jpg"
  prompt_value = "싱그러운 숲 속에 놓인 제품, 환상적인 느낌과 자연친화적인 분위기. 고화질"
  video_name = "output"
  print(make_video(image_value, prompt_value, video_name))
  