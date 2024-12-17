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
    "4": {
        "inputs": {
        "text": [
            "357",
            0
        ],
        "clip": [
            "82",
            1
        ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
        "title": "CLIP Text Encode (Prompt)"
        }
    },
    "5": {
        "inputs": {
        "text": [
            "359",
            0
        ],
        "clip": [
            "82",
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
        "samples": [
            "19",
            0
        ],
        "vae": [
            "82",
            2
        ]
        },
        "class_type": "VAEDecode",
        "_meta": {
        "title": "VAE Decode"
        }
    },
    "19": {
        "inputs": {
        "seed": 100361857014382,
        "steps": 40,
        "cfg": 2,
        "sampler_name": "dpmpp_2m_sde",
        "scheduler": "karras",
        "denoise": 1,
        "model": [
            "37",
            0
        ],
        "positive": [
            "77",
            0
        ],
        "negative": [
            "77",
            1
        ],
        "latent_image": [
            "50",
            0
        ]
        },
        "class_type": "KSampler",
        "_meta": {
        "title": "KSampler"
        }
    },
    "35": {
        "inputs": {
        "mask": [
            "194",
            0
        ]
        },
        "class_type": "MaskToImage",
        "_meta": {
        "title": "Convert Mask to Image"
        }
    },
    "37": {
        "inputs": {
        "model_path": "IC-Light/iclight_sd15_fc.safetensors",
        "model": [
            "82",
            0
        ]
        },
        "class_type": "LoadAndApplyICLightUnet",
        "_meta": {
        "title": "Load And Apply IC-Light"
        }
    },
    "50": {
        "inputs": {
        "pixels": [
            "35",
            0
        ],
        "vae": [
            "82",
            2
        ]
        },
        "class_type": "VAEEncode",
        "_meta": {
        "title": "VAE Encode"
        }
    },
    "75": {
        "inputs": {
        "expand": 0,
        "incremental_expandrate": 0,
        "tapered_corners": true,
        "flip_input": false,
        "blur_radius": 28.1,
        "lerp_alpha": 1,
        "decay_factor": 1,
        "fill_holes": false,
        "mask": [
            "408",
            0
        ]
        },
        "class_type": "GrowMaskWithBlur",
        "_meta": {
        "title": "Grow Mask With Blur"
        }
    },
    "76": {
        "inputs": {
        "images": [
            "35",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "77": {
        "inputs": {
        "multiplier": 0.15,
        "positive": [
            "4",
            0
        ],
        "negative": [
            "5",
            0
        ],
        "vae": [
            "82",
            2
        ],
        "foreground": [
            "78",
            0
        ]
        },
        "class_type": "ICLightConditioning",
        "_meta": {
        "title": "IC-Light Conditioning"
        }
    },
    "78": {
        "inputs": {
        "pixels": [
            "409",
            0
        ],
        "vae": [
            "82",
            2
        ]
        },
        "class_type": "VAEEncode",
        "_meta": {
        "title": "VAE Encode"
        }
    },
    "82": {
        "inputs": {
        "ckpt_name": "epicrealism_naturalSinRC1VAE.safetensors"
        },
        "class_type": "CheckpointLoaderSimple",
        "_meta": {
        "title": "Load Checkpoint"
        }
    },
    "194": {
        "inputs": {
        "min": 0,
        "max": 0.8200000000000001,
        "mask": [
            "75",
            0
        ]
        },
        "class_type": "RemapMaskRange",
        "_meta": {
        "title": "Remap Mask Range"
        }
    },
    "207": {
        "inputs": {
        "images": [
            "406",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "208": {
        "inputs": {
        "text": [
            "357",
            0
        ],
        "clip": [
            "82",
            1
        ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
        "title": "CLIP Text Encode (Prompt)"
        }
    },
    "209": {
        "inputs": {
        "text": [
            "359",
            0
        ],
        "clip": [
            "82",
            1
        ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
        "title": "CLIP Text Encode (Prompt)"
        }
    },
    "210": {
        "inputs": {
        "seed": 180794899782095,
        "steps": 40,
        "cfg": 3.6,
        "sampler_name": "dpmpp_2m_sde",
        "scheduler": "karras",
        "denoise": 1,
        "model": [
            "82",
            0
        ],
        "positive": [
            "315",
            0
        ],
        "negative": [
            "209",
            0
        ],
        "latent_image": [
            "345",
            0
        ]
        },
        "class_type": "KSampler",
        "_meta": {
        "title": "KSampler"
        }
    },
    "211": {
        "inputs": {
        "samples": [
            "210",
            0
        ],
        "vae": [
            "82",
            2
        ]
        },
        "class_type": "VAEDecode",
        "_meta": {
        "title": "VAE Decode"
        }
    },
    "214": {
        "inputs": {
        "strength": 0.2,
        "conditioning": [
            "208",
            0
        ],
        "control_net": [
            "215",
            0
        ],
        "image": [
            "317",
            0
        ]
        },
        "class_type": "ControlNetApply",
        "_meta": {
        "title": "Apply ControlNet (OLD)"
        }
    },
    "215": {
        "inputs": {
        "control_net_name": "control_v11f1p_sd15_depth_fp16.safetensors"
        },
        "class_type": "ControlNetLoader",
        "_meta": {
        "title": "Load ControlNet Model"
        }
    },
    "216": {
        "inputs": {
        "width": 1024,
        "height": 1024,
        "batch_size": 1
        },
        "class_type": "EmptyLatentImage",
        "_meta": {
        "title": "Empty Latent Image"
        }
    },
    "217": {
        "inputs": {
        "blend_percentage": 1,
        "image_a": [
            "211",
            0
        ],
        "image_b": [
            "410",
            0
        ],
        "mask": [
            "219",
            0
        ]
        },
        "class_type": "Image Blend by Mask",
        "_meta": {
        "title": "Image Blend by Mask"
        }
    },
    "219": {
        "inputs": {
        "mask": [
            "331",
            0
        ]
        },
        "class_type": "MaskToImage",
        "_meta": {
        "title": "Convert Mask to Image"
        }
    },
    "251": {
        "inputs": {
        "image": "ad_3.jpg",
        "upload": "image"
        },
        "class_type": "LoadImage",
        "_meta": {
        "title": "Load Image"
        }
    },
    "256": {
        "inputs": {
        "images": [
            "260",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "257": {
        "inputs": {
        "images": [
            "264",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "258": {
        "inputs": {
        "image": [
            "410",
            0
        ]
        },
        "class_type": "SplitImageWithAlpha",
        "_meta": {
        "title": "Split Image with Alpha"
        }
    },
    "259": {
        "inputs": {
        "image": [
            "258",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "260": {
        "inputs": {
        "radius": 5,
        "images": [
            "258",
            0
        ]
        },
        "class_type": "ImageGaussianBlur",
        "_meta": {
        "title": "Image Gaussian Blur"
        }
    },
    "261": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.4,
        "image_a": [
            "259",
            0
        ],
        "image_b": [
            "260",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "263": {
        "inputs": {
        "image": [
            "261",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "264": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 1,
        "image_a": [
            "260",
            0
        ],
        "image_b": [
            "263",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "269": {
        "inputs": {
        "images": [
            "273",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "270": {
        "inputs": {
        "images": [
            "277",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "271": {
        "inputs": {
        "image": [
            "7",
            0
        ]
        },
        "class_type": "SplitImageWithAlpha",
        "_meta": {
        "title": "Split Image with Alpha"
        }
    },
    "272": {
        "inputs": {
        "image": [
            "271",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "273": {
        "inputs": {
        "radius": 5,
        "images": [
            "271",
            0
        ]
        },
        "class_type": "ImageGaussianBlur",
        "_meta": {
        "title": "Image Gaussian Blur"
        }
    },
    "274": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.5,
        "image_a": [
            "272",
            0
        ],
        "image_b": [
            "273",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "276": {
        "inputs": {
        "image": [
            "274",
            0
        ]
        },
        "class_type": "ImageInvert",
        "_meta": {
        "title": "Invert Image"
        }
    },
    "277": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 1,
        "image_a": [
            "273",
            0
        ],
        "image_b": [
            "276",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "291": {
        "inputs": {
        "images": [
            "308",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "305": {
        "inputs": {
        "blend_percentage": 1,
        "image_a": [
            "277",
            0
        ],
        "image_b": [
            "264",
            0
        ],
        "mask": [
            "320",
            0
        ]
        },
        "class_type": "Image Blend by Mask",
        "_meta": {
        "title": "Image Blend by Mask"
        }
    },
    "306": {
        "inputs": {
        "images": [
            "305",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "307": {
        "inputs": {
        "mode": "add",
        "blend_percentage": 0.65,
        "image_a": [
            "273",
            0
        ],
        "image_b": [
            "305",
            0
        ]
        },
        "class_type": "Image Blending Mode",
        "_meta": {
        "title": "Image Blending Mode"
        }
    },
    "308": {
        "inputs": {
        "black_level": 83,
        "mid_level": 127,
        "white_level": 172,
        "image": [
            "307",
            0
        ]
        },
        "class_type": "Image Levels Adjustment",
        "_meta": {
        "title": "Image Levels Adjustment"
        }
    },
    "315": {
        "inputs": {
        "strength": 0.2,
        "conditioning": [
            "214",
            0
        ],
        "control_net": [
            "316",
            0
        ],
        "image": [
            "318",
            0
        ]
        },
        "class_type": "ControlNetApply",
        "_meta": {
        "title": "Apply ControlNet (OLD)"
        }
    },
    "316": {
        "inputs": {
        "control_net_name": "control_v11p_sd15_lineart_fp16.safetensors"
        },
        "class_type": "ControlNetLoader",
        "_meta": {
        "title": "Load ControlNet Model"
        }
    },
    "317": {
        "inputs": {
        "ckpt_name": "depth_anything_vitl14.pth",
        "resolution": 512,
        "image": [
            "410",
            0
        ]
        },
        "class_type": "DepthAnythingPreprocessor",
        "_meta": {
        "title": "Depth Anything"
        }
    },
    "318": {
        "inputs": {
        "resolution": 512,
        "image": [
            "410",
            0
        ]
        },
        "class_type": "AnimeLineArtPreprocessor",
        "_meta": {
        "title": "Anime Lineart"
        }
    },
    "320": {
        "inputs": {
        "mask": [
            "331",
            0
        ]
        },
        "class_type": "MaskToImage",
        "_meta": {
        "title": "Convert Mask to Image"
        }
    },
    "330": {
        "inputs": {
        "expand": 30,
        "tapered_corners": true,
        "mask": [
            "406",
            1
        ]
        },
        "class_type": "GrowMask",
        "_meta": {
        "title": "GrowMask"
        }
    },
    "331": {
        "inputs": {
        "expand": -30,
        "tapered_corners": true,
        "mask": [
            "330",
            0
        ]
        },
        "class_type": "GrowMask",
        "_meta": {
        "title": "GrowMask"
        }
    },
    "345": {
        "inputs": {
        "samples": [
            "346",
            0
        ],
        "mask": [
            "347",
            0
        ]
        },
        "class_type": "SetLatentNoiseMask",
        "_meta": {
        "title": "Set Latent Noise Mask"
        }
    },
    "346": {
        "inputs": {
        "pixels": [
            "410",
            0
        ],
        "vae": [
            "82",
            2
        ]
        },
        "class_type": "VAEEncode",
        "_meta": {
        "title": "VAE Encode"
        }
    },
    "347": {
        "inputs": {
        "mask": [
            "331",
            0
        ]
        },
        "class_type": "InvertMask",
        "_meta": {
        "title": "InvertMask"
        }
    },
    "349": {
        "inputs": {
        "filename_prefix": "ComfyUI",
        "images": [
            "217",
            0
        ]
        },
        "class_type": "SaveImage",
        "_meta": {
        "title": "Save Image"
        }
    },
    "353": {
        "inputs": {
        "filename_prefix": "ComfyUI",
        "images": [
            "308",
            0
        ]
        },
        "class_type": "SaveImage",
        "_meta": {
        "title": "Save Image"
        }
    },
    "357": {
        "inputs": {
        "text": [
            "412",
            0
        ]
        },
        "class_type": "ttN text",
        "_meta": {
        "title": "positive prompt"
        }
    },
    "359": {
        "inputs": {
        "text": "nsfw"
        },
        "class_type": "ttN text",
        "_meta": {
        "title": "negative prompt"
        }
    },
    "364": {
        "inputs": {
        "images": [
            "307",
            0
        ]
        },
        "class_type": "PreviewImage",
        "_meta": {
        "title": "Preview Image"
        }
    },
    "405": {
        "inputs": {
        "model": "u2net: general purpose",
        "providers": "CPU"
        },
        "class_type": "RemBGSession+",
        "_meta": {
        "title": "🔧 RemBG Session"
        }
    },
    "406": {
        "inputs": {
        "rembg_session": [
            "405",
            0
        ],
        "image": [
            "410",
            0
        ]
        },
        "class_type": "ImageRemoveBackground+",
        "_meta": {
        "title": "🔧 Image Remove Background"
        }
    },
    "408": {
        "inputs": {
        "red": 255,
        "green": 255,
        "blue": 255,
        "threshold": 0,
        "image": [
            "217",
            0
        ]
        },
        "class_type": "MaskFromColor+",
        "_meta": {
        "title": "🔧 Mask From Color"
        }
    },
    "409": {
        "inputs": {
        "width": 512,
        "height": 512,
        "interpolation": "nearest",
        "method": "stretch",
        "condition": "always",
        "multiple_of": 0,
        "image": [
            "217",
            0
        ]
        },
        "class_type": "ImageResize+",
        "_meta": {
        "title": "🔧 Image Resize"
        }
    },
    "410": {
        "inputs": {
        "width": 1024,
        "height": 1024,
        "interpolation": "nearest",
        "method": "keep proportion",
        "condition": "always",
        "multiple_of": 0,
        "image": [
            "251",
            0
        ]
        },
        "class_type": "ImageResize+",
        "_meta": {
        "title": "🔧 Image Resize"
        }
    },
    "411": {
        "inputs": {
        "prompt": "제품 뒤에 벛꽃이 흩날리는 사진",
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "llama3:latest",
        "system": "너는 똑똑한 AI 이미지 생성형 프롬프트 작성자야. 입력받은 프롬프트를 기반으로 생성형 AI 이미지 모델을 이용해 독특한 광고 이미지를 생성하기 위한 프롬프트를 작성해줘. 프롬프트는 실제 사진을 묘사해야 하고, 영어로 작성되어야해. 주제, 구도, 분위기, 색감, 조명 등을 각각의 문단 별로 최대한 자세히 서술해줘.\\n답변은 생성한 프롬프트만 하면 돼. ",
        "seed": 756191439,
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
    "412": {
        "inputs": {
        "prompt": [
            "411",
            0
        ],
        "debug": false,
        "url": "http://127.0.0.1:11434",
        "model": "qwen2m:latest",
        "system": "프롬프트를 한 문장으로 요약해줘. 프롬프트는 영어여야 해\\n답변은 오직 프롬프트만 보내줘.",
        "seed": 1802146844,
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
    "413": {
        "inputs": {
        "text": [
            "411",
            0
        ],
        "text2": "Here is the prompt:\\n\\n**Theme:** Whimsical Romance\\n\\n**Composition:** A product (e.g. jewelry, cosmetics, luxury watch) is placed at the center of a serene and idyllic scene, with cherry blossoms (sakura) gently falling from above, creating a soft and romantic ambiance.\\n\\n**Mood:** Dreamy, ethereal, and whimsical, evoking a sense of enchantment and wonder. The overall atmosphere should be tranquil and peaceful, inviting the viewer to step into the serene world.\\n\\n**Color Palette:**\\n\\n* Soft pastel shades (pink, peach, lavender) for the cherry blossoms\\n* Warm beige or cream tones for the product and its packaging\\n* Subtle hints of blue or green in the background to evoke a sense of sky or nature\\n\\n**Lighting:** Soft, gentle, and diffused natural light, as if the scene is bathed in the soft glow of dawn or early evening. Avoid harsh or dramatic lighting.\\n\\n**Additional Details:**\\n\\n* The cherry blossoms should be falling from above, creating a sense of movement and dynamics\\n* The product should be prominently featured, with enough space around it to create a sense of breathing room\\n* Incorporate some subtle textures or patterns in the background (e.g. grass, stones) to add depth and visual interest\\n\\nThe goal is to create an image that is both visually stunning and evocative, capturing the viewer's imagination and inviting them to explore the whimsical world within."
        },
        "class_type": "ShowText|pysssss",
        "_meta": {
        "title": "Show Text 🐍"
        }
    },
    "416": {
        "inputs": {
        "text": [
            "412",
            0
        ],
        "text2": "Craft a dreamy, ethereal image featuring a product at the center of a tranquil sakura blossom scene bathed in soft, warm light, where delicate cherry petals fall gently around it, creating a sense of enchantment and wonder with a color palette of soft pastels, warm beiges, and subtle blues or greens, and incorporate gentle movement and depth through falling blossoms and textures."
        },
        "class_type": "ShowText|pysssss",
        "_meta": {
        "title": "Show Text 🐍"
        }
    },
    "418": {
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
    "419": {
        "inputs": {
        "clip_name": "t5xxl_fp8_e4m3fn.safetensors",
        "type": "sd3"
        },
        "class_type": "CLIPLoader",
        "_meta": {
        "title": "Load CLIP"
        }
    },
    "420": {
        "inputs": {
        "prompt": [
            "412",
            0
        ],
        "strength": 1,
        "force_offload": true,
        "clip": [
            "419",
            0
        ]
        },
        "class_type": "CogVideoTextEncode",
        "_meta": {
        "title": "CogVideo TextEncode"
        }
    },
    "421": {
        "inputs": {
        "prompt": "nsfw",
        "strength": 1,
        "force_offload": true,
        "clip": [
            "419",
            0
        ]
        },
        "class_type": "CogVideoTextEncode",
        "_meta": {
        "title": "CogVideo TextEncode"
        }
    },
    "423": {
        "inputs": {
        "width": 720,
        "height": 480,
        "upscale_method": "lanczos",
        "keep_proportion": false,
        "divisible_by": 16,
        "crop": "disabled",
        "image": [
            "308",
            0
        ]
        },
        "class_type": "ImageResizeKJ",
        "_meta": {
        "title": "Resize Image"
        }
    },
    "424": {
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
            "425",
            0
        ]
        },
        "class_type": "VHS_VideoCombine",
        "_meta": {
        "title": "Video Combine 🎥🅥🅗🅢"
        }
    },
    "425": {
        "inputs": {
        "enable_vae_tiling": false,
        "tile_sample_min_height": 96,
        "tile_sample_min_width": 96,
        "tile_overlap_factor_height": 0.083,
        "tile_overlap_factor_width": 0.083,
        "auto_tile_size": true,
        "pipeline": [
            "426",
            0
        ],
        "samples": [
            "426",
            1
        ]
        },
        "class_type": "CogVideoDecode",
        "_meta": {
        "title": "CogVideo Decode"
        }
    },
    "426": {
        "inputs": {
        "height": 480,
        "width": 720,
        "num_frames": 49,
        "steps": 25,
        "cfg": 6,
        "seed": 65334758276105,
        "scheduler": "DDIM",
        "denoise_strength": 1,
        "pipeline": [
            "418",
            0
        ],
        "positive": [
            "420",
            0
        ],
        "negative": [
            "421",
            0
        ],
        "image_cond_latents": [
            "427",
            0
        ]
        },
        "class_type": "CogVideoSampler",
        "_meta": {
        "title": "CogVideo Sampler"
        }
    },
    "427": {
        "inputs": {
        "chunk_size": 16,
        "enable_tiling": true,
        "pipeline": [
            "418",
            0
        ],
        "image": [
            "423",
            0
        ]
        },
        "class_type": "CogVideoImageEncode",
        "_meta": {
        "title": "CogVideo ImageEncode"
        }
    }
    }
"""

def make_advertise(image_value, prompt_value, generated_video_name, is_vertical=False ):
    prompt = json.loads(prompt_text)
    prompt["251"]["inputs"]["image"] = image_value
    prompt["411"]["inputs"]["prompt"] = prompt_value
  
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    videos = get_videos(ws, prompt)
    ws.close()
    video_paths = []
    for node_id in videos.keys():
        if node_id == "424":
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
  