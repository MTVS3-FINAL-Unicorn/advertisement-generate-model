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

def get_image(filename, subfolder, folder_type):
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
            # If you want to be able to decode the binary stream for latent previews, here is how you can do it:
            bytesIO = BytesIO(out[8:])
            preview_image = Image.open(bytesIO) # This is your preview in PIL image format, store it in a global
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    generated_prompts = []
    for node_id in history['outputs']:
      node_output = history['outputs'][node_id]
      images_output = []
      if 'images' in node_output:
        for image in node_output['images']:
            image_data = get_image(image['filename'], image['subfolder'], image['type'])
            images_output.append(image_data)
      if 'text' in node_output:
        for text in node_output['text']:
          generated_prompts.append(text)
      output_images[node_id] = images_output
    return output_images, generated_prompts

prompt_text = """
{
  "3": {
    "inputs": {
      "seed": 0,
      "steps": 50,
      "cfg": 1.6,
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
      "image": "KakaoTalk_20241121_152121564_07.webp",
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
            "url": "/api/view?filename=rgthree.compare._temp_sbdvq_00001_.png&type=temp&subfolder=&rand=0.2857107034322901"
          },
          {
            "name": "B",
            "selected": true,
            "url": "/api/view?filename=rgthree.compare._temp_sbdvq_00002_.png&type=temp&subfolder=&rand=0.6821615544108421"
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
      "radius": 1,
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
      "black_level": 50,
      "mid_level": 130,
      "white_level": 200,
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
  "90": {
    "inputs": {
      "prompt": " an advertisement video showcasing MR glasses called MetaLens, where the glasses come into focus while the background features a newborn and their parents.",
      "debug": false,
      "url": "http://127.0.0.1:11434",
      "model": "qwen2m:latest",
      "system": "너는 똑똑한 AI 이미지 생성형 프롬프트 작성자야. 입력받은 프롬프트를 기반으로 생성형 AI 이미지 모델을 이용해 광고 이미지를 생성하기 위한 프롬프트를 작성해줘. 프롬프트는 실제 사진을 묘사해야 하고, 영어로 작성되어야해. 주제, 구도, 분위기, 색감, 조명 등을 각각의 문단 별로 최대한 자세히 서술해줘.\\n답변은 생성한 프롬프트만 하면 돼.",
      "seed": 1637683722,
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
      "system": "프롬프트를 한 문장으로 요약해줘. 프롬프트는 영어여야 해\\n답변은 오직 프롬프트만 보내줘.",
      "seed": 1705580069,
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
      "text2": "Create an advertisement video for MR glasses named \\"MetaLens\\". The central scene is set on a warm evening in a cozy nursery with soft, natural lighting casting a glow over everything.\\n\\nScene 1:\\nFrame the MetaLens glasses against a light gray backdrop. The glasses should be prominently displayed at eye level, looking sleek and futuristic. The camera zooms into the product from afar to show its compact size and smooth curves.\\n\\nScene 2: \\nThe scene shifts to reveal a newborn baby in their crib in the nursery. The newborn is softly swaddled under a blanket of calming blue tones, creating a peaceful ambiance that contrasts beautifully with the high-tech glasses. \\n\\nScene 3:\\nNext focus on the parents sitting nearby, observing the baby from afar. Both parents are depicted as tech enthusiasts or modern-day explorers, wearing casual yet stylish clothing to complement their futuristic surroundings.\\n\\nScene 4: \\nShow one of the parents picking up MetaLens and adjusting it slightly before placing them on their face. The glasses should adjust themselves effortlessly onto their nose bridge when they're positioned correctly, demonstrating user-friendly technology.\\n\\nScene 5:\\nThe focus then shifts from the glasses to a blurred background of the nursery scenery behind the parents as the MetaLens comes into full view and sharp focus. The glasses create an immersive environment where the digital and physical worlds seamlessly blend together.\\n\\nScene 6:\\nNext, frame close-ups of both parents wearing the MetaLens while exploring scenes like looking at stars in their room or a magical underwater world through augmented reality enhancements that appear to be real.\\n\\nScene 7: \\nShow the baby's reactions subtly as they are unaware of this digital experience happening around them. Their eyes might catch the glow from the digital images, providing a touch of innocence and wonderment.\\n\\nScene 8:\\nEnd with an aerial view shot showcasing the family together in their nursery enjoying the augmented reality features offered by MetaLens while overlooking the beauty of nature through their window, highlighting the harmony between technology and life.\\n\\nScene 9: \\nCut to a voice-over narrating the benefits of MetaLens - such as creating endless possibilities for bonding over shared experiences, making learning fun, or just enhancing daily routines in a unique way.\\n\\nScene 10:\\nFinally, display MetaLens' slogan alongside its price tag or available offers, encouraging viewers to take action and experience this innovative technology themselves."
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
      "text2": "The advertisement video for MR glasses named \\"MetaLens\\" will feature scenes transitioning from the sleek display of the product against a backdrop, through a serene nursery with a sleeping baby and involved parents, to the practical use of MetaLens by both adults experiencing an augmented reality that blends seamlessly with their environment. This showcases how MetaLens enhances daily life while preserving the innocence of others and is complemented by a voice-over highlighting its benefits before concluding with a call-to-action including the slogan and pricing details."
    },
    "class_type": "ShowText|pysssss",
    "_meta": {
      "title": "Show Text 🐍"
    }
  }
}
"""

async def make_image(image_path, prompt_value, image_name, is_vertical=False):
  prompt = json.loads(prompt_text)
  prompt["33"]["inputs"]["image"] = image_path
  prompt["90"]["inputs"]["prompt"] = prompt_value
  ws = websocket.WebSocket()
  ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
  images, generated_prompts = get_images(ws, prompt)
  ws.close()
  
  image_paths = []
  for node_id in images.keys():
    if node_id == "9":
      for image_data in images[node_id]:
          import io
          from PIL import Image
          import os
          os.makedirs('./tmp', exist_ok=True)
          image = Image.open(io.BytesIO(image_data))
          image_path = f'./tmp/{image_name}'
          image_paths.append(image_path)
          image.save(image_path)
          
  # print('프롬프트:', generated_prompts)
  return generated_prompts[1]
        
if __name__ == "__main__":
  image_path = "ad_3.jpg"
  prompt_value = "싱그러운 숲 속에 놓인 제품, 환상적인 느낌과 자연친화적인 분위기. 고화질"
  image_name = "output"
  make_image(image_path, prompt_value, image_name)
  