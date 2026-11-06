# Lab 5 - CI/CD with GitHub Actions

## Question 1

It is a bad idea for a unit test to load the real model because the test would
depend on external services.

For example, the test could fail if the MLflow server is offline or if there is
a network problem, even if the code is correct.

It could also fail if the model or the `champion` alias is missing or changed.

Using a fake model makes the unit test faster and lets us test only our code.

## Question 2

The test proves that the API can receive an image, preprocess it, call a model
and return a valid JSON response with a category and confidence.

It also checks that the prediction is correctly converted to the class
`Bread`.

It does not prove that the real trained model is accurate or that MLflow is
working, because the test uses a fake model with a fixed output.

## Question 3

The duplicate-image check caught the copied image because the same file content
appeared in two different splits.

A duplicate between training and testing is dangerous because it creates data
leakage. The model may see the same image during training and evaluation, which
can make the test accuracy look better than it really is.

A corrupted image is easier to notice because it usually causes an error or
crash. A duplicate can stay hidden while giving misleading evaluation results.

The validator also found that the existing mini dataset already contained some
duplicates across its splits.

## Question 4

The validation should run after the dataset is downloaded or restored from DVC
and before training starts.

One option is to run it in the training pipeline immediately after `dvc pull`.

Another option is to run it on a self-hosted CI runner that already has access
to the dataset or to the DVC remote.

This way the data contract can still protect the training process even if the
normal GitHub cloud runner cannot access the dataset.

## Question 5

Because `smoke` has `needs: test`, the smoke job only runs if the test job
succeeds.

If a unit test fails, the smoke job is skipped.

Without `needs: test`, GitHub could run both jobs independently, so the Docker
build could still run even when the unit tests are failing.

## Question 6

The first CI run took about 2 minutes 12 seconds.

The second run took about 2 minutes 39 seconds, so the total workflow was
actually a little slower on the second run.

The dependency setup can benefit from the uv cache because packages do not
always need to be downloaded again. However, the total workflow time can still
change because GitHub runners and Docker builds do not always take exactly the
same amount of time.

## Question 7

Using the commit SHA as the Docker image tag makes every image point to one
specific version of the code.

The `latest` tag can change over time. For example, machine A could pull
`latest` in the morning and machine B could pull `latest` after a new image was
published. Both machines would say they are using `latest`, but they could
actually be running different code.

A commit SHA avoids this problem because the tag is fixed and reproducible.

## Question 8

The `push` job declares its permissions explicitly so the `GITHUB_TOKEN` only
gets the access needed by that job.

It needs read access to the repository contents and write access to packages so
it can push the Docker image to GHCR.

If a compromised step had write access to everything, it could potentially
modify repository content, publish or delete packages, or perform other
unauthorized actions using the token.

Using limited permissions reduces the possible damage.

## Question 9

When I intentionally broke the test, the pull request showed a failing `test`
check. The `smoke` and `push` jobs were skipped because they depended on the
previous jobs.

With required status checks enforced, the pull request should not be merged
until the required checks pass. As a repository administrator, GitHub may still
allow bypassing the rule unless bypassing is disabled.

After fixing the code and pushing again, the `test` and `smoke` checks passed
and the pull request was ready to merge.

For a team, this is safer than asking everyone to remember to run tests on
their laptop because the checks are executed automatically and consistently
before code is merged.

## Question 10

The current champion was version 3 with a test accuracy of approximately
`0.7454`.

The test set contained `1096` images.

The value of `2 * SE` was approximately:

`0.0263`

so the promotion threshold was approximately:

`0.7718`

Candidate 1 was version 4. It was trained with a very small learning rate and
had a test accuracy of approximately `0.0721`.

Because `0.0721` was far below the threshold of `0.7718`, the gate kept it as
the `challenger`.

Candidate 2 was version 5 and had a test accuracy of `0.7500`.

Although candidate 2 was slightly better than the champion, it was still below
the required threshold of `0.7718`, so it was also kept as the `challenger`.

This shows that the gate requires a meaningful improvement, not just a very
small increase in accuracy.

## Question 11

One solution is to use a self-hosted GitHub Actions runner on a machine that
can access the MLflow server. The promotion script could then run automatically
after training.

Another solution is to host MLflow on a remote service such as DagsHub. The
GitHub runner could connect to that hosted MLflow server and run the promotion
script automatically after a new model is trained.

## Question 12

The pipeline is:

```text
git push
   |
   v
[Automatic]
GitHub Actions starts
   |
   v
test job
- checkout code
- install dependencies
- Ruff
- pytest
   |
   | only if tests pass
   v
smoke job
- build Docker image
- start container with SKIP_MODEL=1
- check /health
   |
   | only on main
   v
push job
- login to GHCR
- build/push Docker image
- tag image with Git commit SHA
   |
   v
GitHub Container Registry
   |
   | Human / deployment system
   v
pull exact SHA image
   |
   v
running container
```

The code version is decided by the Git commit SHA. The Docker image is also
tagged with this SHA, so the exact source version can be identified.

The model version is independent from the Docker image. Training produces
registered MLflow model versions, and `promote.py` checks their accuracy.

If a candidate passes the quality gate, the `champion` alias is moved to that
model version. If it does not pass, it receives the `challenger` alias instead.

Training and choosing when to run the promotion process still require a human
in the current setup, while the GitHub CI tests, Docker build, smoke test and
image publishing are automatic.