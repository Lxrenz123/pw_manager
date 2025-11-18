FROM python:3.13


WORKDIR /code

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt


RUN useradd -m appuser

COPY ./app /code/app

COPY ./alembic /code/alembic

COPY ./alembic.ini /code/

RUN chown -R appuser:appuser /code

USER appuser


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]