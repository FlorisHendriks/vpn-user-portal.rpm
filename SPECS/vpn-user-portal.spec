%global git a63b4ff69e623b64b70c26de48019188eaa33b96

Name:       vpn-user-portal
Version:    3.0.0
Release:    0.438%{?dist}
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
#        "phpunit/phpunit": "^9"
#    },
BuildRequires:  phpunit9

#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gmp": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-pdo_sqlite": "*",
#        "ext-sodium": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-server": "7.x-dev",
#        "fkooman/secookie": "^6",
#        "php": ">=7.4"
#    },
BuildRequires:  php(language) >= 7.4
BuildRequires:  php-curl
BuildRequires:  php-date
BuildRequires:  php-filter
BuildRequires:  php-gmp
BuildRequires:  php-hash
BuildRequires:  php-json
BuildRequires:  php-mbstring
BuildRequires:  php-openssl
BuildRequires:  php-pcre
BuildRequires:  php-pdo
BuildRequires:  php-pdo_sqlite
BuildRequires:  php-sodium
BuildRequires:  php-spl
BuildRequires:  php-composer(fkooman/secookie) >= 6
BuildRequires:  php-composer(fkooman/secookie) < 7
BuildRequires:  php-composer(fkooman/oauth2-server) >= 7
BuildRequires:  php-composer(fkooman/oauth2-server) < 8

Requires:   php-composer(fedora/autoloader)
Requires:   httpd-filesystem
Requires:   vpn-ca
Requires:   crontabs
Requires:   qrencode
Requires:   php-cli
#    "require": {
#        "ext-curl": "*",
#        "ext-date": "*",
#        "ext-filter": "*",
#        "ext-gmp": "*",
#        "ext-hash": "*",
#        "ext-json": "*",
#        "ext-mbstring": "*",
#        "ext-openssl": "*",
#        "ext-pcre": "*",
#        "ext-pdo": "*",
#        "ext-pdo_sqlite": "*",
#        "ext-sodium": "*",
#        "ext-spl": "*",
#        "fkooman/oauth2-server": "7.x-dev",
#        "fkooman/secookie": "^6",
#        "php": ">=7.4"
#    },
Requires:   php(language) >= 7.4
Requires:   php-curl
Requires:   php-date
Requires:   php-filter
Requires:   php-gmp
Requires:   php-hash
Requires:   php-json
Requires:   php-mbstring
Requires:   php-openssl
Requires:   php-pcre
Requires:   php-pdo
Requires:   php-pdo_sqlite
Requires:   php-sodium
Requires:   php-spl
Requires:   php-composer(fkooman/secookie) >= 6
Requires:   php-composer(fkooman/secookie) < 7
Requires:   php-composer(fkooman/oauth2-server) >= 7
Requires:   php-composer(fkooman/oauth2-server) < 8

Requires(post): /usr/sbin/semanage
Requires(post): /usr/bin/openssl
Requires(postun): /usr/sbin/semanage

#    "suggest": {
#        "ext-ldap": "Support LDAP Authentication",
#        "ext-pdo_mysql": "Support MySQL/MariaDB",
#        "ext-pdo_pgsql": "Support PostgreSQL",
#        "ext-radius": "Support RADIUS Authentication"
#    },
Suggests:  php-ldap
Suggests:  php-pdo_mysql
Suggests:  php-pdo_pgsql
Suggests:  php-radius

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
require_once '%{_datadir}/php/fkooman/SeCookie/autoload.php';
require_once '%{_datadir}/php/fkooman/OAuth/Server/autoload.php';
# optional dependency
if (is_file('%{_datadir}/php/fkooman/SAML/SP/autoload.php') && is_readable('%{_datadir}/php/fkooman/SAML/SP/autoload.php')) {
    require_once '%{_datadir}/php/fkooman/SAML/SP/autoload.php';
}
AUTOLOAD

%install
mkdir -p %{buildroot}%{_datadir}/vpn-user-portal
cp VERSION %{buildroot}%{_datadir}/vpn-user-portal
mkdir -p %{buildroot}%{_datadir}/php/Vpn/Portal
cp -pr src/* %{buildroot}%{_datadir}/php/Vpn/Portal

# bin
for i in add-user status
do
    install -m 0755 -D -p bin/${i}.php %{buildroot}%{_sbindir}/%{name}-${i}
    sed -i '1s/^/#!\/usr\/bin\/php\n/' %{buildroot}%{_sbindir}/%{name}-${i}
done

# libexec
for i in generate-secrets housekeeping db daemon-sync stats
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
/usr/bin/phpunit9 tests --verbose --bootstrap=tests/autoload.php

%post
semanage fcontext -a -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
restorecon -R %{_localstatedir}/lib/vpn-user-portal || :

# Generate CA, OAuth/Node API key iff they do not exist
%{_libexecdir}/vpn-user-portal/generate-secrets

%postun
if [ $1 -eq 0 ] ; then  # final removal
semanage fcontext -d -t httpd_sys_rw_content_t '%{_localstatedir}/lib/vpn-user-portal(/.*)?' 2>/dev/null || :
fi

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/vpn-user-portal.conf
%dir %attr(2750,root,apache) %{_sysconfdir}/vpn-user-portal
%config(noreplace) %{_sysconfdir}/vpn-user-portal/config.php
%config(noreplace) %{_sysconfdir}/cron.d/vpn-user-portal
%{_sbindir}/*
%{_libexecdir}/*
%dir %{_datadir}/php/Vpn
%{_datadir}/php/Vpn/Portal
%{_datadir}/vpn-user-portal
%dir %attr(0700,apache,apache) %{_localstatedir}/lib/vpn-user-portal
%doc README.md CHANGES.md composer.json config/config.php.example CONFIG_CHANGES.md locale/CREDITS.md
%license LICENSE LICENSE.spdx

%changelog
* Thu Jan 20 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.438
- rebuilt

* Wed Jan 19 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.437
- rebuilt

* Wed Jan 19 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.436
- rebuilt

* Wed Jan 19 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.435
- rebuilt

* Wed Jan 19 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.434
- rebuilt

* Wed Jan 19 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.433
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.432
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.431
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.430
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.429
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.428
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.427
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.426
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.425
- rebuilt

* Tue Jan 18 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.424
- rebuilt

* Mon Jan 17 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.423
- rebuilt

* Mon Jan 17 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.422
- rebuilt

* Mon Jan 17 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.421
- rebuilt

* Sat Jan 15 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.420
- rebuilt

* Fri Jan 14 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.419
- rebuilt

* Fri Jan 14 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.418
- rebuilt

* Fri Jan 14 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.417
- rebuilt

* Thu Jan 13 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.416
- rebuilt

* Thu Jan 13 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.415
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.414
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.413
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.412
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.411
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.410
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.409
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.408
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.407
- rebuilt

* Wed Jan 12 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.406
- rebuilt

* Tue Jan 11 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.405
- rebuilt

* Tue Jan 11 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.404
- rebuilt

* Mon Jan 10 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.403
- rebuilt

* Mon Jan 10 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.402
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.401
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.400
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.399
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.398
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.397
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.396
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.395
- rebuilt

* Fri Jan 07 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.394
- rebuilt

* Thu Jan 06 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.393
- rebuilt

* Thu Jan 06 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.392
- rebuilt

* Thu Jan 06 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.391
- rebuilt

* Thu Jan 06 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.390
- rebuilt

* Wed Jan 05 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.389
- rebuilt

* Wed Jan 05 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.388
- rebuilt

* Tue Jan 04 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.387
- rebuilt

* Tue Jan 04 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.386
- rebuilt

* Tue Jan 04 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.385
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.384
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.383
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.382
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.381
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.380
- rebuilt

* Mon Jan 03 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.379
- rebuilt

* Sun Jan 02 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.378
- rebuilt

* Sun Jan 02 2022 François Kooman <fkooman@tuxed.net> - 3.0.0-0.377
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.376
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.375
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.374
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.373
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.372
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.371
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.370
- rebuilt

* Fri Dec 31 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.369
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.368
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.367
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.366
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.365
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.364
- rebuilt

* Thu Dec 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.363
- rebuilt

* Wed Dec 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.362
- rebuilt

* Wed Dec 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.361
- rebuilt

* Wed Dec 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.360
- rebuilt

* Wed Dec 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.359
- rebuilt

* Tue Dec 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.358
- rebuilt

* Tue Dec 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.357
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.356
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.355
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.354
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.353
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.352
- rebuilt

* Mon Dec 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.351
- rebuilt

* Thu Dec 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.350
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.349
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.348
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.347
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.346
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.345
- rebuilt

* Wed Dec 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.344
- rebuilt

* Tue Dec 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.343
- rebuilt

* Tue Dec 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.342
- rebuilt

* Tue Dec 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.341
- rebuilt

* Tue Dec 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.340
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.339
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.338
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.337
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.336
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.335
- rebuilt

* Mon Dec 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.334
- rebuilt

* Thu Dec 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.333
- rebuilt

* Thu Dec 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.332
- rebuilt

* Thu Dec 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.331
- rebuilt

* Wed Dec 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.330
- rebuilt

* Wed Dec 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.329
- rebuilt

* Wed Dec 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.328
- rebuilt

* Tue Dec 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.327
- rebuilt

* Tue Dec 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.326
- rebuilt

* Mon Dec 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.325
- rebuilt

* Mon Dec 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.324
- rebuilt

* Mon Dec 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.323
- rebuilt

* Mon Dec 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.322
- rebuilt

* Sun Dec 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.321
- rebuilt

* Sun Dec 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.320
- rebuilt

* Tue Dec 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.319
- rebuilt

* Mon Dec 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.318
- rebuilt

* Mon Dec 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.317
- rebuilt

* Mon Dec 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.316
- rebuilt

* Mon Dec 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.315
- rebuilt

* Sat Dec 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.314
- rebuilt

* Fri Dec 03 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.313
- rebuilt

* Thu Dec 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.312
- rebuilt

* Thu Dec 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.311
- rebuilt

* Thu Dec 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.310
- rebuilt

* Thu Dec 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.309
- rebuilt

* Wed Dec 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.308
- rebuilt

* Wed Dec 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.307
- rebuilt

* Tue Nov 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.306
- rebuilt

* Tue Nov 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.305
- rebuilt

* Tue Nov 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.304
- rebuilt

* Mon Nov 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.303
- rebuilt

* Mon Nov 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.302
- rebuilt

* Mon Nov 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.301
- rebuilt

* Mon Nov 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.300
- rebuilt

* Sat Nov 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.299
- rebuilt

* Fri Nov 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.298
- rebuilt

* Fri Nov 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.297
- rebuilt

* Fri Nov 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.296
- rebuilt

* Thu Nov 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.295
- rebuilt

* Wed Nov 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.294
- rebuilt

* Wed Nov 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.293
- rebuilt

* Wed Nov 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.292
- rebuilt

* Wed Nov 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.291
- rebuilt

* Tue Nov 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.290
- rebuilt

* Mon Nov 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.289
- rebuilt

* Mon Nov 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.288
- rebuilt

* Mon Nov 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.287
- rebuilt

* Mon Nov 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.286
- rebuilt

* Fri Nov 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.285
- rebuilt

* Fri Nov 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.284
- rebuilt

* Fri Nov 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.283
- rebuilt

* Fri Nov 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.282
- rebuilt

* Fri Nov 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.281
- rebuilt

* Thu Nov 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.280
- rebuilt

* Thu Nov 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.279
- rebuilt

* Tue Nov 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.278
- rebuilt

* Tue Nov 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.277
- rebuilt

* Mon Nov 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.276
- rebuilt

* Mon Nov 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.275
- rebuilt

* Wed Nov 03 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.274
- rebuilt

* Tue Nov 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.273
- rebuilt

* Tue Nov 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.272
- rebuilt

* Tue Nov 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.271
- rebuilt

* Mon Nov 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.270
- rebuilt

* Mon Nov 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.269
- rebuilt

* Mon Nov 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.268
- rebuilt

* Fri Oct 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.267
- rebuilt

* Fri Oct 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.266
- rebuilt

* Fri Oct 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.265
- rebuilt

* Thu Oct 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.264
- rebuilt

* Thu Oct 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.263
- rebuilt

* Thu Oct 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.262
- rebuilt

* Thu Oct 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.261
- rebuilt

* Thu Oct 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.260
- rebuilt

* Thu Oct 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.259
- rebuilt

* Thu Oct 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.258
- rebuilt

* Thu Oct 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.257
- rebuilt

* Thu Oct 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.256
- rebuilt

* Wed Oct 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.255
- rebuilt

* Wed Oct 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.254
- rebuilt

* Thu Oct 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.253
- rebuilt

* Thu Oct 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.252
- rebuilt

* Thu Oct 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.251
- rebuilt

* Wed Oct 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.250
- rebuilt

* Wed Oct 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.249
- rebuilt

* Tue Oct 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.248
- rebuilt

* Tue Oct 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.247
- rebuilt

* Mon Oct 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.246
- rebuilt

* Mon Oct 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.245
- rebuilt

* Mon Oct 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.244
- rebuilt

* Mon Oct 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.243
- rebuilt

* Mon Oct 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.242
- rebuilt

* Fri Oct 08 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.241
- rebuilt

* Thu Oct 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.240
- rebuilt

* Thu Oct 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.239
- rebuilt

* Wed Oct 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.238
- rebuilt

* Wed Oct 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.237
- rebuilt

* Wed Oct 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.236
- rebuilt

* Tue Oct 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.235
- rebuilt

* Tue Oct 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.234
- rebuilt

* Sat Oct 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.233
- rebuilt

* Fri Oct 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.232
- rebuilt

* Fri Oct 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.231
- rebuilt

* Fri Oct 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.230
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.229
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.228
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.227
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.226
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.225
- rebuilt

* Thu Sep 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.224
- rebuilt

* Wed Sep 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.223
- rebuilt

* Wed Sep 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.222
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.221
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.220
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.219
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.218
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.217
- rebuilt

* Tue Sep 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.216
- rebuilt

* Mon Sep 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.215
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.214
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.213
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.212
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.211
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.210
- rebuilt

* Fri Sep 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.209
- rebuilt

* Thu Sep 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.208
- rebuilt

* Thu Sep 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.207
- rebuilt

* Thu Sep 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.206
- rebuilt

* Thu Sep 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.205
- rebuilt

* Thu Sep 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.204
- rebuilt

* Wed Sep 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.203
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.202
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.201
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.200
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.199
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.198
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.197
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.196
- rebuilt

* Tue Sep 21 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.195
- rebuilt

* Mon Sep 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.194
- rebuilt

* Mon Sep 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.193
- rebuilt

* Fri Sep 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.192
- rebuilt

* Fri Sep 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.191
- rebuilt

* Fri Sep 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.190
- rebuilt

* Fri Sep 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.189
- rebuilt

* Thu Sep 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.188
- rebuilt

* Thu Sep 16 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.187
- rebuilt

* Wed Sep 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.186
- rebuilt

* Wed Sep 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.185
- rebuilt

* Wed Sep 15 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.184
- rebuilt

* Tue Sep 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.183
- rebuilt

* Mon Sep 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.182
- rebuilt

* Thu Sep 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.181
- rebuilt

* Wed Sep 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.180
- rebuilt

* Wed Sep 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.179
- rebuilt

* Wed Sep 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.178
- rebuilt

* Wed Sep 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.177
- rebuilt

* Wed Sep 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.176
- rebuilt

* Tue Aug 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.175
- rebuilt

* Tue Aug 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.174
- rebuilt

* Tue Aug 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.173
- rebuilt

* Tue Aug 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.172
- rebuilt

* Tue Aug 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.171
- rebuilt

* Thu Aug 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.170
- rebuilt

* Thu Aug 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.169
- rebuilt

* Wed Aug 11 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.168
- rebuilt

* Tue Aug 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.167
- rebuilt

* Thu Aug 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.166
- rebuilt

* Wed Aug 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.165
- rebuilt

* Wed Aug 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.164
- rebuilt

* Thu Jul 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.163
- rebuilt

* Tue Jul 27 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.162
- rebuilt

* Thu Jul 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.161
- rebuilt

* Thu Jul 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.160
- rebuilt

* Thu Jul 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.159
- rebuilt

* Thu Jul 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.158
- rebuilt

* Thu Jul 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.157
- rebuilt

* Tue Jul 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.156
- rebuilt

* Wed Jul 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.155
- rebuilt

* Wed Jul 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.154
- rebuilt

* Wed Jul 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.153
- rebuilt

* Tue Jul 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.152
- rebuilt

* Mon Jul 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.151
- rebuilt

* Mon Jul 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.150
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.149
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.148
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.147
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.146
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.145
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.144
- rebuilt

* Mon Jul 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.143
- rebuilt

* Wed Jun 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.142
- rebuilt

* Wed Jun 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.141
- rebuilt

* Tue Jun 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.140
- rebuilt

* Tue Jun 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.139
- rebuilt

* Tue Jun 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.138
- rebuilt

* Tue Jun 29 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.137
- rebuilt

* Mon Jun 28 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.136
- rebuilt

* Fri Jun 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.135
- rebuilt

* Fri Jun 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.134
- rebuilt

* Fri Jun 25 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.133
- rebuilt

* Thu Jun 24 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.132
- rebuilt

* Wed Jun 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.131
- rebuilt

* Wed Jun 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.130
- rebuilt

* Tue Jun 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.129
- rebuilt

* Tue Jun 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.128
- rebuilt

* Tue Jun 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.127
- rebuilt

* Tue Jun 22 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.126
- rebuilt

* Mon Jun 14 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.125
- rebuilt

* Sat Jun 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.124
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.123
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.122
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.121
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.120
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.119
- rebuilt

* Thu Jun 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.118
- rebuilt

* Fri Jun 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.117
- rebuilt

* Wed Jun 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.116
- rebuilt

* Wed Jun 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.115
- rebuilt

* Wed Jun 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.114
- rebuilt

* Wed Jun 02 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.113
- rebuilt

* Wed May 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.112
- rebuilt

* Wed May 26 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.111
- rebuilt

* Sun May 23 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.110
- rebuilt

* Thu May 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.109
- rebuilt

* Thu May 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.108
- rebuilt

* Thu May 20 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.107
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.106
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.105
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.104
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.103
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.102
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.101
- rebuilt

* Wed May 19 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.100
- rebuilt

* Tue May 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.99
- rebuilt

* Tue May 18 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.98
- rebuilt

* Mon May 17 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.97
- rebuilt

* Thu May 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.96
- rebuilt

* Thu May 13 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.95
- rebuilt

* Wed May 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.94
- rebuilt

* Wed May 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.93
- rebuilt

* Wed May 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.92
- rebuilt

* Wed May 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.91
- rebuilt

* Wed May 12 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.90
- rebuilt

* Mon May 10 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.89
- rebuilt

* Sat May 08 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.88
- rebuilt

* Fri May 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.87
- rebuilt

* Fri May 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.86
- rebuilt

* Fri May 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.85
- rebuilt

* Fri May 07 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.84
- rebuilt

* Thu May 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.83
- rebuilt

* Thu May 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.82
- rebuilt

* Thu May 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.81
- rebuilt

* Thu May 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.80
- rebuilt

* Thu May 06 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.79
- rebuilt

* Wed May 05 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.78
- rebuilt

* Tue May 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.77
- rebuilt

* Tue May 04 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.76
- rebuilt

* Sat May 01 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.75
- rebuilt

* Fri Apr 30 2021 François Kooman <fkooman@tuxed.net> - 3.0.0-0.74
- rebuilt

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
