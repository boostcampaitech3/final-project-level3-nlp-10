FROM python:3.9.8-slim-buster

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 80
COPY . ./code/app
ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
