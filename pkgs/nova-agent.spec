%global debug_package %{nil}

# python3
%if 0%{?fedora} || 0%{?suse_version}
%global with_python3 1
%endif

# systemd
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} >= 7
%global with_systemd 1
%endif

# suse macro fixes
%if 0%{?suse_version}
%global __python3 /usr/bin/python3
%global python3_version %{py3_ver}
%endif

# el6 macro fixes
%if 0%{?rhel} && 0%{?rhel} <= 6
%global __python2 %{__python}
%global python2_version %{python_version}
%global python2_sitelib %{python_sitelib}
%endif

Name:       nova-agent
Version:    0.2.0
Release:    1%{?dist}
Summary:    Agent for setting up clean servers on Xen

Group:      System Environment/Base
License:    ASL 2.0
URL:        https://github.com/gtmanfred/nova-agent
Source0:    https://github.com/gtmanfred/nova-agent/archive/v%{version}.tar.gz
BuildArch:  noarch

%if 0%{?with_python3}
BuildRequires: python3-devel
BuildRequires: python3-setuptools
%else
BuildRequires: python-devel
BuildRequires: python-setuptools
%endif # with_python3

# systemd macros
%if 0%{?with_systemd}
%if 0%{?suse_version}
BuildRequires: systemd-rpm-macros
%else
BuildRequires: systemd
%endif # suse_version
%endif # with_systemd

# pycrypto
%if 0%{?with_python3}
%if 0%{?suse_version}
Requires: python3-pycrypto
%else
Requires: python3-crypto
%endif # suse_version
%else
Requires: python-crypto
%endif # with_python3

# scriptlets
%if 0%{?with_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
%endif # with_systemd

# common requirements
Requires: /usr/bin/xenstore-ls
Requires: /usr/bin/xenstore-read
Requires: /usr/bin/xenstore-rm
Requires: /usr/bin/xenstore-write


%description
Python agent for setting up clean servers on Xen using xenstore data and the
command line commands:
xenstore-write
xenstore-read
xenstore-ls
xenstore-rm


%prep
%setup -q


%build
%if 0%{?with_python3}
%{__python3} setup.py build
%else
%{__python2} setup.py build
%endif # with_python3


%install
%if 0%{?with_python3}
%{__python3} setup.py install --optimize 1 --skip-build --root %{buildroot}
%else
%{__python2} setup.py install --optimize 1 --skip-build --root %{buildroot}
%endif # with_python3

%if 0%{?with_systemd}
install -Dm644 etc/%{name}.service %{buildroot}/%{_unitdir}/nova-agent.service
%else
install -Dm755 etc/%{name}.redhat %{buildroot}/%{_initddir}/nova-agent
%endif # with_systemd


%post
%if 0%{?suse_version}
%service_add_post %{name}.service
%else
%if 0%{?with_systemd}
%systemd_post %{name}.service
%else
chkconfig --add %{name}
%endif # with_systemd
%endif # suse_version


%preun
%if 0%{?suse_version}
%service_del_preun %{name}.service
%else
%if 0%{?with_systemd}
%systemd_preun %{name}.service
%else
if [ $1 -eq 0 ]; then
    service %{name} stop &> /dev/null
    chkconfig --del %{name} &> /dev/null
fi
%endif # with_systemd
%endif # suse_version


%postun
%if 0%{?suse_version}
%service_del_postun %{name}.service
%else
%if 0%{?with_systemd}
%systemd_postun_with_restart %{name}.service
%else
if [ $1 -ge 1 ]; then
    service %{name} condrestart >/dev/null 2>&1 || :
fi
%endif # with_systemd
%endif # suse_version


%files
%{!?_licensedir:%global license %%doc}
%license LICENSE.txt
%if 0%{?with_python3}
%{python3_sitelib}/novaagent*
%else
%{python2_sitelib}/novaagent*
%endif # with_python3
%{_bindir}/nova-agent
%if 0%{?with_systemd}
%{_unitdir}/nova-agent.service
%else
%{_initddir}/nova-agent
%endif # with_systemd


%changelog
* Mon Feb 01 2016 Carl George <carl.george@rackspace.com> - 0.2.0-1
- Disable debug packages
- Build with Python 3 on Fedora and openSUSE
- openSUSE macros fixes

* Fri Jan 29 2016 Carl George <carl.george@rackspace.com> - 0.1.0-1
- Initial build of package
