# Use an official Python runtime as a parent image
ARG PYTHON_IMAGE
FROM $PYTHON_IMAGE

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Define environment variable
# ENV NAME World

# Run bot.py when the container launches
CMD ["python", "./telegramDockerSDK.py"]
