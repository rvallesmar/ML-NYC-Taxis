FROM python:3.8.13 as base

ENV PYTHONPATH=$PYTHONPATH:/src/

# Copy requirements first for better caching
COPY requirements.txt .

# Install requirements but exclude xgboost
RUN pip3 install $(grep -v "xgboost" requirements.txt)

# Install xgboost 1.6.1
RUN pip3 install xgboost==1.6.1

COPY ./ /src/

WORKDIR /src

FROM base as test
RUN ["pytest", "-v", "/src/tests"]

FROM base as build
ENTRYPOINT ["python3", "/src/ml_service.py"] 