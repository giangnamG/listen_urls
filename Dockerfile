FROM python:3.11.5

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install flask 
RUN mkdir uploads

EXPOSE 5000

CMD ["python", "app.py"]

# docker build -t listen_query .
# docker run --name=listen_query -d -p 5000:5000 listen_query