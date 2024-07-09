import os
import logging
import json
import time
import torch
from diffusers import DiffusionPipeline, EulerAncestralDiscreteScheduler

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s - %(message)s"
)

# Setup default device
default_device_name = torch.device("cuda")
torch_dtype = torch.float16


def log_device_info():
    device_count = torch.cuda.device_count()
    logging.info(f"Number of devices available: {device_count}")

    if device_count > 0:
        for i in range(device_count):
            logging.info(f"Device {i}: {torch.cuda.get_device_name(i)}")
    else:
        logging.error("No CUDA devices available. Exiting.")
        exit()


def get_device(device_number):
    if device_number < torch.cuda.device_count():
        device_name = torch.device(f"cuda:{device_number}")
        logging.info(
            f"Selected device {device_number}: {torch.cuda.get_device_name(device_number)}"
        )
        return device_name
    else:
        logging.error(f"Device number {device_number} not available. Exiting.")
        exit()


def load_model_and_pipeline(model_path, torch_dtype, device_name):
    try:
        pipe = DiffusionPipeline.from_pretrained(
            model_path, torch_dtype=torch_dtype, safety_checker=None
        )
        pipe = pipe.to(device_name)
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(
            pipe.scheduler.config
        )
        return pipe
    except Exception as e:
        logging.error(f"Error loading model and pipeline: {e}")
        return None


def get_prompt_embeddings(
    pipe, prompt, negative_prompt, split_character=",", device=default_device_name
):
    try:
        max_length = pipe.tokenizer.model_max_length
        input_ids = pipe.tokenizer(
            prompt, return_tensors="pt", truncation=False
        ).input_ids.to(device)
        negative_ids = pipe.tokenizer(
            negative_prompt, return_tensors="pt", truncation=False
        ).input_ids.to(device)

        input_length = input_ids.shape[-1]
        negative_length = negative_ids.shape[-1]

        if input_length > negative_length:
            padding_length = input_length - negative_length
            negative_ids = torch.nn.functional.pad(
                negative_ids, (0, padding_length), value=pipe.tokenizer.pad_token_id
            )
        elif negative_length > input_length:
            padding_length = negative_length - input_length
            input_ids = torch.nn.functional.pad(
                input_ids, (0, padding_length), value=pipe.tokenizer.pad_token_id
            )

        concat_embeds, neg_embeds = [], []
        for i in range(0, max(input_length, negative_length), max_length):
            concat_embeds.append(pipe.text_encoder(input_ids[:, i : i + max_length])[0])
            neg_embeds.append(pipe.text_encoder(negative_ids[:, i : i + max_length])[0])

        return torch.cat(concat_embeds, dim=1), torch.cat(neg_embeds, dim=1)
    except Exception as e:
        logging.error(f"Error generating prompt embeddings: {e}")
        return None, None


def generate_image(pipe, prompt, negative_prompt, seed, width, height, device_name):
    try:
        prompt_embeds, negative_prompt_embeds = get_prompt_embeddings(
            pipe, prompt, negative_prompt, device=device_name
        )
        generator = torch.manual_seed(seed)
        image = pipe(
            prompt_embeds=prompt_embeds,
            negative_prompt_embeds=negative_prompt_embeds,
            width=width,
            height=height,
            guidance_scale=7,
            num_inference_steps=28,
            num_images_per_prompt=1,
            generator=generator,
        ).images
        return image[0]
    except Exception as e:
        logging.error(f"Error generating image: {e}")
        return None


def save_image(image, output_folder):
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        timestamp = int(time.time())
        image_name = f"image_{timestamp}.png"
        image_path = os.path.join(output_folder, image_name)
        image.save(image_path)
        logging.info(f"Image saved at {image_path}")
        return image_path, image_name
    except Exception as e:
        logging.error(f"Error saving image: {e}")
        return None, None


# # Example of how to use the functions
# if __name__ == "__main__":
#     log_device_info()

#     # Example device number, change this to the desired device number
#     device_number = 0
#     device_name = get_device(device_number)

#     model_path = "amajicmixRealistic_v7"
#     pipe = load_model_and_pipeline(model_path, torch_dtype, device_name)

#     if pipe:
#         prompt = "A beautiful landscape"
#         negative_prompt = "ugly"
#         seed = 42
#         width = 512
#         height = 512
#         image = generate_image(
#             pipe, prompt, negative_prompt, seed, width, height, device_name
#         )

#         if image:
#             output_folder = "output_images"
#             save_image(image, output_folder)
