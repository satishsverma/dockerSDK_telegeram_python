import logging
import tokenkey
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import docker

client = docker.from_env()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""Use following commands
    /start - to get commands
    /getlist - to get list of containers
    /run - to run the containers
    /stop - to stop all containers
    """)

def getlist(update, context):
    """Send a message when the command /getlist is issued."""
    for container in client.containers.list():
        update.message.reply_text(container.name)

def run(update, context):
    """Send a message when the command /getlist is issued."""
    update.message.reply_text(client.containers.run("alpine", ["echo", "hello", "world"]))

def stop(update, context):
    """Send a message when the command /getlist is issued."""
    for container in client.containers.list():
        container.stop()
    update.message.reply_text("All Containers are stopped")

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    updater = Updater(tokenkey.BotToken, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("getlist", getlist))
    dp.add_handler(CommandHandler("run", run))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("help", help))


    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()