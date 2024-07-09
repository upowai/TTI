import numpy as np
from PIL import Image, UnidentifiedImageError
import logging
import imagehash
from io import BytesIO


def compare_images(images_info: list, hash_threshold: int = 5):
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    images = []
    wallet_addresses = [info["wallet_address"] for info in images_info]

    if len(images_info) != 3:
        logger.error("There must be exactly three images for comparison.")
        return None

    for i, image_bytes in enumerate(images_info):
        try:
            image = Image.open(BytesIO(image_bytes["output"])).convert("RGB")
            images.append(image)
        except UnidentifiedImageError as e:
            logger.error(
                f"Cannot identify image file for wallet: {wallet_addresses[i]} - {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"An error occurred while loading image for wallet {wallet_addresses[i]}: {e}"
            )
            return None

    try:
        # Perceptual hashing
        hashes = [imagehash.phash(image) for image in images]
        hash_diffs = [
            (i, j, abs(hashes[i] - hashes[j]))
            for i in range(len(hashes))
            for j in range(i + 1, len(hashes))
        ]
        logger.info(
            f"Perceptual hash differences: {[(wallet_addresses[i], wallet_addresses[j], diff) for i, j, diff in hash_diffs]}"
        )
    except Exception as e:
        logger.error(f"An error occurred during hashing: {e}")
        return None

    # Compare hash differences with threshold
    similar_pairs = [pair for pair in hash_diffs if pair[2] < hash_threshold]

    results = {addr: "failed" for addr in wallet_addresses}
    if len(similar_pairs) == 3:
        logger.info("All three images are similar.")
        results = {addr: "passed" for addr in wallet_addresses}
    elif len(similar_pairs) == 0:
        logger.info("All three images are different.")
    else:
        match_count = {addr: 0 for addr in wallet_addresses}
        for i, j, diff in similar_pairs:
            match_count[wallet_addresses[i]] += 1
            match_count[wallet_addresses[j]] += 1
            logger.info(
                f"Images for wallets {wallet_addresses[i]} and {wallet_addresses[j]} are similar (difference: {diff})."
            )

        majority_pass = [addr for addr, count in match_count.items() if count >= 1]
        for addr in majority_pass:
            results[addr] = "passed"

    print("results:", results)

    return results
