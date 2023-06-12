
# Use the official Python base image
FROM python:3.10


# Set the working directory to C:\Users\Afitha\internpro\userinfo
WORKDIR C:\Users\Afitha\internpro\userinfo

ADD . .

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
COPY . /app

CMD [ "python3","manage.py","runserver","0.0.0.0.8000" ]





# Use the official Python base image
FROM python:3.8

# Set the working directory to /home/ameen/kafka-Storm/Kafka_Storm
WORKDIR /home/ameen/kafka-Storm/Kafka_Storm

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    leiningen \
    git \
    wget \
    python-is-python3
    
    
# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/kafka_storm"
ENV PATH="/opt/storm/bin:${PATH}"
ENV LEIN_ROOT=true

# Install Streamparse
RUN pip install streamparse
RUN pip install hdfs
RUN pip3 install confluent-kafka
RUN pip3 install faker
RUN pip3 install git+https://github.com/dpkp/kafka-python.git


# Install Storm 1.2.3
COPY ../apache/apache-storm-1.2.3 /opt/storm

# Copy your existing Streamparse directory into the Docker image
COPY ../kafka-Storm/Kafka_Storm /kafka_storm

# Change the working directory to /kafka_storm
WORKDIR /kafka_storm

# Set the entrypoint command to run your Streamparse topology
CMD ["sparse", "run", "--name", "first_topology"]