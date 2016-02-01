PORTNAME=       nova-agent
PORTVERSION=    0.2.0
MASTER_SITES=   GITHUB
CATEGORIES=     misc python
DISTNAME=       nova-agent-master
DISTFILES=      master.tar.gz
PKGNAMEPREFIX=  ${PYTHON_PKGNAMEPREFIX}

RUN_DEPENDS=    ${PYTHON_PKGNAMEPREFIX}netifaces>0:${PORTSDIR}/net/py-netifaces \
                ${PYTHON_PKGNAMEPREFIX}pycrypto>0:${PORTSDIR}/security/py-pycrypto

GH_ACCOUNT=     gtmanfred
GH_PROJECT=     nova-agent
GH_TAGNAME=     fa9f9ae332a97c6bd3aca03bdec08ddf72b89ea1

FETCH_ARGS=    -pRr

MAINTAINER=    danielwallace@gtmanfred.com
COMMENT=       Agent for reading xenstore

LICENSE=       APACHE20


USES=          python:2
USE_PYTHON=    distutils autoplist
USE_RC_SUBR=   nova-agent

.include <bsd.port.mk>
