%if 0%{?fedora}
%bcond_without python3
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
%bcond_without systemd
%endif

%bcond_without tests

Name: nova-agent
Version: 2.1.0
Release: 1%{?dist}
Summary: Agent for setting up clean servers on Xen
License: ASL 2.0
URL: https://github.com/oldarmyc/nova-agent
Source0: https://github.com/oldarmyc/nova-agent/archive/%{version}/nova-agent-%{version}.tar.gz
BuildArch: noarch

%{?with_systemd:BuildRequires: systemd}
BuildRequires: python%{?with_python3:3}-devel
BuildRequires: python%{?with_python3:3}-setuptools
%if %{with tests}
%{!?with_python3:BuildRequires: python-mock}
BuildRequires: python%{?with_python3:3}-nose
%{?el6:BuildRequires: python-unittest2}
%{?el6:BuildRequires: python-argparse}
BuildRequires: python%{?with_python3:3}-crypto
BuildRequires: python%{?with_python3:3}-netifaces
BuildRequires: python%{?with_python3:3}-pyxs
%endif

%{?el6:Requires: python-argparse}
Requires: python%{?with_python3:3}-crypto
Requires: python%{?with_python3:3}-netifaces
Requires: python%{?with_python3:3}-pyxs
%if %{with systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%endif


%description
Python agent for setting up clean servers on Xen using xenstore data


%prep
%autosetup -p 1


%build
%if %{with python3}
%py3_build
%else
%py2_build
%endif


%install
%if %{with python3}
%py3_install
%else
%py2_install
%endif

%if %{with systemd}
install -Dm644 etc/nova-agent.service %{buildroot}/%{_unitdir}/nova-agent.service
%else
install -Dm755 etc/nova-agent.redhat %{buildroot}/%{_initddir}/nova-agent
%endif


%if %{with tests}
%check
%if %{with python3}
nosetests-%{python3_version} -v
%else
nosetests -v
%endif
%endif


%post
%if %{with systemd}
%systemd_post nova-agent.service
%else
chkconfig --add nova-agent
%endif


%preun
%if %{with systemd}
%systemd_preun nova-agent.service
%else
if [ $1 -eq 0 ]; then
    service nova-agent stop &> /dev/null
    chkconfig --del nova-agent &> /dev/null
fi
%endif


%postun
%if %{with systemd}
%systemd_postun_with_restart nova-agent.service
%else
if [ $1 -ge 1 ]; then
    service nova-agent condrestart >/dev/null 2>&1 || :
fi
%endif


%files
%license LICENSE.txt
%if %{with python3}
%{python3_sitelib}/novaagent*
%else
%{python2_sitelib}/novaagent*
%endif
%{_bindir}/nova-agent
%if %{with systemd}
%{_unitdir}/nova-agent.service
%else
%{_initddir}/nova-agent
%endif


%changelog
* Wed Aug 02 2017 Carl George <carl@george.computer> - 2.0.3-1
- Latest upstream
- Run test suite

* Mon Jun 26 2017 Dave Kludt <david.kludt@rackspace.com> 2.0.0-1
- Refactor code and bump to higher version so upgrade can be done

* Mon Feb 15 2016 Daniel Wallace <danielwallace@gtmanfred.com> 0.2.1-1
- Always write a string to xenstore on returns

* Mon Feb 01 2016 Carl George <carl.george@rackspace.com> - 0.2.0-1
- Disable debug packages
- Build with Python 3 on Fedora and openSUSE
- openSUSE macros fixes

* Fri Jan 29 2016 Carl George <carl.george@rackspace.com> - 0.1.0-1
- Initial build of package
