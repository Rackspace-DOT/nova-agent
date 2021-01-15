%define version %(echo "$TAG_NAME")

Name: nova-agent
Summary: some summary of nova-agent
Version: %{version}
Release: 1%{?dist}
License: Proprietary or GPL-2 or whatever
Group: Applications/System
Source0: nova-agent.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: python3-devel

%if "%{?dist}" == ".el7"
Requires: python36-cryptography
%else
Requires: python3-cryptography
%endif

%description
It's yo fav! nova-agent!
%prep
%setup -q
%install
rm -rf $RPM_BUILD_ROOT
%{__python3} setup.py pyz
mkdir -p $RPM_BUILD_ROOT/usr/bin/
cp usr/nova-agent.pyz $RPM_BUILD_ROOT/usr/bin/nova-agent
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
cp etc/nova-agent.service $RPM_BUILD_ROOT/%{_unitdir}/nova-agent.service
%clean
rm -rf %{buildroot}
%files
%defattr(-,root,root,-)
/usr/bin/nova-agent
%{_unitdir}/nova-agent.service
%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service
