FROM python:3.9-slim
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "src/api.py"]
