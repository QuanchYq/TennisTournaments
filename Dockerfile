FROM python:3.8.8
WORKDIR /app

COPY requirements.txt /app/requirements.txt
COPY keyboards.py /app/keyboards.py
COPY libs.py /app/libs.py
COPY users.db /app/users.db
COPY events.db /app/events.db
COPY test.py /app/test.py
COPY alert.py /app/alert.py
COPY ttournamentsbot.py /app/ttournamentsbot.py
# Install the dependencies
RUN pip install -r requirements.txt

# Запускаем cron в фоновом режиме и отслеживаем логи
CMD python ttournamentsbot.py & python alert.py




