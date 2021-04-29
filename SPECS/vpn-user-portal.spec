%global git 67e1bfd48d11d95ed8b96b8d8969e92dea77adf8

Name:       vpn-user-portal
Version:    3.0.0
Release:    0.73%{?dist}
Summary:    User and admin portal for Let's Connect! and eduVPN
Group:      Applications/Internet
License:    AGPLv3+
URL:        https://git.sr.ht/~fkooman/vpn-user-portal
%if %{defined git}
Source0:    https://git.sr.ht/~fkooman/vpn-user-portal/archive/%{git}.tar.gz
%else
Source0:    https://git.sr.ht/~fkooman/vpn-user-portal/refs/download/%{version}/vpn-user-portal-%{version}.tar.xz
Source1:    https://git.sr.ht/~fkooman/vpn-user-portal/refs/download/%{version}/vpn-user-portal-%{version}.tar.xz.minisig
Source2:    minisign-8466FFE127BCDC82.pub
%endif
Source3:    vpn-user-portal-httpd.conf
Source4:    vpn-user-portal.cron
Patch0:     vpn-user-portal-autoload.patch

BuildArch:  noarch

BuildRequires:  minisign
BuildRequires:  php-fedora-autoloader-devel
BuildRequires:  %{_bindir}/phpab
#    "require-dev": {
#        "ext-json": "*",
#        "phpunit/phpunit": "^9",
#        "fkooman/saml-sp": "2.x-dev"
#    },
BuildRequires:  php-json
#BuildRequires:  php-composer(fkooman/saml-sp)
BuildRequires:  phpunit9

#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-sodium": "*",
#        "ext-sqlite3": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "2.x-dev",
#        "fkooman/oauth2-server": "7.x-dev",
#        "php": ">=7.4"
#    },
#    "suggest": {
#        "ext-ldap": "Support LDAP user authentication",
#        "ext-radius": "Support RADIUS user authentication"
#    },
BuildRequires:  php(language) >= 7.4
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-hash
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-sodium
BuildRequires:  php-sqlite3
BuildRequires:  php-spl
BuildRequires:  php-ldap
BuildRequires:  php-radius
BuildRequires:  php-composer(fkooman/jwt)
BuildRequires:  php-composer(fkooman/oauth2-server)

Requires:   httpd-filesystem
Requires:   vpn-ca
Requires:   wireguard-tools
Requires:   vpn-daemon
Requires:   wg-daemon
Requires:   /usr/bin/qrencode
Requires:   crontabs
#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-hash": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-sodium": "*",
#        "ext-sqlite3": "*",
#        "ext-spl": "*",
#        "fkooman/jwt": "2.x-dev",
#        "fkooman/oauth2-server": "7.x-dev",
#        "php": ">=7.4"
#    },
#    "suggest": {
#        "ext-ldap": "Support LDAP user authentication",
#        "ext-radius": "Support RADIUS user authentication"
#    },
Requires:   php(language) >= 7.4
Requires:   php-cli
Requires:   php-curl
Requires:   php-date
Requires:   php-hash
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-sodium
Requires:   php-sqlite3
Requires:   php-spl
Requires:   php-ldap
Requires:   php-radius
Requires:   php-composer(fkooman/jwt)
Requires:   php-composer(fkooman/oauth2-server)

Requires(post): /usr/sbin/semanage
Requires(post): /usr/bin/openssl
Requires(postun): /usr/sbin/semanage

%description
The user and admin portal and API for Let's Connect! and eduVPN allowing 
for self-management by users and administrative tasks by designated 
administrators.

%prep
%if %{defined git}
%setup -qn vpn-user-portal-%{git}
%else
/usr/bin/minisign -V -m %{SOURCE0} -x %{SOURCE1} -p %{SOURCE2}
%setup -qn vpn-user-portal-%{version}
%endif
%patch0 -p1

%build
echo "%{version}-%{release}" > VERSION

%{_bindir}/phpab -t fedora -o src/autoload.php src
cat <<'AUTOLOAD' | tee -a src/autoload.php
require_once '%{_datadir}/php/fkooman/Jwt/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
# optional dependency
if (is_file('%{_datadir}/php/fkooman/SAML/SP/autoload.php') && is_readable('%{_datadir}/php/fkooman/SAML/SP/autoload.php')) {
    require_once '%{_datadir}/php/fkooman/SAML/SP/autoload.php';
}
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal
cp VERSION %{buildroot}%{_datadir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/php/LC/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/LC/Portal

# bin
for i in add-user show-oauth-key suggest-ip generate-dns-zones
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_sbindir}/%{name}-${i}
    sed -i '1s/^/#!\/usr\/bin\/php\n/' %{buildroot}%{_sbindir}/%{name}-${i}
done

# libexec
for i in foreign-key-list-fetcher generate-secrets housekeeping init stats wg-sync-peers
do
    install -m 0755 -D -p libexec/${i}.php %{buildroot}%{_libexecdir}/%{name}/${i}
    sed -i '1s/^/#!\/usr\/bin\/php\n/' %{buildroot}%{_libexecdir}/%{name}/${i}
done

cp -pr schema web views locale %{buildroot}%{_datadir}/vpn-user-portal

mkdir -p %{buildroot}%{_sysconfdir}/vpn-user-portal
cp -pr config/config.php.example %{buildroot}%{_sysconfdir}/vpn-user-portal/config.php
ln -s ../../../etc/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/config

mkdir -p %{buildroot}%{_localstatedir}/lib/vpn-user-portal
ln -s ../../../var/lib/vpn-user-portal %{buildroot}%{_datadir}/vpn-user-portal/data

# cron
mkdir -p %{buildroot}%{_sysconfdir}/cron.d
%{__install} -p -D -m 0640 %{SOURCE4} %{buildroot}%{_sysconfdir}/cron.d/vpn-user-portal

# httpd
install -m 0644 -D -p %{SOURCE3} %{buildroot}%{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf

%check
%{_bindir}/phpab -o tests/autoload.php tests
cat <<'AUTOLOAD' | tee -a tests/autoload.php
require_once 'src/autoload.php';
AUTOLOAD

# XXX tests are disabled for now as they are broken
#/usr/bin/phpunit9 tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-user-portal || :

# Generate OAuth/Node API key iff they do not exist
%{_libexecdir}/vpn-user-portal/generate-secrets

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf
%dir %attr(0750,root,apache) %{_sysconfdir}/vpn-user-portal
%config(noreplace) %{_sysconfdir}/vpn-user-portal/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-user-portal
%{_sbindir}/*
%{_libexecdir}/*
%dir %{_datadir}/php/LC
%{_datadir}/php/LC/Portal
%{_datadir}/vpn-user-portal
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-user-portal
%doc README.md CHANGES.md composer.json config/config.php.example CONFIG_CHANGES.md locale/CREDITS.md
%license LICENSE LICENSE.spdx

%changelog
* Thu Apr 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.73
- rebuilt

* Thu Apr 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.72
- rebuilt

* Thu Apr 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.71
- rebuilt

* Thu Apr 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.70
- rebuilt

* Mon Apr 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.69
- rebuilt

* Fri Apr 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.68
- rebuilt

* Fri Apr 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.67
- rebuilt

* Fri Apr 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.66
- rebuilt

* Thu Apr 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.65
- rebuilt

* Thu Apr 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.64
- rebuilt

* Thu Apr 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.63
- rebuilt

* Thu Apr 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.62
- rebuilt

* Wed Apr 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.61
- rebuilt

* Wed Apr 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.60
- rebuilt

* Tue Apr 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.59
- rebuilt

* Tue Apr 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.58
- rebuilt

* Mon Apr 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.57
- rebuilt

* Sun Apr 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.56
- rebuilt

* Fri Apr 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.55
- rebuilt

* Fri Apr 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.54
- rebuilt

* Fri Apr 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.53
- rebuilt

* Thu Apr 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.52
- rebuilt

* Thu Apr 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.51
- rebuilt

* Thu Apr 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.50
- rebuilt

* Thu Apr 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.49
- rebuilt

* Thu Apr 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.48
- rebuilt

* Tue Apr 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.47
- rebuilt

* Tue Apr 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.46
- rebuilt

* Tue Apr 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.45
- rebuilt

* Fri Apr 09 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.44
- rebuilt

* Fri Apr 09 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.43
- rebuilt

* Fri Apr 09 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.42
- rebuilt

* Thu Apr 08 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.41
- rebuilt

* Thu Apr 08 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.40
- rebuilt

* Thu Apr 08 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.39
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.38
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.37
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.36
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.35
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.34
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.33
- rebuilt

* Tue Apr 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.32
- rebuilt

* Fri Mar 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.31
- rebuilt

* Fri Mar 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.30
- rebuilt

* Fri Mar 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.29
- rebuilt

* Thu Mar 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.28
- rebuilt

* Thu Mar 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.27
- rebuilt

* Thu Mar 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.26
- rebuilt

* Thu Mar 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.25
- rebuilt

* Thu Mar 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.24
- rebuilt

* Wed Mar 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.23
- rebuilt

* Wed Mar 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.22
- rebuilt

* Wed Mar 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.21
- rebuilt

* Wed Mar 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.20
- rebuilt

* Wed Mar 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.19
- rebuilt

* Tue Mar 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.18
- rebuilt

* Fri Mar 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.17
- rebuilt

* Fri Mar 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.16
- rebuilt

* Fri Mar 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.15
- rebuilt

* Fri Mar 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.14
- rebuilt

* Fri Mar 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.13
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.12
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.11
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.10
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.9
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.8
- rebuilt

* Thu Mar 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.7
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.6
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.5
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.4
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.3
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.2
- rebuilt

* Wed Mar 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.1
- update to 3.0.0

* Mon Mar 15 2021 François Kooman <fkooman@tuxed.net> - 2.3.8-1
- update to 2.3.8

* Tue Feb 23 2021 François Kooman <fkooman@tuxed.net> - 2.3.7-1
- update to 2.3.7

* Fri Nov 27 2020 François Kooman <fkooman@tuxed.net> - 2.3.6-1
- update to 2.3.6

* Tue Oct 20 2020 François Kooman <fkooman@tuxed.net> - 2.3.5-1
- update to 2.3.5

* Tue Sep 08 2020 François Kooman <fkooman@tuxed.net> - 2.3.4-1
- update to 2.3.4

* Thu Aug 20 2020 François Kooman <fkooman@tuxed.net> - 2.3.3-5
- convert php-sodium to php-libsodium functions/constants on el7

* Tue Aug 11 2020 François Kooman <fkooman@tuxed.net> - 2.3.3-4
- put version/release in VERSION file

* Mon Aug 10 2020 François Kooman <fkooman@tuxed.net> - 2.3.3-3
- update URL/summary/description

* Tue Aug 04 2020 François Kooman <fkooman@tuxed.net> - 2.3.3-2
- release files moved to src.tuxed.net

* Tue Jul 28 2020 François Kooman <fkooman@tuxed.net> - 2.3.3-1
- update to 2.3.3

* Mon Jul 27 2020 François Kooman <fkooman@tuxed.net> - 2.3.2-1
- update to 2.3.2

* Fri Jul 10 2020 François Kooman <fkooman@tuxed.net> - 2.3.1-1
- update to 2.3.1

* Mon Jun 29 2020 François Kooman <fkooman@tuxed.net> - 2.3.0-1
- update to 2.3.0

* Tue May 26 2020 François Kooman <fkooman@tuxed.net> - 2.2.8-1
- update to 2.2.8

* Thu May 21 2020 François Kooman <fkooman@tuxed.net> - 2.2.7-1
- update to 2.2.7

* Tue May 12 2020 François Kooman <fkooman@tuxed.net> - 2.2.6-1
- update to 2.2.6

* Sun Apr 05 2020 François Kooman <fkooman@tuxed.net> - 2.2.5-1
- update to 2.2.5

* Mon Mar 30 2020 François Kooman <fkooman@tuxed.net> - 2.2.4-1
- update to 2.2.4

* Mon Mar 23 2020 François Kooman <fkooman@tuxed.net> - 2.2.3-1
- update to 2.2.3

* Fri Mar 13 2020 François Kooman <fkooman@tuxed.net> - 2.2.2-1
- update to 2.2.2

* Fri Feb 14 2020 François Kooman <fkooman@tuxed.net> - 2.2.1-1
- update to 2.2.1

* Thu Feb 13 2020 François Kooman <fkooman@tuxed.net> - 2.2.0-1
- update to 2.2.0

* Mon Jan 20 2020 François Kooman <fkooman@tuxed.net> - 2.1.6-1
- update to 2.1.6

* Mon Jan 20 2020 François Kooman <fkooman@tuxed.net> - 2.1.5-1
- update to 2.1.5
- be explicit about fkooman/secookie version

* Tue Dec 10 2019 François Kooman <fkooman@tuxed.net> - 2.1.4-1
- update to 2.1.4

* Mon Dec 02 2019 François Kooman <fkooman@tuxed.net> - 2.1.3-1
- update to 2.1.3

* Thu Nov 21 2019 François Kooman <fkooman@tuxed.net> - 2.1.2-1
- update to 2.1.2

* Thu Nov 21 2019 François Kooman <fkooman@tuxed.net> - 2.1.1-1
- update to 2.1.1

* Mon Nov 04 2019 François Kooman <fkooman@tuxed.net> - 2.1.0-1
- update to 2.1.0

* Mon Oct 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.14-1
- update to 2.0.14

* Wed Sep 25 2019 François Kooman <fkooman@tuxed.net> - 2.0.13-1
- update to 2.0.13

* Thu Aug 29 2019 François Kooman <fkooman@tuxed.net> - 2.0.12-1
- update to 2.0.12

* Mon Aug 19 2019 François Kooman <fkooman@tuxed.net> - 2.0.11-1
- update to 2.0.11

* Tue Aug 13 2019 François Kooman <fkooman@tuxed.net> - 2.0.10-1
- update to 2.0.10

* Thu Aug 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.9-2
- use /usr/bin/php instead of /usr/bin/env php

* Thu Aug 08 2019 François Kooman <fkooman@tuxed.net> - 2.0.9-1
- update to 2.0.9
- switch to minisign signature verification for release builds
- add CONFIG_CHANGES to documentation

* Wed Jul 31 2019 François Kooman <fkooman@tuxed.net> - 2.0.8-1
- update to 2.0.8

* Sat Jul 20 2019 François Kooman <fkooman@tuxed.net> - 2.0.7-1
- update to 2.0.7

* Thu Jun 27 2019 François Kooman <fkooman@tuxed.net> - 2.0.6-1
- update to 2.0.6

* Fri Jun 07 2019 François Kooman <fkooman@tuxed.net> - 2.0.5-1
- update to 2.0.5

* Tue May 21 2019 François Kooman <fkooman@tuxed.net> - 2.0.4-1
- update to 2.0.4

* Tue May 14 2019 François Kooman <fkooman@tuxed.net> - 2.0.3-1
- update to 2.0.3

* Wed May 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.2-1
- update to 2.0.2

* Fri Apr 26 2019 François Kooman <fkooman@tuxed.net> - 2.0.1-1
- update to 2.0.1

* Mon Apr 01 2019 François Kooman <fkooman@tuxed.net> - 2.0.0-1
- update to 2.0.0
