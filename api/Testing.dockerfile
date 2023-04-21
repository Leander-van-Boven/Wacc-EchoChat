FROM leandervboven/echochat:api

WORKDIR /api

# Update installed pip packages with required packages for testing
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY ./tests ./tests

CMD ["python3", "-m", "app.main"]
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
