# Docker SDK Telegram Bot

This project implements a Telegram bot that interacts with Docker containers using the Docker SDK for Python. The bot allows users to start specific containers, list containers, run containers, get container logs, and stop containers through Telegram commands.

## Features

- Start a specific Docker container
- List all Docker containers
- Logs a specific Docker container
- Stop a specific Docker container
- Stop all Docker containers
- Rate limiting to prevent command spam
- Error handling and logging
- Memory usage monitoring

## Overview

Containerization has revolutionized software deployment and management, and in this tutorial, we demonstrate how to leverage the Telegram Python module and the Docker SDK to control Docker containers programmatically. By integrating the Telegram platform with Docker, you can automate container operations, monitor containers, and interact with them using a chatbot interface.
Contents

The repository includes the following files:

    1. Python script demonstrating the integration of the Telegram Python module and Docker SDK to control Docker containers. This script provides examples of retrieving container lists, stopping all containers.
    2. README.md: This README file providing an overview of the repository and the video tutorial.

# Getting Started
To get started with the code examples in this repository, follow these steps:

## Prerequisites

- Docker
- Docker Compose

## Installation

1. Clone the repository:
Clone this repository to your local machine or download the code as a ZIP file.

```bash
cd dockerSDK_telegeram_python
```

## Set up environment variables.
2. Rename `.env-example` to `.env`

```bash
mv .env-example .env
```

3. And set up environment variables:

    `TELEGRAM_BOT_TOKEN`= "Your Telegram Bot Token"
    
    `CONTAINERS_TO_SKIP`= "Comma-separated list of container names to skip (optional)"


Note:- `CONTAINERS_TO_SKIP`: This environment variable can be set to a comma-separated list of container names that should not be affected by the bot's commands.

## Docker Support

To run this bot in a Docker container:

1. Build the Docker image:
```bash
docker compose build 
```
2. Run the Docker container:
```bash
docker compose up
```

3. In Telegram, you can use the following commands:
- `/help`: Get help and list of commands.
- `/list`: Get a list of all containers.
- `/start CONTAINER_NAME`: Start a specific container.
- `/logs CONTAINER_NAME -n 10` : Get container logs default 10 lines.
- `/stop CONTAINER_NAME`: Container name to stop or use 'all' to stop all containers.
- `/compose` - Start containers from github repo with branch.
- `/del CONTAINER_NAME`: Delete a container.

Note: Mounting `/var/run/docker.sock` allows the bot to interact with the Docker daemon on the host.

## Security Considerations

- Ensure that only authorized users have access to your Telegram bot.
- Be cautious about which containers you allow the bot to control, especially in production environments.
- Regularly review and update the `CONTAINERS_TO_SKIP` list to prevent unintended actions on critical containers.

## Applications

The integration of the Telegram Python module and Docker SDK opens up various applications, including:

Remote container management: Control Docker containers from anywhere by sending commands via the Telegram chatbot.
Automation of container operations: Build scripts or bots that automatically start, stop, or restart containers based on specific events or triggers.
Deployment orchestration: Initiate deployments, spin up new containers, and manage container clusters through Telegram messages.
Monitoring and notifications: Receive real-time updates on container status, resource usage, and error alerts via Telegram, enabling prompt response to issues.
Interactive container management: Provide a user-friendly interface for users to interact with Docker containers through a Telegram chatbot.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
