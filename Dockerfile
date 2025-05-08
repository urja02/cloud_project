FROM python:3-alpine3.15
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_ENV=production

# Command to run the Flask app
CMD ["python", "user.py"]