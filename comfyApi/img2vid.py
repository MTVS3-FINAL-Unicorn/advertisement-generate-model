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
    "79": {
      "inputs": {
        "model": "THUDM/CogVideoX-5b-I2V",
        "precision": "bf16",
        "fp8_transformer": "disabled",
        "compile": "disabled",
        "enable_sequential_cpu_offload": true
      },
      "class_type": "DownloadAndLoadCogVideoModel",
      "_meta": {
        "title": "(Down)load CogVideo Model"
      }
    },
    "80": {
      "inputs": {
        "clip_name": "t5xxl_fp8_e4m3fn.safetensors",
        "type": "sd3"
      },
      "class_type": "CLIPLoader",
      "_meta": {
        "title": "Load CLIP"
      }
    },
    "81": {
      "inputs": {
        "prompt": "",
        "strength": 1,
        "force_offload": true,
        "clip": [
          "80",
          0
        ]
      },
      "class_type": "CogVideoTextEncode",
      "_meta": {
        "title": "CogVideo TextEncode"
      }
    },
    "82": {
      "inputs": {
        "prompt": "nsfw",
        "strength": 1,
        "force_offload": true,
        "clip": [
          "80",
          0
        ]
      },
      "class_type": "CogVideoTextEncode",
      "_meta": {
        "title": "CogVideo TextEncode"
      }
    },
    "83": {
      "inputs": {
        "width": 720,
        "height": 480,
        "upscale_method": "lanczos",
        "keep_proportion": false,
        "divisible_by": 16,
        "crop": "disabled",
        "image": [
          "96",
          0
        ]
      },
      "class_type": "ImageResizeKJ",
      "_meta": {
        "title": "Resize Image"
      }
    },
    "84": {
      "inputs": {
        "frame_rate": 8,
        "loop_count": 0,
        "filename_prefix": "CogVideoX-I2V",
        "format": "video/h264-mp4",
        "pix_fmt": "yuv420p",
        "crf": 19,
        "save_metadata": true,
        "pingpong": false,
        "save_output": true,
        "images": [
          "85",
          0
        ]
      },
      "class_type": "VHS_VideoCombine",
      "_meta": {
        "title": "Video Combine 🎥🅥🅗🅢"
      }
    },
    "85": {
      "inputs": {
        "enable_vae_tiling": true,
        "tile_sample_min_height": 96,
        "tile_sample_min_width": 96,
        "tile_overlap_factor_height": 0.083,
        "tile_overlap_factor_width": 0.083,
        "auto_tile_size": true,
        "pipeline": [
          "86",
          0
        ],
        "samples": [
          "86",
          1
        ]
      },
      "class_type": "CogVideoDecode",
      "_meta": {
        "title": "CogVideo Decode"
      }
    },
    "86": {
      "inputs": {
        "height": 480,
        "width": 720,
        "num_frames": 49,
        "steps": 22,
        "cfg": 6,
        "seed": 65334758276105,
        "scheduler": "DDIM",
        "denoise_strength": 1,
        "pipeline": [
          "79",
          0
        ],
        "positive": [
          "81",
          0
        ],
        "negative": [
          "82",
          0
        ],
        "image_cond_latents": [
          "87",
          0
        ]
      },
      "class_type": "CogVideoSampler",
      "_meta": {
        "title": "CogVideo Sampler"
      }
    },
    "87": {
      "inputs": {
        "chunk_size": 16,
        "enable_tiling": true,
        "pipeline": [
          "79",
          0
        ],
        "image": [
          "83",
          0
        ]
      },
      "class_type": "CogVideoImageEncode",
      "_meta": {
        "title": "CogVideo ImageEncode"
      }
    },
    "96": {
      "inputs": {
        "image": "00dca766-f992-46f2-b1c7-06d836dd41c2",
        "upload": "image"
      },
      "class_type": "LoadImage",
      "_meta": {
        "title": "Load Image"
      }
    }
  }
"""

async def make_video(image_path, prompt_value, video_name, is_vertical=False):
  prompt = json.loads(prompt_text)
  # print('프롬프트 입니다 ', prompt_value)
  prompt["96"]["inputs"]["image"] = image_path
  prompt["81"]["inputs"]["prompt"] = prompt_value
  
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  videos = get_videos(ws, prompt)
  ws.close()
  # print('비디오 :', videos)
  video_paths = []
  for node_id in videos.keys():
    # print('노드 번호 : ', node_id)
    if node_id == "84":
      for video_data in videos[node_id]:
          video_path = f'./tmp/{video_name}'
          video_paths.append(video_path)
          with open(video_path, 'wb') as f:
              f.write(video_data)
  return video_paths
        
if __name__ == "__main__":
  image_value = "ad_3.jpg"
  prompt_value = "싱그러운 숲 속에 놓인 제품, 환상적인 느낌과 자연친화적인 분위기. 고화질"
  video_name = "output"
  make_video(image_value, prompt_value, video_name)
  