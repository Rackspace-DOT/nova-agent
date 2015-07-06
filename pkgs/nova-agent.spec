%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_version: %global python2_version %(%{__python2} -c "import sys; sys.stdout.write(sys.version[:3])")}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

%global _name novaagent

Name:       nova-agent
Version:    0.1.0
Release:    1%{?dist}
Summary:    Agent for setting up clean servers on Xen

Group:      System Environment/Base
License:    GPL
URL:        https://github.com/gtmanfred/nova-agent
Source0:    https://github.com/gtmanfred/nova-agent/archive/v%{version}.tar.gz

BuildRequires:  python-setuptools python
%if 0%{?rhel} != 6 && 0%{?suse_version} == 0
BuildRequires:  systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif
%if 0%{?suse_version}
BuildRequires:  systemd-rpm-macros
Requires(post): systemd-rpm-macros
Requires(preun): systemd-rpm-macros
Requires(postun): systemd-rpm-macros
%endif
Requires:   python-crypto


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

%if 0%{?rhel} == 6
install -Dm755 etc/%{name}.redhat %{buildroot}/%{_initddir}/nova-agent
%else
install -Dm644 etc/%{name}.service %{buildroot}/%{_unitdir}/nova-agent.service
%endif


%if 0%{?rhel} != 6 && 0%{?suse_version} == 0
%post
%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service
%endif


%if 0%{?suse_version}
%post
%service_add_post %{name}.service


%preun
%service_del_preun %{name}.service


%postun
%service_del_postun %{name}.service
%endif


%files
%{python2_sitelib}/%{_name}-%{version}-py%{python2_version}.egg-info
%{python2_sitelib}/novaagent/
%{_bindir}/nova-agent

%if 0%{?rhel} == 6
%{_initddir}/nova-agent
%else
%{_unitdir}/nova-agent.service
%endif
