# Use the official Python base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Copy the entry.sh script into the container
COPY entry.sh .

# Give executable permissions to the entry.sh script
RUN chmod +x entry.sh

# Expose the desired port for the Django application to run on
EXPOSE 8000

# Start the Django development server using the entry.sh script
CMD ["./entry.sh"]
