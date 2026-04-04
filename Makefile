install:
	uv pip compile \
		requirements.in -o requirements.txt --upgrade && \
	uv pip install \
		--extra-index-url https://download.pytorch.org/whl/cpu \
		-r requirements.txt

test:
	pytest -v

build:
	docker build -t baolongnguyenmac/chatbot_video_rag:v1 .

run:
	export PYTHONPATH='./src' && \
	python -m chat_rag
