# Lab 3 - Containerizing the Model with Docker

## Question 1

The registered model was assigned version `1`.

A logged model artifact belongs to a specific MLflow run. It is the model
produced by that particular experiment and is tied to that run's parameters,
metrics, and artifacts.

A registered model is managed separately in the MLflow Model Registry. It has
a stable name such as `food11` and can have multiple versions that may come
from different training runs.

This makes it possible to manage model versions independently from the
experiments that produced them.

## Question 2

MLflow replaced the old built-in stages such as `Staging` and `Production`
with model aliases.

Aliases are named pointers such as `champion` or `challenger` that can point
to a specific registered model version.

A model is versioned separately from the run that produced it because several
training runs may produce different candidate models. The Model Registry gives
these models a stable name and independent version numbers.

An alias is more flexible than a fixed stage because it can be reassigned to
another model version without changing the application code. For example, the
application can always load:

`models:/food11@champion`

If a newer model becomes the preferred version, the `champion` alias can simply
be moved to that version.

## Question 3

Loading the model using the MLflow model URI

`models:/food11@champion`

is better than loading a `.pth` file directly because the application does
not need to know the exact physical location or filename of the model.

The `champion` alias points to the registered model version that should
currently be served. MLflow handles locating and loading the corresponding
model artifact.

If a newer model becomes the preferred model, I do not need to modify the
serving code. I only need to register the new model version and move the
`champion` alias to that version.

The API can continue loading:

`models:/food11@champion`

while the alias determines which version is actually served.