from pathlib import Path
from PIL import Image


# Food-11 category mapping
CATEGORIES = {
    0: "Bread",
    1: "Dairy product",
    2: "Dessert",
    3: "Egg",
    4: "Fried food",
    5: "Meat",
    6: "Noodles-Pasta",
    7: "Rice",
    8: "Seafood",
    9: "Soup",
    10: "Vegetable-Fruit",
}

IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "food11_raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "food11_processed"
MINI_DIR = PROJECT_ROOT / "data" / "food11_processed_mini"

SPLITS = ["training", "evaluation", "validation"]


def prepare_data():
    for split in SPLITS:
        raw_split = RAW_DIR / split

        # Keep track of how many images are added to each mini category
        mini_counts = {category: 0 for category in CATEGORIES.values()}

        for image_path in sorted(raw_split.iterdir()):
            if not image_path.is_file():
                continue

            try:
                # Food-11 filenames begin with the category number
                # Example: 0_123.jpg -> category 0 -> Bread
                category_id = int(image_path.stem.split("_")[0])
            except (ValueError, IndexError):
                print(f"Skipping unexpected filename: {image_path.name}")
                continue

            if category_id not in CATEGORIES:
                print(f"Skipping unknown category: {image_path.name}")
                continue

            category_name = CATEGORIES[category_id]

            processed_category = PROCESSED_DIR / split / category_name
            mini_category = MINI_DIR / split / category_name

            processed_category.mkdir(parents=True, exist_ok=True)
            mini_category.mkdir(parents=True, exist_ok=True)

            try:
                with Image.open(image_path) as image:
                    image = image.convert("RGB")
                    image = image.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)

                    # Save to the full processed dataset
                    processed_output = processed_category / image_path.name
                    image.save(processed_output)

                    # Save at most 100 images per category in the mini dataset
                    if mini_counts[category_name] < MINI_LIMIT:
                        mini_output = mini_category / image_path.name
                        image.save(mini_output)
                        mini_counts[category_name] += 1

            except Exception as error:
                print(f"Error processing {image_path.name}: {error}")

        print(f"Finished processing {split}")

    print("Data preparation completed.")


if __name__ == "__main__":
    prepare_data()