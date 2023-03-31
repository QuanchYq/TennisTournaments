FROM python:3.8.8
WORKDIR /app


COPY cronjob /app/cronjob
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
RUN apt-get update && apt-get install -y cron && \
    cat cronjob | crontab - && \
    touch /var/log/cron.log
    

# Запускаем cron в фоновом режиме и отслеживаем логи
CMD ["sh", "-c", "python ttournamentsbot.py & cron -f"



