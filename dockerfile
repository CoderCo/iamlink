# Use an official Python runtime as a parent image
FROM python:3.11

# Set up a working directory
WORKDIR /app

# Copy your Django project files into the container
COPY . /app

# Install any dependencies using pip (requirements.txt should be present)
RUN pip install -r requirements.txt

# Expose the port your application will run on
EXPOSE 8000

# Define the command to start your Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]