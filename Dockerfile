FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system bot && adduser --system --ingroup bot bot
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY --chown=bot:bot . .
USER bot
CMD ["python", "-m", "app.main"]

