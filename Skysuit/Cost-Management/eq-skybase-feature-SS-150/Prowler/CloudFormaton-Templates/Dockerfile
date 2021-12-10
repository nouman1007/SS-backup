FROM amazonlinux:2

ARG USERNAME=prowler
ARG USERID=34000
ARG S32
ARG ROLE2
ARG S3ACCOUNT2
ENV S3=$S32
ENV ROLE=$ROLE2
ENV S3ACCOUNT=$S3ACCOUNT2

RUN echo $S3
# install common tools
RUN yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum update -y
RUN yum install -y sudo bash curl wget git man-db nano vim bash-completion tmux  gcc gcc-c++ make tar

RUN useradd --uid 1000 --shell /bin/bash -m --home-dir /home/ubuntu prowler && \
    sed -i 's/%wheel\s.*/%wheel ALL=NOPASSWD:ALL/' /etc/sudoers && \
    usermod -a -G wheel prowler
RUN yum  install -y  python3 bash curl jq file && \
    pip3 install  --upgrade pip && \
    pip install awscli boto3 detect-secrets && \
    yum install -y git
WORKDIR /prowler

COPY . ./

RUN chown -R prowler .

USER ${USERNAME}

ENTRYPOINT ["./execute.sh"]
