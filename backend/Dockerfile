FROM python:3.12-slim

WORKDIR /app

ARG DEPLOYENV=build

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies with UV
RUN uv pip install --system -r pyproject.toml --no-cache

COPY app .
RUN python manage.py collectstatic --noinput

EXPOSE 8000

ENTRYPOINT ["sh", "./start.sh"]