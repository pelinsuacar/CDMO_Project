FROM minizinc/minizinc:2.7.6

COPY . /src

RUN apt-get update \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip git \
    && apt-get install -y dos2unix 

#set working directory for the container
WORKDIR /src