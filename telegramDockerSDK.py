import logging
import os
import signal
import time
import psutil
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes
import docker
import requests
import subprocess
import tempfile
from urllib.parse import urlparse
from git import Repo, GitCommandError

# import shutil

# Initialize Docker client with connection pooling
client = docker.DockerClient(base_url='unix://var/run/docker.sock', max_pool_size=10)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Get CONTAINERS_TO_SKIP from environment variable
containers_to_skip_str = os.getenv('CONTAINERS_TO_SKIP')
CONTAINERS_TO_SKIP = [container.strip() for container in containers_to_skip_str.split(',')]

def rate_limit_decorator(func):
    last_request = {}
    
    async def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        current_time = time.time()
        
        if user_id in last_request and current_time - last_request[user_id] < 1:
            await update.message.reply_text("Please wait before sending another command.")
            return
        
        last_request[user_id] = current_time
        return await func(update, context)
    
    return wrapper

@rate_limit_decorator
async def help_command(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""Use following commands
    /help    - to get help
    /list    - to get list of containers
    /start   - to start a container
    /logs   - to get a container logs
    /stop    - to stop a containers
    /compose - to start containers from github repo with branch
    /del     - to delete a container
    """)

@rate_limit_decorator
async def getlist(update: Update, context: CallbackContext):
    """Send a message when the command /list is issued."""
    container_names = [container.name for container in client.containers.list() if container.name not in CONTAINERS_TO_SKIP]
    if container_names:
        for name in container_names:
            await update.message.reply_text(name)
    else:
        await update.message.reply_text("No containers available.")

@rate_limit_decorator
async def stop(update: Update, context: CallbackContext):
    """Send a message when the command /stop <container_name> or /stop all is issued."""
    if context.args:
        container_name = context.args[0]
        if len(container_name) < 3:
            await update.message.reply_text("Container name must be at least 5 characters long.")
            return
        if container_name == "all":
            stopped_containers = []
            for container in client.containers.list():
                if container.name not in CONTAINERS_TO_SKIP:
                    try:
                        container.stop(timeout=10)
                        stopped_containers.append(container.name)
                    except docker.errors.APIError as e:
                        logger.error(f"Error stopping container {container.name}: {e}")
            if stopped_containers:
                await update.message.reply_text("Stopped containers:-\n" + "\n".join(stopped_containers))
            else:
                await update.message.reply_text("No applicable containers to stop.")
        else:
            if container_name not in CONTAINERS_TO_SKIP:
                try:
                    container = client.containers.get(container_name)
                    container.stop(timeout=10)
                    await update.message.reply_text(f"Container '{container_name}' has been stopped.")
                except docker.errors.NotFound:
                    await update.message.reply_text(f"Container '{container_name}' not found.")
                except docker.errors.APIError as e:
                    logger.error(f"Error stopping container {container_name}: {e}")
                    await update.message.reply_text(f"Failed to stop container '{container_name}': {e}")
            else:
                await update.message.reply_text(f"Container '{container_name}' is in the skip list.")
    else:
        await update.message.reply_text("Please provide a container name to stop or use 'all' to stop all containers.")

@rate_limit_decorator
async def start(update: Update, context: CallbackContext):
    """Send a message when the command /start <container_name> is issued."""
    if context.args:
        container_name = context.args[0]
        if container_name not in CONTAINERS_TO_SKIP:
            try:
                container = client.containers.get(container_name)
                container.start()
                await update.message.reply_text(f"Container '{container_name}' has been started.")
            except docker.errors.NotFound:
                await update.message.reply_text(f"Container '{container_name}' not found.")
            except docker.errors.APIError as e:
                logger.error(f"Error stopping container {container_name}: {e}")
                await update.message.reply_text(f"Failed to start container '{container_name}': {e}")
        else:
            await update.message.reply_text(f"Container '{container_name}' is in the skip list.")
    else:
        await update.message.reply_text("Please provide a container name to start.")

@rate_limit_decorator
async def get_logs(update: Update, context: CallbackContext):
    """Send the logs of a specific container when the command /logs <container_name> -n <number_of_lines> is issued."""
    if context.args:
        try:
            container_name = context.args[0]
            num_lines = 10  # Default number of lines
            if len(container_name) < 5:
                await update.message.reply_text("Container name must be at least 5 characters long.")
                return

            if "-n" in context.args:
                n_index = context.args.index("-n")
                if n_index + 1 < len(context.args):
                    try:
                        num_lines = int(context.args[n_index + 1])
                    except ValueError:
                        await update.message.reply_text("Invalid number of lines. Using default of 10 lines.")

            if container_name not in CONTAINERS_TO_SKIP:
                container = client.containers.get(container_name)
                logs = container.logs(tail=num_lines).decode('utf-8')
                formatted_logs = '\n\t\t\t\t#---Next Line---#\n'.join(logs.splitlines())
                await update.message.reply_text(formatted_logs)
            else:
                await update.message.reply_text(f"Container '{container_name}' is in the skip list.")
        except docker.errors.NotFound:
            await update.message.reply_text(f"Container '{container_name}' not found.")
        except docker.errors.APIError as e:
            logger.error(f"Error getting logs for container {container_name}: {e}")
            await update.message.reply_text(f"Failed to get logs for container '{container_name}': {e}")
    else:
        await update.message.reply_text("Please provide a container name to get logs. Use /logs <container_name> -n <number_of_lines>.")

@rate_limit_decorator
async def delete_container(update: Update, context: CallbackContext):
    """Send a message when the command /del <container_name> is issued."""
    if context.args:
        container_name = context.args[0]
        if len(container_name) < 5:
            await update.message.reply_text("Container name must be at least 5 characters long.")
            return

        if container_name not in CONTAINERS_TO_SKIP:
            try:
                container = client.containers.get(container_name)
                container.remove(v=True, force=True)
                await update.message.reply_text(f"Container '{container_name}' has been deleted.")
            except docker.errors.NotFound:
                await update.message.reply_text(f"Container '{container_name}' not found.")
            except docker.errors.APIError as e:
                logger.error(f"Error deleting container {container_name}: {e}")
                await update.message.reply_text(f"Failed to delete container '{container_name}': {e}")
        else:
            await update.message.reply_text(f"Container '{container_name}' is in the skip list.")
    else:
        await update.message.reply_text("Please provide a container name to delete.")

@rate_limit_decorator
async def run_compose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run a docker-compose.yaml file from a GitHub URL."""
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /compose <github_url> <branch>")
        return

    github_url = context.args[0]
    branch = context.args[1]
    
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(dir='/tmp')
        
        # Extract the repo name from the URL
        repo_name = os.path.splitext(os.path.basename(urlparse(github_url).path))[0]
        print(f"repo_name:-", repo_name)

        # Clone the specific branch of the repository into the temporary directory
        Repo.clone_from(github_url, temp_dir, branch=branch)

        # Construct the path to the docker-compose.yaml file
        compose_file_path = os.path.join(temp_dir, "docker-compose.yml")

        # Check if the docker-compose.yaml file exists
        if not os.path.exists(compose_file_path):
            await update.message.reply_text(f"No docker-compose.yml file found in the branch '{branch}'.")
            return

        # Run docker-compose in the temporary directory
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            cwd=temp_dir,  # Change directory to the temporary directory
            check=True,
            text=True,  # Capture stdout and stderr as text
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        await update.message.reply_text(f"Docker Compose from '{github_url}' branch '{branch}' is running.\nOutput:\n{result.stdout}")
        
        # Cleanup the temporary directory
        # shutil.rmtree(temp_dir)
        
    except GitCommandError as e:
        logger.error(f"Git command error: {e}")
        await update.message.reply_text(f"Failed to clone the repository: {e}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running docker-compose up: {e}\n{e.stderr}")
        await update.message.reply_text(f"Failed to run docker-compose up: {e.stderr}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text(f"An unexpected error occurred: {e}")

@rate_limit_decorator
async def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def error_handler(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")
    await update.message.reply_text("An error occurred. Please try again later.")

def check_memory():
    """Monitor memory usage"""
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        logger.warning("Memory usage is high: %s%%", memory.percent)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("Received shutdown signal, exiting...")
    application.stop()

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("No token provided. Set the TELEGRAM_BOT_TOKEN environment variable.")

    global application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", getlist))
    # application.add_handler(CommandHandler("run", run))
    application.add_handler(CommandHandler("logs", get_logs))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("del", delete_container))
    application.add_handler(CommandHandler("compose", run_compose))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the Bot
    application.run_polling()

    # Periodically check memory
    while True:
        check_memory()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    main()