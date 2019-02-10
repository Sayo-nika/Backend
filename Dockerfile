FROM python:3.7
RUN mkdir -p /app
WORKDIR /app
COPY . .
RUN pip install --user -r requirements.txt
EXPOSE 4444
ENV PYTHONPATH="$PYTHONPATH:/app"
CMD ["python", "main.py"]
