FROM python:3.8.12-slim-bullseye
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app
RUN mkdir -p /app/logs

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD ["python", "rpi_sub_pub.py"]
