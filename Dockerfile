FROM python:3.12-slim

# Update packages
RUN apt update

# Install weasyprint, openssh-client and git
RUN apt install weasyprint openssh-client git -y

# Install requirements
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Copy project
WORKDIR /usr/src/
COPY . .

# Make script executable
RUN chmod +x ComCom.py
RUN echo '#!/bin/sh\nexec /usr/src/ComCom.py "$@"' > /usr/local/bin/comcom && chmod +x /usr/local/bin/comcom

# Create app directory
RUN mkdir app
WORKDIR /usr/src/app

# Entrypoint
ENTRYPOINT ["bash", "/usr/src/entrypoint.sh"]