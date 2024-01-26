FROM minizinc/minizinc:2.7.6

RUN apt-get update \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip git \
    && apt-get install -y dos2unix \
    && git clone https://github.com/pelinsuacar/CDMO_Project src \
    && find . -name '*.sh' -exec dos2unix {} + \
    && find . -name '*.sh' -exec chmod +x {} +


#set working directory for the container
WORKDIR /src

RUN python3 -m pip install -r requirements.txt  

