# Stage 1: Base image với Python
FROM python:3.11-slim as base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && \
	apt-get install -y nano ffmpeg libsm6 libxext6 && \
		rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies
FROM base as dependencies

COPY requirements.in /app

RUN uv pip compile requirements.in -o requirements.txt && \
    uv pip install \
		--extra-index-url https://download.pytorch.org/whl/cpu \
		--no-cache-dir --upgrade \
		--system \
		-r requirements.txt

# Stage 3: Production
FROM dependencies as production

COPY . /app

EXPOSE 7860

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# ENV HOME=/home/user \
# 	PATH=/home/user/.local/bin:$PATH

CMD python -m chat_rag
