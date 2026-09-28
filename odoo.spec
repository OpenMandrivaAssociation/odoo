Summary:	Open source ERP and accounting
Name:		odoo
# The typelib generator greps every .js and .py. Odoo does not ship
# GObject typelibs, and the addon tree makes that scan dominate the build.
%global __typelib_path ^$
%global debug_package %{nil}
# Snapshot of the 20.0 branch, which release.py reports as 20.0 final.
# Git commit 17ff827a18248397342e73bb2bcac48e2b8e1027 (2026-09-26).
Version:	20.0.0
Release:	1
License:	LGPL-3.0-or-later
Group:		Applications/Productivity
URL:		https://www.odoo.com/
Source0:	https://github.com/odoo/odoo/archive/17ff827a18248397342e73bb2bcac48e2b8e1027.tar.gz#/odoo-%{version}.tar.gz
# Python packages that are not in the distribution, as source tarballs.
# Built at package build time. No network and no prebuilt wheels.
Source1:	odoo-%{version}-sdists.tar.xz
Source2:	odoo.conf
Source3:	odoo.sysusers
Source4:	README.install.omv
BuildRequires:	gcc
BuildRequires:	lib64python-devel
BuildRequires:	libev-devel
BuildRequires:	python-pip
BuildRequires:	python-setuptools
Requires:	python
Requires:	python-asn1crypto
Requires:	python-attrs
Requires:	python-babel
Requires:	python-beautifulsoup4
Requires:	python-cbor2
Requires:	python-certifi
Requires:	python-chardet
Requires:	python-cryptography
Requires:	python-dateutil
Requires:	python-docopt
Requires:	python-docutils
Requires:	python-freezegun
Requires:	python-greenlet
Requires:	python-h11
Requires:	python-idna
Requires:	python-imaging
Requires:	python-isodate
Requires:	python-jinja2
Requires:	python-ldap
Requires:	python-libsass
Requires:	python-lxml
Requires:	python-lxml-html-clean
Requires:	python-magic
Requires:	python-markupsafe
Requires:	python-passlib
Requires:	python-platformdirs
Requires:	python-polib
Requires:	python-psutil
Requires:	python-psycopg2
Requires:	python-pyopenssl
Requires:	python-pypdf
Requires:	python-pyserial
Requires:	python-pytz
Requires:	python-pyusb
Requires:	python-qrcode
Requires:	python-reportlab
Requires:	python-requests
Requires:	python-requests-toolbelt
Requires:	python-six
Requires:	python-urllib3
Requires:	python-werkzeug
Requires:	python-xlrd
Recommends:	postgresql
%description
Odoo 20 Community is an ERP with accounting, invoicing, inventory,
sales, and purchases. This package is the LGPLv3 community edition.

It listens on port 8069. PostgreSQL is expected on the local host.
See README.install.omv after installation.

%package nginx
Summary:	nginx reverse proxy for Odoo
Group:		Applications/Productivity
Requires:	%{name} = %{EVRD}
Requires:	nginx

%description nginx
nginx site that proxies odoo.* to the Odoo service on port 8069.
The site is installed disabled.

%prep
%autosetup -p1 -n odoo-17ff827a18248397342e73bb2bcac48e2b8e1027
mkdir -p sdists
tar -C sdists -xf %{SOURCE1}

%build

%install
python -m venv --system-site-packages %{buildroot}/usr/lib/odoo/venv
%{buildroot}/usr/lib/odoo/venv/bin/pip install --no-binary :all: --no-index \
	--find-links sdists --no-build-isolation \
	geoip2 gevent num2words ofxparse openpyxl pyusb rjsmin python-stdnum \
	vobject XlsxWriter zeep
%{buildroot}/usr/lib/odoo/venv/bin/pip install --no-deps --no-build-isolation .
find %{buildroot}/usr/lib/odoo/venv/bin -type f -exec \
	sed -i '1s|^#!.*python.*|#!/usr/lib/odoo/venv/bin/python|' {} +

addons=$(find %{buildroot}/usr/lib/odoo/venv -type d -path '*/odoo/addons' | head -1)
addons=${addons#%{buildroot}}

install -d %{buildroot}%{_sysconfdir}/odoo
sed "s|@ADDONS@|${addons}|" %{SOURCE2} > %{buildroot}%{_sysconfdir}/odoo/odoo.conf

install -d %{buildroot}%{_sysusersdir}
install -m 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/odoo.conf

install -d %{buildroot}/var/lib/odoo
install -d %{buildroot}/var/log/odoo
install -d %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/odoo.conf << 'EOF'
d /var/lib/odoo 0750 odoo odoo -
d /var/log/odoo 0750 odoo odoo -
EOF

install -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/odoo.service << 'EOF'
[Unit]
Description=Odoo
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/usr/lib/odoo/venv/bin/odoo --config /etc/odoo/odoo.conf
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

install -d %{buildroot}%{_sysconfdir}/nginx/sites-available
cat > %{buildroot}%{_sysconfdir}/nginx/sites-available/odoo.conf << 'EOF'
upstream odoo {
	server 127.0.0.1:8069;
}

server {
	listen 80;
	server_name odoo.*;

	proxy_read_timeout 720s;
	proxy_connect_timeout 720s;
	proxy_send_timeout 720s;
	client_max_body_size 64m;

	location / {
		proxy_pass http://odoo;
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
		proxy_set_header X-Real-IP $remote_addr;
	}
}
EOF

cp %{SOURCE4} .

%post
chown odoo:odoo /var/lib/odoo /var/log/odoo || :

%files
%doc README.install.omv README.md LICENSE
%dir /usr/lib/odoo
/usr/lib/odoo/venv
%dir %attr(0750,odoo,odoo) /var/lib/odoo
%dir %attr(0750,odoo,odoo) /var/log/odoo
%dir %{_sysconfdir}/odoo
%attr(0640,root,odoo) %config(noreplace) %{_sysconfdir}/odoo/odoo.conf
%{_unitdir}/odoo.service
%{_sysusersdir}/odoo.conf
%{_tmpfilesdir}/odoo.conf

%files nginx
%config(noreplace) %{_sysconfdir}/nginx/sites-available/odoo.conf
