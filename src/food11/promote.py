import argparse
import math
import os
from pathlib import Path

import mlflow

MODEL_NAME = "food11"
METRIC_NAME = "test_accuracy"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DIR = (
    PROJECT_ROOT
    / "data"
    / "food11_processed_mini"
    / "evaluation"
)


def get_test_size() -> int:
    return sum(
        1
        for path in TEST_DIR.rglob("*")
        if path.is_file()
    )


def get_accuracy(
    client: mlflow.MlflowClient,
    version,
) -> float:
    if not version.run_id:
        raise ValueError(
            f"Model version {version.version} has no run ID."
        )

    run = client.get_run(version.run_id)

    if METRIC_NAME not in run.data.metrics:
        raise ValueError(
            f"Run {version.run_id} does not contain "
            f"{METRIC_NAME}."
        )

    return run.data.metrics[METRIC_NAME]


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--version",
        required=True,
        type=int,
        help="Candidate model version",
    )

    args = parser.parse_args()

    tracking_uri = os.getenv(
        "MLFLOW_TRACKING_URI",
        "http://127.0.0.1:5000",
    )

    mlflow.set_tracking_uri(tracking_uri)

    client = mlflow.MlflowClient()

    candidate = client.get_model_version(
        MODEL_NAME,
        str(args.version),
    )

    champion = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    candidate_accuracy = get_accuracy(
        client,
        candidate,
    )

    champion_accuracy = get_accuracy(
        client,
        champion,
    )

    n = get_test_size()

    se = math.sqrt(
        champion_accuracy
        * (1 - champion_accuracy)
        / n
    )

    required_accuracy = (
        champion_accuracy + 2 * se
    )

    print(
        f"Champion version: {champion.version}"
    )
    print(
        f"Champion accuracy: {champion_accuracy:.4f}"
    )
    print(
        f"Candidate version: {candidate.version}"
    )
    print(
        f"Candidate accuracy: {candidate_accuracy:.4f}"
    )
    print(f"Test size: {n}")
    print(f"2 * SE: {2 * se:.4f}")
    print(
        f"Promotion threshold: "
        f"{required_accuracy:.4f}"
    )

    if candidate_accuracy >= required_accuracy:
        decision = "promoted"

        client.set_registered_model_alias(
            MODEL_NAME,
            "champion",
            args.version,
        )

        print("Decision: PROMOTED to champion")

    else:
        decision = "challenger"

        client.set_registered_model_alias(
            MODEL_NAME,
            "challenger",
            args.version,
        )

        print("Decision: kept as challenger")

    client.set_model_version_tag(
        MODEL_NAME,
        str(args.version),
        "promotion_decision",
        decision,
    )

    client.set_model_version_tag(
        MODEL_NAME,
        str(args.version),
        "candidate_test_accuracy",
        str(candidate_accuracy),
    )

    client.set_model_version_tag(
        MODEL_NAME,
        str(args.version),
        "champion_test_accuracy",
        str(champion_accuracy),
    )


if __name__ == "__main__":
    main()