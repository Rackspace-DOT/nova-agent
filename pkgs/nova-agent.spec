%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_version: %global python2_version %(%{__python2} -c "import sys; sys.stdout.write(sys.version[:3])")}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%if 0%{?fedora} || 0%{?rhel}
%global redhat 1
%if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
%global with_systemd 1
%else
%global with_systemd 0
%endif
%endif

%if 0%{?suse_version}
%global suse 1
%global with_systemd 1
%endif

Name:       nova-agent
Version:    0.1.0
Release:    1%{?dist}
Summary:    Agent for setting up clean servers on Xen

Group:      System Environment/Base
License:    Apache 2.0
URL:        https://github.com/gtmanfred/nova-agent
Source0:    https://github.com/gtmanfred/nova-agent/archive/v%{version}.tar.gz
BuildArch:  noarch

%if 0%{?redhat}
BuildRequires: python-devel
%endif # redhat
BuildRequires:  python-setuptools

# systemd macros
%if 0%{?with_systemd}
%if 0%{?redhat}
BuildRequires: systemd
%endif # redhat
%if 0%{?suse}
BuildRequires: systemd-rpm-macros
%endif # suse
%endif # with_systemd

# pycrypto
%if 0%{?redhat}
Requires:   python-crypto
%endif # redhat
%if 0%{?suse}
Requires:   python-pycrypto
%endif # suse

# scriptlets
%if 0%{?redhat}
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
%endif # redhat
%if 0%{?suse}
Requires(post): systemd-rpm-macros
Requires(preun): systemd-rpm-macros
Requires(postun): systemd-rpm-macros
%endif # suse

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
%{__python2} setup.py build


%install
%{__python2} setup.py install --skip-build --root=%{buildroot}

%if 0%{?with_systemd}
install -Dm644 etc/%{name}.service %{buildroot}/%{_unitdir}/nova-agent.service
%else
install -Dm755 etc/%{name}.redhat %{buildroot}/%{_initddir}/nova-agent
%endif # with_systemd

%post
%if 0%{?redhat}
%if 0%{?with_systemd}
%systemd_post %{name}.service
%else
chkconfig --add %{name}
%endif # with_systemd
%endif # redhat

%if 0%{?suse}
%service_add_post %{name}.service
%endif # suse


%preun
%if 0%{?redhat}
%if 0%{?with_systemd}
%systemd_preun %{name}.service
%else
if [ $1 -eq 0 ] ; then
    service %{name} stop &> /dev/null
    chkconfig --del %{name} &> /dev/null
fi
%endif # with_systemd
%endif # redhat

%if 0%{?suse}
%service_del_preun %{name}.service
%endif # suse


%postun
%if 0%{?redhat}
%if 0%{?with_systemd}
%systemd_postun_with_restart %{name}.service
%else
if [ "$1" -ge "1" ] ; then
    service %{name} condrestart >/dev/null 2>&1 || :
fi
%endif # with_systemd
%endif # redhat

%if 0%{?suse}
%service_del_postun %{name}.service
%endif # suse


%files
%{python2_sitelib}/novaagent*
%{_bindir}/nova-agent
%if 0%{?with_systemd}
%{_unitdir}/nova-agent.service
%else
%{_initddir}/nova-agent
%endif # with_systemd
