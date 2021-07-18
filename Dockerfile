# Setup image with chromedriver and all the necessary packages to run this package

FROM python:3.8

WORKDIR /package

# Setup python enviroment
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Update the repositories and Install dependencies
RUN apt-get -yqq update && \
    apt-get -yqq install gnupg2 && \
    apt-get -yqq install curl unzip && \
    apt-get -yqq install xvfb tinywm && \
    apt-get -yqq install fonts-ipafont-gothic xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic && \
    apt-get install -y unzip xvfb libxi6 libgconf-2-4 && \
    apt-get install -y fonts-liberation &&\
    apt-get install -y libasound2-dev &&\
    apt-get install -y libatk-bridge2.0-0 &&\
    apt-get install -y libatk1.0-0&&\
    apt-get install -y libatspi2.0-0 &&\
    apt-get install -y libcups2 &&\
    apt-get install -y libgbm1 &&\
    apt-get install -y libgtk-3-0 &&\
    apt-get install -y libnspr4 &&\
    apt-get install -y libnss3-tools &&\
    apt-get install -y libxcomposite1 &&\
    apt-get install -y libxkbcommon0 &&\
    apt-get install -y libxrandr2 &&\
    apt-get install -y xdg-utils &&\
    apt-get install -y libu2f-udev &&\
    apt-get install -y libvulkan1 &&\
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
ARG CHROMEDRIVER_VERSION="89.0.4389.23"
RUN wget http://170.210.201.179/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_90.0.4430.212-1_amd64.deb
RUN apt install ./google-chrome-stable_90.0.4430.212-1_amd64.deb

# Install Chrome WebDriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Source code copy
COPY . .

# Run tests
CMD [ "python3", "test/tests.py"]