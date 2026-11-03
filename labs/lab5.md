# Lab 5 - CI/CD with GitHub Actions

## Question 1

It is a bad idea for a unit test to load the real model because the test would
depend on external services.

For example, the test could fail if the MLflow server is offline or if there is
a network problem, even if the code is correct.

It could also fail if the model or the `champion` alias is missing or changed.

Using a fake model makes the unit test faster and lets us test only our code.