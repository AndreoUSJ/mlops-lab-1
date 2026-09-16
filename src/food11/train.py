import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("food11")


# ---------------------------------------------------------
# Command-line arguments
# ---------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Train a Food-11 classifier using ResNet18"
    )

    parser.add_argument(
        "--dataset",
        choices=["processed", "mini"],
        default="mini",
        help="Dataset to use: processed or mini",
    )

    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs",
    )

    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size",
    )

    return parser.parse_args()


# ---------------------------------------------------------
# Load Food-11 datasets
# ---------------------------------------------------------

def create_dataloaders(dataset_name, batch_size):

    if dataset_name == "mini":
        data_dir = PROJECT_ROOT / "data" / "food11_processed_mini"
    else:
        data_dir = PROJECT_ROOT / "data" / "food11_processed"

    train_dir = data_dir / "training"
    val_dir = data_dir / "validation"
    test_dir = data_dir / "evaluation"

    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    train_dataset = datasets.ImageFolder(
        train_dir,
        transform=transform,
    )

    val_dataset = datasets.ImageFolder(
        val_dir,
        transform=transform,
    )

    test_dataset = datasets.ImageFolder(
        test_dir,
        transform=transform,
    )

    print("Classes:")
    print(train_dataset.classes)

    print(f"Training images: {len(train_dataset)}")
    print(f"Validation images: {len(val_dataset)}")
    print(f"Test images: {len(test_dataset)}")

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    return train_loader, val_loader, test_loader


# ---------------------------------------------------------
# Create pretrained ResNet18
# ---------------------------------------------------------

def create_model():

    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(
        weights=weights
    )

    # ResNet18 normally outputs 1000 ImageNet classes.
    # Food-11 contains 11 classes.
    number_features = model.fc.in_features

    model.fc = nn.Linear(
        number_features,
        11,
    )

    return model


# ---------------------------------------------------------
# Evaluate model
# ---------------------------------------------------------

def evaluate(model, loader, criterion, device):

    model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                labels,
            )

            total_loss += loss.item() * images.size(0)

            _, predictions = torch.max(
                outputs,
                1,
            )

            correct += (
                predictions == labels
            ).sum().item()

            total += labels.size(0)

    average_loss = total_loss / total
    accuracy = correct / total

    return average_loss, accuracy


# ---------------------------------------------------------
# Main training function
# ---------------------------------------------------------

def train(args):

    # Select GPU if available, otherwise CPU
    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Using device: {device}")

    # Load datasets
    train_loader, val_loader, test_loader = create_dataloaders(
        args.dataset,
        args.batch_size,
    )

    # Build pretrained ResNet18
    model = create_model()

    model = model.to(device)

    criterion = nn.CrossEntropyLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    # -----------------------------------------------------
    # Start MLflow run
    # -----------------------------------------------------

    with mlflow.start_run():

        # Log hyperparameters once at the beginning
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "num_classes": 11,
            }
        )

        # -------------------------------------------------
        # Training loop
        # -------------------------------------------------

        for epoch in range(args.epochs):

            model.train()

            running_loss = 0.0
            total_samples = 0

            for images, labels in train_loader:

                images = images.to(device)
                labels = labels.to(device)

                optimizer.zero_grad()

                outputs = model(images)

                loss = criterion(
                    outputs,
                    labels,
                )

                loss.backward()

                optimizer.step()

                running_loss += (
                    loss.item()
                    * images.size(0)
                )

                total_samples += images.size(0)

            train_loss = (
                running_loss
                / total_samples
            )

            # ---------------------------------------------
            # Validation
            # ---------------------------------------------

            val_loss, val_accuracy = evaluate(
                model,
                val_loader,
                criterion,
                device,
            )

            print(
                f"Epoch {epoch + 1}/{args.epochs} "
                f"- train_loss: {train_loss:.4f} "
                f"- val_loss: {val_loss:.4f} "
                f"- val_accuracy: {val_accuracy:.4f}"
            )

            # Log metrics after every epoch
            mlflow.log_metric(
                "train_loss",
                train_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_loss",
                val_loss,
                step=epoch,
            )

            mlflow.log_metric(
                "val_accuracy",
                val_accuracy,
                step=epoch,
            )

        # -------------------------------------------------
        # Final test evaluation
        # -------------------------------------------------

        test_loss, test_accuracy = evaluate(
            model,
            test_loader,
            criterion,
            device,
        )

        print(
            f"Final test accuracy: "
            f"{test_accuracy:.4f}"
        )

        mlflow.log_metric(
            "test_accuracy",
            test_accuracy,
        )

        mlflow.log_metric(
            "test_loss",
            test_loss,
        )

        # -------------------------------------------------
        # Save trained model as MLflow artifact
        # -------------------------------------------------

        mlflow.pytorch.log_model(
    model,
    name="model",
    serialization_format="pickle",
)

        print("Model logged to MLflow.")


# ---------------------------------------------------------
# Program entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    args = parse_args()

    train(args)