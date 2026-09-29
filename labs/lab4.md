# Lab 4 - Orchestrating the App with Docker Compose

## Question 1

Without a volume, the MLflow database and artifacts are stored only inside
the container.

After I stopped and removed the first container and started a new one from the
same image, the MLflow UI was fresh again and the previous data was gone.

This happens because removing the container also removes the data stored in its
own writable filesystem.

## Question 2

A named volume is useful because Docker manages the storage for us and keeps
the MLflow database and artifacts even if the container is removed.

A bind mount would also work, but it would store the files in a specific folder
on my computer.

For this lab, a named volume is cleaner because the data belongs to the Docker
stack and does not need to be edited directly from the host.

## Question 3

In Lab 3, the inference container had to reach MLflow running on my Windows
host, so I used `host.docker.internal`.

With Docker Compose, the containers are on the same private network.
Docker Compose provides DNS between services, so the inference container can
reach the MLflow container using the service name:

`http://mlflow:5000`

## Question 4

The frontend reads `INFERENCE_URL` from an environment variable so the same
image can work in different environments.

Inside Docker Compose, it can use:

`http://inference:8000`

But if I run the frontend by itself, I can give it another URL such as:

`http://127.0.0.1:8000`

without changing the code.

## Question 5

The inference service does not need to publish port 8000 because I do not
access it directly from my computer.

The frontend and inference containers are on the same Docker Compose network,
so the frontend can reach the API using:

`http://inference:8000`

Only the services that I need to open from the host, which are MLflow and the
frontend, need published ports.

## Question 6

`depends_on` only makes Docker start the MLflow container before the inference
container. It does not guarantee that MLflow is fully ready.

If the inference service tries to load the model before MLflow is ready, the
model loading fails during startup and the inference container exits.

In my run, the inference container also stopped because the new MLflow
instance did not contain the `food11` registered model yet.

## Question 7

After running `docker compose ps`, MLflow and the frontend had published ports.

MLflow uses port `5000` and the frontend uses port `8501`.

The inference service only showed `8000/tcp` because it is not published to
the host. The frontend reaches it directly through the Docker Compose network.

This matches the configuration in `docker-compose.yml`.

## Question 8

After moving the `champion` alias to the new model version, the running
inference service still used the old model.

This is because `serve.py` loads the model only once when the application
starts.

To load the new model version, I used:

`docker compose restart inference`

After moving the `champion` alias to version 2, the running inference service
would still use the model that it loaded when it started.

I restarted only the inference service with:

`docker compose restart inference`

After the restart, the service loads the model again and resolves the
`champion` alias to the new version.

In my test, version 2 used the same model artifact as version 1, so the
prediction itself did not visibly change.

## Question 9

A restart is enough because the model itself is not baked into the inference
Docker image.

The image contains the API code and its dependencies. When the container
starts, it connects to MLflow and loads the model referenced by the
`champion` alias.

Because of this, I can change the model in MLflow and restart the inference
container without rebuilding the Docker image.

A restart is enough because the trained model is not stored inside the
inference Docker image.

The image contains the API code and dependencies. The model is downloaded from
MLflow when the container starts.

This means I can change the model behind the `champion` alias and restart the
inference container without rebuilding the image.   

## Question 10

After running `docker compose down` and then `docker compose up`, the registered
model and the `champion` alias were still there.

This is because the named volume was kept even though the containers were
removed.

When I ran `docker compose down -v`, Docker also removed the named volume.

After starting the stack again, MLflow was empty and the registered model was
gone because its database and artifacts had been stored in that volume.


## Question 11

Docker Compose is mainly designed to run services on one machine.

If I wanted to run several replicas of the inference service behind a load
balancer, I would need an orchestration platform such as Kubernetes or Docker
Swarm.

For MLflow to survive the failure of one machine, I would also need persistent
storage and a database that are available outside a single host.

Docker Compose does not provide automatic multi-machine scheduling,
load balancing, failover, or high availability.