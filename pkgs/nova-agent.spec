%global pythonver %(%{__python} -c "import sys; print sys.version[:3]" 2>/dev/null || echo 0.0)
%global _name novaagent

Name:       nova-agent
Version:    0.1
Release:    1%{?dist}
Summary:    Agent for setting up clean servers on Xen

Group:      System Environment/Base
License:    GPL
URL:        https://github.com/gtmanfred/nova-agent
Source0:    https://github.com/gtmanfred/nova-agent/archive/master.tar.gz

BuildRequires:  python-setuptools python
%if 0%{?rhel} != 6 && 0%{?suse_version} == 0
BuildRequires:  systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
%endif
%if 0%{?suse_version} >=13
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
%setup -qc

%build
cd %{name}-master
%{__python} setup.py build

%install
echo %{rhel}
cd %{name}-master
%__python setup.py install --skip-build --root=%{buildroot}

%if 0%{?rhel} == 6
install -Dm755 etc/%{name}.redhat %{buildroot}/%{_initddir}/nova-agent
%else
install -Dm644 etc/%{name}.service %{buildroot}/%{_unitdir}/nova-agent.service
%endif

if [ -f %{buildroot}%{python_sitelib}/%{_name}-%{version}-py%{pythonver}.egg-info ]; then
    echo %{python_sitelib}/%{_name}-%{version}-py%{pythonver}.egg-info
fi > egg-info

%if 0%{?rhel} != 6 && 0%{?suse_version} == 0
%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service
%endif

%if 0%{?suse_version} >= 13
%pre
%service_add_pre %{name}.service

%post
%service_add_post %{name}.service

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service
%endif

%files
%{python_sitelib}/%{_name}-%{version}-py%{pythonver}.egg-info
%{python_sitelib}/novaagent/
%{_bindir}/nova-agent

%if 0%{?rhel} == 6
%{_initddir}/nova-agent
%else
%{_unitdir}/nova-agent.service
%endif
