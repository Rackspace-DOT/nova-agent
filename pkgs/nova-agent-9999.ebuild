# Copyright 1999-2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

EAPI=5
PYTHON_COMPAT=( python2_7 python3_3 python3_4 )

inherit distutils-r1 git-2

DESCRIPTION="Agent for reading xenstore"
HOMEPAGE="https://github.com/gtmanfred/nova-agent"
EGIT_REPO_URI="https://github.com/gtmanfred/${PN}.git"
EGIT_BRANCH="master"
S="${WORKDIR}/${PN}-master/"

LICENSE="Apache-2.0"
SLOT="0"
KEYWORDS="~amd64 ~x86 ~amd64-linux ~x86-linux"

DEPEND="dev-python/setuptools[${PYTHON_USEDEP}]"
RDEPEND="dev-python/pycrypto[${PYTHON_USEDEP}]
	app-emulation/xen-tools"

python_install_all() {
	distutils-r1_python_install_all
	newinitd etc/nova-agent.gentoo nova-agent
}

pkg_postinst() {
	elog "If you would like to utilize openstack-guest-agents-unix, add 'nova-agent' to"
	elog "your 'default' runlevel:"
	elog "  rc-update add nova-agent default"
}
