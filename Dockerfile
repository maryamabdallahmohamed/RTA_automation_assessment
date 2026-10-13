
FROM python:3.13

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync 

COPY . .


EXPOSE 7860

CMD ["uv", "run", "--frozen", "--no-sync", "python", "app.py"]