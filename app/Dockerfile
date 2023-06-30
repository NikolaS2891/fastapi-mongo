FROM python:3.10.1

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/myuser/.local/bin:${PATH}"

WORKDIR /app

RUN useradd -m myuser
USER myuser

COPY --chown=myuser:myuser requirements.txt requirements.txt

RUN python3 -m pip install --user --upgrade pip
RUN python3 -m pip install --user --upgrade pip
RUN pip3 install --user -r requirements.txt

COPY --chown=myuser:myuser . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]