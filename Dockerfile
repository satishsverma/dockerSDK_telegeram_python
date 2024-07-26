# Use an official Python runtime as a parent image
ARG PYTHON_IMAGE
FROM $PYTHON_IMAGE

ENV COMPOSE_VERSION=v2.29.0

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# upgrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# get latest docker compose released tag
RUN apt update \
    && apt install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* 

# Install docker-compose
RUN curl -L https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose

# Run python program when the container launches
CMD ["python", "./telegramDockerSDK.py"]
