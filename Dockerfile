# pull official base image
FROM python:3.11.2-slim-buster

# install necessary packages (tkinter)
RUN apt-get update \
    && apt-get install -y tk \
    && rm -rf /var/lib/apt/lists/*

# install PortAudio
RUN apt-get update \
    && apt-get install -y portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.in .
RUN pip install --no-cache-dir -r requirements.in

# copy project
COPY . .

# run whisper_clip.pyw
CMD ["python", "speech_to_clipboard_cli.py"]