## A sample third-party authentication service integration with Docker Registry
This repository illustrates how to set up a third-party (token-based) 
authentication service for use with a private Docker registry. The overall
approach is described [here](https://github.com/docker/distribution/blob/master/docs/spec/auth/token.md).

The sample consists of a Docker registry configured (via `docker-compose.yml`) 
to make use of a simple token-based authentication service written in Python
(see `authserver/authserver.py`).


### Acquire certificates

Before starting, both the docker registry and the authentication server need 
a host certificate. 
[These instructions](https://docs.docker.com/registry/insecure/) 
can be used to generate a self-signed certificates for each of them. Place the
files under `certs/` and make sure to set the `CN` (Common Name) appropriately
to your hostname/IP address (for example `myhost.com`).

For example, one for the auth server:

    openssl genrsa -out certs/authserver.key 2048
    openssl req -new -x509 -sha256 -key certs/authserver.key \
      -out certs/authserver.crt -days 365 -subj "/O=Elastisys/OU=Auth/CN=${HOSTNAME}"

... and one for the Docker registry:

    openssl genrsa -out certs/myregistry.key 2048
    openssl req -new -x509 -sha256 -key certs/myregistry.key \
      -out certs/myregistry.crt -days 365 -subj "/O=Elastisys/OU=Registry/CN=${HOSTNAME}"



It may be necessary to explicitly set up the OS to trust the certificates.
On Ubuntu, this means copying `certs/*.crt` to 
`/usr/local/share/ca-certificates/`	and running:

    sudo update-ca-certificates

Restart the docker daemon to make sure it picks up the trusted certs:

    sudo service docker restart


### Start the services

Now everything should be prepared to start the docker registry and the 
authentication server.

Build and start the auth server:

    cd authserver && make venv && . venv.authserver/bin/activate && make init
    ./authserver.py

Start the registry (*make sure the `${HOSTNAME}` environment variable is set):
 
    export HOSTNAME=$(hostname)
    docker-compose up -d && docker-compose logs


### Interact with the docker registry

Log in to the docker registry with one of the authorized users. 
The user credential database (well..) is found under `authserver/users.auth`:	
	
    docker login https://${HOSTNAME}:5000

Push an image from your local machine to the registry:

    docker pull ubuntu:wily
    docker tag ubuntu:wily ${HOSTNAME}:5000/my/ubuntu:1.0.0
	docker push ${HOSTNAME}:5000/my/ubuntu:1.0.0
	
Pull an image:

    docker pull ${HOSTNAME}:5000/my/ubuntu:1.0.0
	
Log out:

    docker logout https://${HOSTNAME}:5000

