# Copyright 1999-2014 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=5
PYTHON_COMPAT=( python2_7 )

inherit autotools eutils python-single-r1 vcs-snapshot

DESCRIPTION="Openstack Unix Guest Agent"
HOMEPAGE="http://github.com/gtmanfred/nova-agent"
SRC_URI="https://github.com/gtmanfred/${PN}/archive/master.tar.gz -> ${P}.tar.gz"
LICENSE="Apache-2.0"
SLOT="0"
KEYWORDS="~amd64"

CDEPEND="
	dev-python/pycrypto[${PYTHON_USEDEP}]
	${PYTHON_DEPS}
"
DEPEND="
	${CDEPEND}
"
RDEPEND="${CDEPEND}"

pkg_setup() {
	python-single-r1_pkg_setup
}

src_install() {
    esetup.py install --root="${D}"

	doinitd etc/nova-agent.gentoo
}

pkg_postinst() {
	elog "If you would like to utilize openstack-guest-agents-unix, add 'nova-agent' to"
	elog "your 'default' runlevel:"
	elog "  rc-update add nova-agent default"
}
