FROM python:3.10.11

EXPOSE 80

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY src /app/src
COPY routes /app/routes
COPY main.py /app/main.py
COPY models /app/models
WORKDIR /app
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","80"]