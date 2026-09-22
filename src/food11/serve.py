import io
import os

import mlflow
import mlflow.pyfunc
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from torchvision import transforms


# ---------------------------------------------------------
# MLflow configuration
# ---------------------------------------------------------

MLFLOW_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://127.0.0.1:5000",
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

MODEL_URI = "models:/food11@champion"


# ---------------------------------------------------------
# Load the model once when the application starts
# ---------------------------------------------------------

print(f"MLflow tracking URI: {MLFLOW_TRACKING_URI}")
print(f"Loading model: {MODEL_URI}")

model = mlflow.pyfunc.load_model(MODEL_URI)

print("Model loaded successfully.")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Food-11 Classification API",
    description="Classify food images using the Food-11 ResNet18 model.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Food-11 classes
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Image preprocessing
# Must match preprocessing used during training
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------
# Prediction endpoint
# ---------------------------------------------------------

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
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

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read image: {error}",
        )

    # Preprocess image
    image_tensor = transform(image)

    # Add batch dimension:
    # [3, 128, 128] -> [1, 3, 128, 128]
    input_batch = image_tensor.unsqueeze(0)

    # MLflow pyfunc accepts numpy input
    model_input = input_batch.numpy()

    try:
        predictions = model.predict(model_input)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Model prediction failed: {error}",
        )

    # Convert model output back to a tensor
    logits = torch.as_tensor(predictions)

    # Convert logits to probabilities
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