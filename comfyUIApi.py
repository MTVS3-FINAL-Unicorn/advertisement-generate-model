import json
import random
import urllib.parse
import urllib.request
import uuid

import websocket
server_address = "127.0.0.1:8189"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_file(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())
    
def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      images_output = []
      if 'images' in node_output:
        for image in node_output['images']:
            image_data = get_file(image['filename'], image['subfolder'], image['type'])
            images_output.append(image_data)
      output_images[node_id] = images_output
    return output_images

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
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      video_output = []
      if 'gifs' in node_output:
        for video in node_output['gifs']:
          video_data = get_file(video['filename'], video['subfolder'], video['type'])
          video_output.append(video_data)
      output_videos[node_id] = video_output
    return output_videos

prompt_text = """
    {
    "3": {
        "inputs": {
        "seed": 0,
        "steps": 20,
        "cfg": 3,
        "sampler_name": "dpmpp_2m_sde",
        "scheduler": "karras",
        "denoise": 1,
        "model": [
            "18",
            0
        ],
        "positive": [
            "19",
            0
        ],
        "negative": [
            "19",
            1
        ],
        "latent_image": [
            "23",
            0
        ]
        },
        "class_type": "KSampler",
        "_meta": {
        "title": "KSampler"
        }
    },
    "4": {
        "inputs": {
        "ckpt_name": "epicrealism_naturalSinRC1VAE.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
        "title": "Load Checkpoint"
        }
    },
    "6": {
        "inputs": {
        "text": [
            "91",
            0
        ],
        "clip": [
            "4",
            1
        ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
        "title": "CLIP Text Encode (Prompt)"
        }
    },
    "7": {
        "inputs": {
        "text": "(noise, blur, worst quality, low quality, error, cropped, bad anatomy, bad proportions, wrong hands)\\n(NSFW, nude)",
        "clip": [
            "4",
            1
        ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
        "title": "CLIP Text Encode (Prompt)"
        }
    },
    "8": {
        "inputs": {
        "samples": [
            "3",
            0
        ],
        "vae": [
            "4",
            2
        ]
        },
        "class_type": "VAEDecode",
        "_meta": {
        "title": "VAE Decode"
        }
    },
    "9": {
        "inputs": {
        "filename_prefix": "ComfyUI",
        "images": [
            "76",
            0
        ]
        },
        "class_type": "SaveImage",
        "_meta": {
        "title": "Save Image"
        }
    },
    "14": {
        "inputs": {
        "images": [
            "60",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "15": {
        "inputs": {
        "image": [
            "60",
            0
        ]
        },
        "class_type": "SplitImageWithAlpha",
        "_meta": {
        "title": "Split Image with Alpha"
        }
    },
    "16": {
        "inputs": {
        "x": 0,
        "y": 0,
        "resize_source": false,
        "destination": [
            "61",
            0
        ],
        "source": [
            "15",
            0
        ],
        "mask": [
            "60",
            1
        ]
        },
        "class_type": "ImageCompositeMasked",
        "_meta": {
        "title": "ImageCompositeMasked"
        }
    },
    "17": {
        "inputs": {
        "image": [
            "60",
            0
        ],
        "alpha": [
            "60",
            1
        ]
        },
        "class_type": "ICLightApplyMaskGrey",
        "_meta": {
        "title": "IC Light Apply Mask Grey"
        }
    },
    "18": {
        "inputs": {
        "model_path": "IC-Light/iclight_sd15_fc.safetensors",
        "model": [
            "29",
            0
        ]
        },
        "class_type": "LoadAndApplyICLightUnet",
        "_meta": {
        "title": "Load And Apply IC-Light"
        }
    },
    "19": {
        "inputs": {
        "multiplier": 0.182,
        "positive": [
            "6",
            0
        ],
        "negative": [
            "7",
            0
        ],
        "vae": [
            "4",
            2
        ],
        "foreground": [
            "20",
            0
        ]
        },
        "class_type": "ICLightConditioning",
        "_meta": {
        "title": "IC-Light Conditioning"
        }
    },
    "20": {
        "inputs": {
        "pixels": [
            "17",
            0
        ],
        "vae": [
            "4",
            2
        ]
        },
        "class_type": "VAEEncode",
        "_meta": {
        "title": "VAE Encode"
        }
    },
    "23": {
        "inputs": {
        "pixels": [
            "16",
            0
        ],
        "vae": [
            "4",
            2
        ]
        },
        "class_type": "VAEEncode",
        "_meta": {
        "title": "VAE Encode"
        }
    },
    "28": {
        "inputs": {
        "preset": "VIT-G (medium strength)",
        "model": [
            "4",
            0
        ]
        },
        "class_type": "IPAdapterUnifiedLoader",
        "_meta": {
        "title": "IPAdapter Unified Loader"
        }
    },
    "29": {
        "inputs": {
        "weight": 1,
        "weight_type": "ease in-out",
        "combine_embeds": "concat",
        "start_at": 0,
        "end_at": 1,
        "embeds_scaling": "V only",
        "model": [
            "28",
            0
        ],
        "ipadapter": [
            "28",
            1
        ],
        "image": [
            "16",
            0
        ],
        "attn_mask": [
            "60",
            1
        ]
        },
        "class_type": "IPAdapterAdvanced",
        "_meta": {
        "title": "IPAdapter Advanced"
        }
    },
    "33": {
        "inputs": {
        "image": "mongtoo_resize2.png",
        "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
        "title": "Load Image"
        }
    },
    "57": {
        "inputs": {
        "images": [
            "17",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "58": {
        "inputs": {
        "rgthree_comparer": {
            "images": [
            {
                "name": "A",
                "selected": true,
                "url": "/api/view?filename=rgthree.compare._temp_vjkie_00051_.png&type=temp&subfolder=&rand=0.03875649013922433"
            },
            {
                "name": "B",
                "selected": true,
                "url": "/api/view?filename=rgthree.compare._temp_vjkie_00052_.png&type=temp&subfolder=&rand=0.15152673713182918"
            }
            ]
        },
        "image_a": [
            "76",
            0
        ],
        "image_b": [
            "61",
            0
        ]
        },
        "class_type": "Image Comparer (rgthree)",
        "_meta": {
        "title": "Image Comparer (rgthree)"
        }
    },
    "59": {
        "inputs": {
        "model": "u2net: general purpose",
        "providers": "CPU"
        },
        "class_type": "RemBGSession+",
        "_meta": {
        "title": "🔧 RemBG Session"
        }
    },
    "60": {
        "inputs": {
        "rembg_session": [
            "59",
            0
        ],
        "image": [
            "61",
            0
        ]
        },
        "class_type": "ImageRemoveBackground+",
        "_meta": {
        "title": "🔧 Image Remove Background"
        }
    },
    "61": {
        "inputs": {
        "width": 512,
        "height": 512,
        "interpolation": "nearest",
        "method": "keep proportion",
        "condition": "downscale if bigger",
        "multiple_of": 0,
        "image": [
            "33",
            0
        ]
        },
        "class_type": "ImageResize+",
        "_meta": {
        "title": "🔧 Image Resize"
        }
    },
    "62": {
        "inputs": {
        "image": [
            "16",
            0
        ]
        },
        "class_type": "SplitImageWithAlpha",
        "_meta": {
        "title": "Split Image with Alpha"
        }
    },
    "63": {
        "inputs": {
        "image": [
            "62",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "64": {
        "inputs": {
        "radius": 2,
        "images": [
            "62",
            0
        ]
        },
        "class_type": "ImageGaussianBlur",
        "_meta": {
        "title": "Image Gaussian Blur"
        }
    },
    "65": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.4,
        "image_a": [
            "63",
            0
        ],
        "image_b": [
            "64",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "66": {
        "inputs": {
        "image": [
            "65",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "67": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 1,
        "image_a": [
            "64",
            0
        ],
        "image_b": [
            "66",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "68": {
        "inputs": {
        "image": [
            "8",
            0
        ]
        },
        "class_type": "SplitImageWithAlpha",
        "_meta": {
        "title": "Split Image with Alpha"
        }
    },
    "69": {
        "inputs": {
        "image": [
            "68",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "70": {
        "inputs": {
        "radius": 2,
        "images": [
            "68",
            0
        ]
        },
        "class_type": "ImageGaussianBlur",
        "_meta": {
        "title": "Image Gaussian Blur"
        }
    },
    "71": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.5,
        "image_a": [
            "69",
            0
        ],
        "image_b": [
            "70",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "72": {
        "inputs": {
        "image": [
            "71",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "73": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 1,
        "image_a": [
            "70",
            0
        ],
        "image_b": [
            "72",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "74": {
        "inputs": {
        "blend_percentage": 1,
        "image_a": [
            "73",
            0
        ],
        "image_b": [
            "67",
            0
        ],
        "mask": [
            "78",
            0
        ]
        },
        "class_type": "Image Blend by Mask",
        "_meta": {
        "title": "Image Blend by Mask"
        }
    },
    "75": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.55,
        "image_a": [
            "70",
            0
        ],
        "image_b": [
            "74",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "76": {
        "inputs": {
        "black_level": 60,
        "mid_level": 130,
        "white_level": 190,
        "image": [
            "75",
            0
        ]
        },
        "class_type": "Image Levels Adjustment",
        "_meta": {
        "title": "Image Levels Adjustment"
        }
    },
    "77": {
        "inputs": {
        "expand": -2,
        "tapered_corners": true,
        "mask": [
            "60",
            1
        ]
        },
        "class_type": "GrowMask",
        "_meta": {
        "title": "GrowMask"
        }
    },
    "78": {
        "inputs": {
        "mask": [
            "77",
            0
        ]
        },
        "class_type": "MaskToImage",
        "_meta": {
        "title": "Convert Mask to Image"
        }
    },
    "79": {
        "inputs": {
        "model": "THUDM/CogVideoX-5b-I2V",
        "precision": "fp16",
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
        "prompt": [
            "91",
            0
        ],
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
            "76",
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
        "save_output": false,
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
        "steps": 18,
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
    "90": {
        "inputs": {
        "prompt": "회색 강아지 인형이 숲 속을 돌아다니고 있다. ",
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "llama3:latest",
        "system": "너는 똑똑한 AI 이미지 생성형 프롬프트 작성자야. 입력받은 프롬프트를 기반으로 생성형 AI 이미지 모델을 이용해 광고 이미지를 생성하기 위한 프롬프트를 작성해줘. 프롬프트는 실제 사진을 묘사해야 하고, 영어로 작성되어야해. 주제, 구도, 분위기, 색감, 조명 등을 각각의 문단 별로 최대한 자세히 서술해줘.\\n답변은 생성한 프롬프트만 하면 돼. ",
        "seed": 409350015,
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
    "91": {
        "inputs": {
        "prompt": [
            "90",
            0
        ],
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "qwen2m:latest",
        "system": "프롬프트를 한 문장으로 요약해줘. 프롬프트는 영어여야 해\\n답변의 형식은 아래처럼 오직 프롬프트만 보내줘.\\n\\nidyllic atmosphere, with a delicate cherry blossom tree in full bloom behind a product, Soft, warm sunlight",
        "seed": 108406798,
        "top_k": 40,
        "top_p": 0.9,
        "temperature": 0.8,
        "num_predict": -1,
        "tfs_z": 1,
        "keep_alive": 5,
        "keep_context": true,
        "format": "text"
        },
        "class_type": "OllamaGenerateAdvance",
        "_meta": {
        "title": "Ollama Generate Advance"
        }
    },
    "92": {
        "inputs": {
        "text": [
            "90",
            0
        ],
        "text2": "Here is the prompt:\\n\\n**Theme:** Whimsical Forest Adventure\\n\\n**Composition:** A small, gray plush puppy toy ( approx. 5-7 inches in length) stands out amidst a lush, vibrant forest landscape. The camera angle should be from a slight overhead perspective, allowing the viewer to see the puppy's miniature figure in relation to the surrounding environment.\\n\\n**Mood:** Playful, Curious, and Enchanting\\n\\n**Color Palette:**\\n\\n* Main colors: Soft greens (e.g., sage, moss), rich browns, and weathered wood tones\\n* Accent colors: Warm beige, creamy whites, and subtle hints of blue (for the sky or mist)\\n\\n**Lighting:** Natural, with soft dappled sunlight filtering through the leaves. The atmosphere should be tranquil, with a few wispy clouds adding to the dreamy quality.\\n\\n**Additional Details:**\\n\\n* Include some scattered forest floor elements, such as twigs, pinecones, and ferns\\n* Consider incorporating a few subtle, shimmering effects (e.g., dew droplets, spider webs) to enhance the magical atmosphere\\n* The puppy toy should be positioned in a way that suggests it's exploring or discovering something new (e.g., peeking behind a leaf, sniffing at a flower)\\n\\nPlease create an AI-generated image based on this prompt."
        },
        "class_type": "ShowText|pysssss",
        "_meta": {
        "title": "Show Text 🐍"
        }
    },
    "93": {
        "inputs": {
        "text": [
            "91",
            0
        ],
        "text2": "The prompt outlines creating a whimsical forest adventure scene featuring a small gray plush puppy toy amidst a lush greenery backdrop with soft sunlight filtering through the trees and enveloped in a palette of sage greens, rich browns, and weathered woods. The overall mood should be playful, curious, and enchanting with gentle lighting from dappled sunlight and subtle details like shimmering dew droplets or spider webs adding to the mystical atmosphere. The puppy toy is depicted as if it's exploring or discovering its surroundings by positioning it among scattered forest elements such as twigs, pinecones, and ferns in an overhead perspective that highlights both the puppy and environment."
        },
        "class_type": "ShowText|pysssss",
        "_meta": {
        "title": "Show Text 🐍"
        }
    }
    }
"""

def make_advertise(image_value, prompt_value, generated_video_name, is_vertical=False ):
    prompt = json.loads(prompt_text)
    prompt["33"]["inputs"]["image"] = image_value
    prompt["90"]["inputs"]["prompt"] = prompt_value
  
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    videos = get_videos(ws, prompt)
    ws.close()
    video_paths = []
    for node_id in videos.keys():
        if node_id == "84":
            for video_data in videos[node_id]:
                video_path = f'./tmp/{generated_video_name}.mp4'
                video_paths.append(video_path)
                with open(video_path, 'wb') as f:
                    f.write(video_data)
    return video_paths
        
if __name__ == "__main__":
  image_value = "ad_3.jpg"
  prompt_value = "싱그러운 숲 속에 놓인 제품, 환상적인 느낌과 자연친화적인 분위기. 고화질"
  video_name = "output"
  print(make_video(image_value, prompt_value, video_name))
  