FROM weboftrust/keri:1.2.3

WORKDIR /usr/local/var

RUN mkdir -p /usr/local/var/webs
COPY . /usr/local/var/webs

WORKDIR /usr/local/var/webs

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /usr/local/var/webs/volume/dkr/examples