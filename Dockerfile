FROM python:3.6
RUN mkdir -p /app
WORKDIR /app
COPY . .
RUN pip install --user -r requirements.txt
EXPOSE 4444
CMD ["python", "main.py"]