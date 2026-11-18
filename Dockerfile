FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pytest httpx
COPY . .

FROM base AS trained
ARG GIT_COMMIT=local
ENV GIT_COMMIT=${GIT_COMMIT}
RUN python train.py

FROM trained AS tested
RUN python -m pytest -q tests

FROM base AS final
COPY --from=tested /app/artifacts ./artifacts
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
