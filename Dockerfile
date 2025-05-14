# Base image
FROM python:3.11

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Django project code
COPY .. /app

# Collect statisc of project
#RUN python manage.py collectstatic

# Expose port 8000
EXPOSE 8080

# Start Gunicorn
CMD ["gunicorn", "systemreporting.wsgi:application", "--bind", "0.0.0.0:8080"]