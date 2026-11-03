from pathlib import Path

from PIL import Image

CLASSES = [
    "Bread",
    "Dairy product",
    "Dessert",
    "Egg",
    "Fried food",
    "Meat",
    "Noodles-Pasta",
    "Rice",
    "Seafood",
    "Soup",
    "Vegetable-Fruit",
]

CATEGORIES = {index: name for index, name in enumerate(CLASSES)}

IMAGE_SIZE = (128, 128)
MINI_LIMIT = 100

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "food11_raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "food11_processed"
MINI_DIR = PROJECT_ROOT / "data" / "food11_processed_mini"

SPLITS = ["training", "evaluation", "validation"]


def category_from_filename(filename: str) -> str:
    """Example: '3_120.jpg' -> 'Egg'."""
    category_id = int(Path(filename).stem.split("_")[0])

    if category_id not in CATEGORIES:
        raise ValueError(f"Unknown category id: {category_id}")

    return CATEGORIES[category_id]


def resize_image(img: Image.Image, size: int = 128) -> Image.Image:
    """Return an RGB image resized to size x size."""
    return img.convert("RGB").resize(
        (size, size),
        Image.Resampling.LANCZOS,
    )


def prepare_data():
    for split in SPLITS:
        raw_split = RAW_DIR / split

        mini_counts = {
            category: 0
            for category in CATEGORIES.values()
        }

        for image_path in sorted(raw_split.iterdir()):
            if not image_path.is_file():
                continue

            try:
                category_name = category_from_filename(
                    image_path.name
                )

            except (ValueError, IndexError):
                print(
                    f"Skipping unexpected filename: "
                    f"{image_path.name}"
                )
                continue

            processed_category = (
                PROCESSED_DIR / split / category_name
            )

            mini_category = (
                MINI_DIR / split / category_name
            )

            processed_category.mkdir(
                parents=True,
                exist_ok=True,
            )

            mini_category.mkdir(
                parents=True,
                exist_ok=True,
            )

            try:
                with Image.open(image_path) as image:
                    image = resize_image(image)

                    processed_output = (
                        processed_category /
                        image_path.name
                    )

                    image.save(processed_output)

                    if mini_counts[category_name] < MINI_LIMIT:
                        mini_output = (
                            mini_category /
                            image_path.name
                        )

                        image.save(mini_output)

                        mini_counts[category_name] += 1

            except Exception as error:  # noqa: BLE001
                print(
                    f"Error processing "
                    f"{image_path.name}: {error}"
                )

        print(f"Finished processing {split}")

    print("Data preparation completed.")


if __name__ == "__main__":
    prepare_data()