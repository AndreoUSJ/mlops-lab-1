# Lab 3 - Containerizing the Model with Docker

## Question 1

The registered model was given version `1`.

The logged model artifact belongs to one specific MLflow run.

A registered model has a common name, such as `food11`, and can have multiple
versions coming from different runs. This makes it easier to manage models
separately from the experiments that created them.

## Question 2

MLflow now uses aliases such as `champion` and `challenger` instead of the old
stages like `Staging` and `Production`.

Model versions are useful because different runs can produce different models.

An alias is flexible because it can be moved from one version to another.
For example, the application can always load:

`models:/food11@champion`

without knowing the exact version number.

## Question 3

Using:

`models:/food11@champion`

is better than loading a `.pth` file directly because the application does not
need to know where the model file is stored.

MLflow finds the model using the registry and the `champion` alias.

If I want to serve a newer model, I only need to move the `champion` alias to
the new version. I do not need to change the API code.

## Question 4

`pyproject.toml` and `uv.lock` are copied before the source code so Docker can
cache the dependency installation.

If I only change something in `serve.py`, Docker can reuse the dependency layer
instead of installing all the packages again.

This makes rebuilds much faster.

## Question 5

The multi-stage image size was about:

`2.01 GB`

The naive single-stage image size was about:

`2.15 GB`

So the multi-stage build saved around `140 MB`.

Using `docker history`, the biggest layer was the Python virtual environment,
which was around `1.44 GB`.

Most of this size comes from large dependencies such as PyTorch and MLflow.

## Question 6

Without `.dockerignore`, Docker would send many unnecessary files during the
build, which makes the build slower.

Folders such as `data/`, `.venv/`, `mlruns/`, and `.git/` are not needed in the
Docker image.

The `.venv/` folder could also cause problems if it was copied because it was
created on Windows, while the Docker container runs Linux.

The other large folders, especially `data/` and `mlruns/`, would mainly make
the build context much bigger and slower.

## Question 7

The container cannot use `127.0.0.1:5000` to reach MLflow on my computer
because `127.0.0.1` inside the container refers to the container itself.

On Docker Desktop, `host.docker.internal` lets the container reach the host
machine.

So the container uses:

`http://host.docker.internal:5000`

to connect to MLflow.

## Question 8

I stopped the first container and started another container using the same
Docker image.

The API still worked without rebuilding the image.

The application code and dependencies are inside the Docker image, but the
model is loaded from MLflow when the container starts using:

`models:/food11@champion`

This means I can change the model behind the `champion` alias without rebuilding
the Docker image.

## Question 9

The Dockerfile is stored in Git, but the Docker image currently exists only on
my computer.

For another machine or a CI/Kubernetes environment to use the same image, it
should be pushed to a container registry such as Docker Hub or GitHub Container
Registry.

Using a fixed version tag or image digest would also make sure that the exact
same image is used instead of relying only on `latest`.