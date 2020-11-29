FROM python:3.8-slim

ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

EXPOSE 80

# Install production dependencies.
RUN pip install -r requirements.txt

CMD [ "gunicorn", "-b 0.0.0.0:8080", "index:server"]