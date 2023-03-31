FROM python:3.8.8
WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron

# Copy the cron job file and the script to execute
COPY cronjob /etc/cron.d/cronjob
COPY trigger_app.sh /app/trigger_app.sh

# Give execution rights on the cron job and the script
RUN chmod 0644 /etc/cron.d/cronjob
RUN chmod +x /app/trigger_app.sh

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
