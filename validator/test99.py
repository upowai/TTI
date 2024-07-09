import numpy as np
from PIL import Image, UnidentifiedImageError
import logging
import imagehash


def compare_images(images_info: list, hash_threshold: int = 5):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    images = []
    image_paths = [info["path"] for info in images_info]
    image_names = [info["name"] for info in images_info]

    for i, path in enumerate(image_paths):
        try:
            image = Image.open(path).convert("RGB")
            images.append(image)
        except FileNotFoundError as e:
            logger.error(f"File not found: {image_names[i]} ({path}) - {e}")
            return
        except UnidentifiedImageError as e:
            logger.error(f"Cannot identify image file: {image_names[i]} ({path}) - {e}")
            return
        except Exception as e:
            logger.error(
                f"An error occurred while loading image {image_names[i]} ({path}): {e}"
            )
            return

    try:
        # Perceptual hashing
        hashes = [imagehash.phash(image) for image in images]
        hash_diffs = [
            (i, j, abs(hashes[i] - hashes[j]))
            for i in range(len(hashes))
            for j in range(i + 1, len(hashes))
        ]
        logger.info(
            f"Perceptual hash differences: {[(image_names[i], image_names[j], diff) for i, j, diff in hash_diffs]}"
        )
    except Exception as e:
        logger.error(f"An error occurred during hashing: {e}")
        return

    # Compare hash differences with threshold
    similar_pairs = [pair for pair in hash_diffs if pair[2] < hash_threshold]

    results = {name: "failed" for name in image_names}
    if len(similar_pairs) == 3:
        logger.info("All three images are similar.")
        results = {name: "passed" for name in image_names}
    elif len(similar_pairs) == 0:
        logger.info("All three images are different.")
    else:
        match_count = {name: 0 for name in image_names}
        for i, j, diff in similar_pairs:
            match_count[image_names[i]] += 1
            match_count[image_names[j]] += 1
            logger.info(
                f"Images {image_names[i]} and {image_names[j]} are similar (difference: {diff})."
            )

        majority_pass = [name for name, count in match_count.items() if count >= 1]
        for name in majority_pass:
            results[name] = "passed"

    return results


# Example usage
images_info = [
    {"name": "Image 1", "path": "./output/1.png"},
    {"name": "Image 2", "path": "./output/2.png"},
    {"name": "Image 3", "path": "./output/3.png"},
]

results = compare_images(images_info)
print(results)
