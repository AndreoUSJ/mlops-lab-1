import io
import os
from typing import Annotated

import mlflow.pyfunc
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

import mlflow

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_URI = "models:/food11@champion"


app = FastAPI(
    title="Food-11 Classification API",
    description="Classify food images using the Food-11 ResNet18 model.",
    version="1.0.0",
)


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


transform = transforms.Compose(
    [
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


model = None


@app.on_event("startup")
def load_model():
    global model

    if os.environ.get("SKIP_MODEL"):
        print("SKIP_MODEL is set. Model loading skipped.")
        return

    print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"Loading model: {MODEL_URI}")

    model = mlflow.pyfunc.load_model(MODEL_URI)

    print("Model loaded successfully.")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
async def predict(
    file: Annotated[UploadFile, File()],
):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    try:
        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        ).convert("RGB")

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image.",
        )

    except Exception as error:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Could not read image: {error}",
        )

    image_tensor = transform(image)
    input_batch = image_tensor.unsqueeze(0)
    model_input = input_batch.numpy()

    try:
        predictions = model.predict(model_input)

    except Exception as error:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {error}",
        )

    logits = torch.as_tensor(predictions)

    probabilities = torch.softmax(
        logits,
        dim=1,
    )

    confidence, predicted_index = torch.max(
        probabilities,
        dim=1,
    )

    predicted_class = CLASSES[
        predicted_index.item()
    ]

    return {
        "category": predicted_class,
        "confidence": round(
            confidence.item(),
            4,
        ),
    }