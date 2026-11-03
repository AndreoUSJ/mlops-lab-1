import argparse
import hashlib
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError

try:
    from src.food11.data import CLASSES
except ModuleNotFoundError:
    from data import CLASSES


SPLITS = ["training", "validation", "evaluation"]


def print_result(name: str, passed: bool, details: str = "") -> None:
    status = "PASS" if passed else "FAIL"

    if details:
        print(f"{status} - {name}: {details}")
    else:
        print(f"{status} - {name}")


def validate_class_folders(dataset: Path) -> bool:
    passed = True
    expected = set(CLASSES)

    for split in SPLITS:
        split_path = dataset / split

        if not split_path.exists():
            print_result(
                "class folders",
                False,
                f"{split} folder is missing",
            )
            passed = False
            continue

        actual = {
            path.name
            for path in split_path.iterdir()
            if path.is_dir()
        }

        if actual != expected:
            missing = expected - actual
            extra = actual - expected

            details = []

            if missing:
                details.append(
                    f"missing={sorted(missing)}"
                )

            if extra:
                details.append(
                    f"extra={sorted(extra)}"
                )

            print_result(
                "class folders",
                False,
                f"{split}: {', '.join(details)}",
            )

            passed = False

    if passed:
        print_result(
            "class folders",
            True,
            "all splits contain exactly 11 classes",
        )

    return passed


def validate_images(dataset: Path) -> bool:
    passed = True

    for split in SPLITS:
        for class_name in CLASSES:
            folder = dataset / split / class_name

            if not folder.exists():
                continue

            for path in folder.iterdir():
                if not path.is_file():
                    continue

                try:
                    with Image.open(path) as image:
                        image.load()

                        if image.mode != "RGB":
                            print_result(
                                "image format",
                                False,
                                f"{path} is {image.mode}, expected RGB",
                            )
                            passed = False

                        if image.size != (128, 128):
                            print_result(
                                "image size",
                                False,
                                f"{path} is {image.size}",
                            )
                            passed = False

                except (OSError, UnidentifiedImageError):
                    print_result(
                        "image validation",
                        False,
                        f"cannot open {path}",
                    )
                    passed = False

    if passed:
        print_result(
            "image validation",
            True,
            "all images are RGB and 128x128",
        )

    return passed


def validate_minimum_count(
    dataset: Path,
    min_per_class: int,
) -> bool:
    passed = True

    for split in SPLITS:
        for class_name in CLASSES:
            folder = dataset / split / class_name

            if not folder.exists():
                passed = False
                continue

            count = sum(
                1
                for path in folder.iterdir()
                if path.is_file()
            )

            if count < min_per_class:
                print_result(
                    "minimum count",
                    False,
                    (
                        f"{split}/{class_name} has "
                        f"{count}, expected at least "
                        f"{min_per_class}"
                    ),
                )
                passed = False

    if passed:
        print_result(
            "minimum count",
            True,
            f"every class has at least {min_per_class} images",
        )

    return passed


def validate_no_duplicates(dataset: Path) -> bool:
    seen: dict[str, tuple[str, Path]] = {}
    passed = True

    for split in SPLITS:
        for class_name in CLASSES:
            folder = dataset / split / class_name

            if not folder.exists():
                continue

            for path in folder.iterdir():
                if not path.is_file():
                    continue

                file_hash = hashlib.md5(
                    path.read_bytes(),
                    usedforsecurity=False,
                ).hexdigest()

                if file_hash in seen:
                    previous_split, previous_path = seen[file_hash]

                    if previous_split != split:
                        print_result(
                            "duplicate images",
                            False,
                            (
                                f"{path} duplicates "
                                f"{previous_path}"
                            ),
                        )
                        passed = False
                else:
                    seen[file_hash] = (split, path)

    if passed:
        print_result(
            "duplicate images",
            True,
            "no image appears in multiple splits",
        )

    return passed


def class_distribution(
    dataset: Path,
    split: str,
) -> dict[str, float]:
    counts = {}

    for class_name in CLASSES:
        folder = dataset / split / class_name

        if not folder.exists():
            counts[class_name] = 0
            continue

        counts[class_name] = sum(
            1
            for path in folder.iterdir()
            if path.is_file()
        )

    total = sum(counts.values())

    if total == 0:
        return {
            class_name: 0.0
            for class_name in CLASSES
        }

    return {
        class_name: count / total
        for class_name, count in counts.items()
    }


def validate_distribution(
    dataset: Path,
    tau: float,
) -> bool:
    training = class_distribution(
        dataset,
        "training",
    )

    validation = class_distribution(
        dataset,
        "validation",
    )

    passed = True

    for class_name in CLASSES:
        difference = abs(
            training[class_name]
            - validation[class_name]
        )

        if difference > tau:
            print_result(
                "class distribution",
                False,
                (
                    f"{class_name}: difference "
                    f"{difference:.4f} > {tau}"
                ),
            )

            passed = False

    if passed:
        print_result(
            "class distribution",
            True,
            f"all differences are within tau={tau}",
        )

    return passed


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "dataset",
        type=Path,
    )

    parser.add_argument(
        "--min-per-class",
        type=int,
        default=50,
    )

    parser.add_argument(
        "--tau",
        type=float,
        default=0.05,
    )

    args = parser.parse_args()

    checks = [
        validate_class_folders(args.dataset),
        validate_images(args.dataset),
        validate_minimum_count(
            args.dataset,
            args.min_per_class,
        ),
        validate_no_duplicates(args.dataset),
        validate_distribution(
            args.dataset,
            args.tau,
        ),
    ]

    if all(checks):
        print("\nData contract passed.")
        sys.exit(0)

    print("\nData contract failed.")
    sys.exit(1)


if __name__ == "__main__":
    main()