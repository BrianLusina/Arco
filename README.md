# Arco Project

This is a containerized application with the server having a contained flask application, client running a ReactJS application with a PostgreSQL data backend and redis client to manage sessions in the server.

Each container can be build separately and all are put together with `docker-compose`

### Requirements

There are a couple of things you need to have before hand as you set up this project:

1. __Node and npm__
   
   Required for client side code. Especially when setting up the project and installing dependenices.
   
   Install npm and node
   
    ```bash
    curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
    sudo apt-get install -y nodejs npm
    ```
    > Installs Node 7.x
   
   Install application dependencies
   
   ```bash
   cd client
   npm install
   # if using yarn
   yarn install
   ```
   
   
2. __Python and Pip__
   
   The server runs a flask application and will require you to have virtualenv installed as well as pip
    ```bash
    sudo apt-get install -y python-pip
    sudo pip install virtualenv
    cd server
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
    
> sets up and installs pip and virtualenv, then installs the application requirements 

3. __Docker and docker-compose__

This is essential for running this containerized application. Docker compose will ensure that each container is build and run concurrently.
 
 Each application contains a Dockerfile and at the root of the project, there is a `docker-compose.yml` file with instructions on how to build this application.
 
 Installing docker and docker compose
 ```bash
 sudo apt-get install -y --no-install-recommends linux-image-extra-$(uname -r) linux-image-extra-virtual

# Install packages to allow apt to use a repository over HTTPS:
sudo apt-get install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common

# add dockers official GPG key
curl -fsSL https://apt.dockerproject.org/gpg | sudo apt-key add -

# add stable repo
sudo add-apt-repository "deb https://apt.dockerproject.org/repo/ ubuntu-$(lsb_release -cs) main"

# install docker
sudo apt-get update
sudo apt-get -y install docker docker-engine

sudo usermod -aG docker $(whoami)

# Installing docker compose
sudo -i
curl -L https://github.com/docker/compose/releases/download/1.12.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
 ```
 > This will set up docker and docker-compose

### Running the application

