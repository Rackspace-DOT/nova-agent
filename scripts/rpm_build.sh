#!/bin/bash
set -euxo pipefail

if [ ! -f /.dockerenv ]; then
    error_and_exit "This should be run inside docker"
fi

if [ $# -ne 1 ]; then
  echo "syntax:  $0 <git_tag_id>"
  exit 1
fi

yum install -y git rpm-build python3-devel

rm -Rf /source/rpmbuild/
mkdir -p /source/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
cd /source

git archive --format=tgz --prefix nova-agent-$1/ -o /source/rpmbuild/SOURCES/nova-agent.tar.gz $1
rpmbuild --define "_topdir /source/rpmbuild" --define "version $1" -bb /source/scripts/nova-agent.spec
