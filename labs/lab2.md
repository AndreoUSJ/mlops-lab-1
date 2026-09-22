# Lab 2 - Model Training and Experiment Tracking with MLflow

## Question 2

`--backend-store-uri` tells MLflow where to store run metadata such as
parameters, metrics, experiment information, and run information.

In this lab, the metadata is stored in a local SQLite database:

`sqlite:///mlflow.db`

`--default-artifact-root` tells MLflow where to store artifacts generated
by runs, such as trained models and other output files.

In this lab, artifacts are stored in:

`./mlruns`

The difference is that metadata describes the experiment and its results,
while artifacts are the actual files produced by a run.

## Question 3

`mlflow.db` and `mlruns/` should not be tracked by Git because they are
local outputs generated while running MLflow rather than source code.

- `mlflow.db` contains local experiment metadata such as runs, parameters,
  metrics, and experiment information.
- `mlruns/` contains artifacts produced by the experiments, such as saved
  models.

They should not be tracked by DVC either because they are experiment-tracking
outputs that are already managed by MLflow. DVC is used to version datasets
and other data dependencies, while MLflow is responsible for experiment
metadata, metrics, and artifacts.

## Question 4

When `mlflow.set_experiment("food11")` is called for the first time and an
experiment with that name does not already exist, MLflow automatically creates
the new experiment.

Subsequent runs that use the same experiment name will be recorded under the
existing `food11` experiment.

## Question 5

`mlflow.log_param()` is used to log a parameter whose value is normally fixed
for the whole run, such as the learning rate, batch size, number of epochs, or
dataset.

`mlflow.log_metric()` is used to log numerical values produced during training,
such as training loss, validation loss, or validation accuracy.

`log_metric()` accepts a `step` argument because a metric can change over time.
For example, validation accuracy can have a different value at every epoch.
The step tells MLflow which epoch or training step each metric value belongs to.

A parameter does not need a step because it is generally defined once for the
entire run and does not evolve during training.

## Question 6

The MLflow run contains the hyperparameters, including the dataset,
number of epochs, learning rate and batch size, as well as the logged
training and validation metrics.

The metric charts show how values such as `train_loss`, `val_loss`
and `val_accuracy` evolve during training.

The trained ResNet18 model is also logged as an MLflow model artifact.

Because the MLflow server was started with:

`--default-artifact-root ./mlruns`

Therefore, the model files are stored somewhere inside:

`C:\Users\User\Desktop\MLops\mlops-lab-1\mlruns`

MLflow stores metadata about the run in `mlflow.db`, while the actual model
artifact files are stored in the `mlruns` directory.

## Question 7

Among the experiments, the learning rate `0.0001` gave the highest final
validation accuracy.

The results were:

- `lr = 0.01` → `val_accuracy = 0.1816`
- `lr = 0.001` → `val_accuracy = 0.5794`
- `lr = 0.0001` → `val_accuracy = 0.7172`

A higher learning rate is therefore not always better. In these experiments,
the largest learning rate (`0.01`) produced the lowest validation accuracy.
A learning rate that is too high can cause the optimization process to make
updates that are too large and prevent the model from converging effectively.
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)

## Question 8

The parallel coordinates plot shows that the learning rate has a strong
relationship with validation accuracy.

The highest learning rate, `0.01`, produced the lowest validation accuracy,
while the smaller learning rate `0.0001` produced the highest validation
accuracy in these runs.

For `lr = 0.001`, increasing the batch size from 32 to 64 increased the final
validation accuracy from approximately `0.5794` to `0.6104`.

Therefore, both learning rate and batch size affect the result, but in these
experiments the learning rate had the clearest effect. These results are based
on individual training runs, so repeated runs could vary because training is
stochastic.

## Question 9

After sorting the runs by `val_accuracy` in descending order, the run with the
highest final validation accuracy was:

- Run name: `nervous-sloth-246`
- Run ID: `9b69b9bb64664adbb94847cfeea368f3`
- Learning rate: `0.0001`
- Batch size: `32`
- Validation accuracy: approximately `0.7172`
- Test accuracy: approximately `0.7454`