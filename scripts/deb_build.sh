#!/bin/bash
set -euxo pipefail
DEBEMAIL="brian.metzler@rackspace.com"
DEBFULLNAME="Brian Metzler"
MAINTAINER="$DEBFULLNAME <$DEBEMAIL>"
export DEBEMAIL DEBFULLNAME MAINTAINER

if [ ! -f /.dockerenv ]; then
    error_and_exit "This should be run inside docker"
fi

if [ $# -ne 1 ]; then
  echo "syntax:  $0 <git_tag_id>"
  exit 1
fi

apt-get update

# Build essentials and Build requirements
apt-get install -y  git \
                    build-essential \
                    dh-make \
                    devscripts \
                    fakeroot \
                    dh-systemd \
                    python3-all \
                    python3-setuptools \
                    vim \
                    python3-pip \
                    rsync \
                    tree

cd /source
python3 -m pip install -e .[tests]

# Build pyz(zipapp) version to $(pwd)/usr/nova-agent.pyz
python3 setup.py pyz --version $1

cp /source/usr/nova-agent.pyz /source/scripts/nova-agent
chmod 755 /source/scripts/nova-agent

cd /source/scripts

# Build debian package
dpkg-buildpackage -us -uc

# Create output dir and copy deb to it
mkdir -p /source/dist/deb/
cd /source
chmod a+rw *.deb
cp *.deb /source/dist/deb/