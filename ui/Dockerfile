FROM python:3.8.13 AS base

ENV PYTHONPATH=/src/

COPY ./requirements.txt /src/requirements.txt

WORKDIR /src

# Install dependencies with explicit altair installation
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install altair==4.2.2

COPY ./ /src/

FROM base AS test
RUN ["python", "-m", "pytest", "-v", "tests"]

FROM base AS build
CMD ["streamlit", "run", "--server.port", "9090", "app/taxi_prediction_app.py"] 