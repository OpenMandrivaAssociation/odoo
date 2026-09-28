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
Source2:	odoo.conf
Source3:	odoo.sysusers
Source4:	README.install.omv
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(geoip2)
BuildRequires:	python%{pyver}dist(gevent)
BuildRequires:	python%{pyver}dist(num2words)
BuildRequires:	python%{pyver}dist(ofxparse)
BuildRequires:	python%{pyver}dist(openpyxl)
BuildRequires:	python%{pyver}dist(rjsmin)
BuildRequires:	python%{pyver}dist(python-stdnum)
BuildRequires:	python%{pyver}dist(vobject)
BuildRequires:	python%{pyver}dist(xlsxwriter)
BuildRequires:	python%{pyver}dist(zeep)
Requires:	python
Requires:	python%{pyver}dist(geoip2)
Requires:	python%{pyver}dist(gevent)
Requires:	python%{pyver}dist(num2words)
Requires:	python%{pyver}dist(ofxparse)
Requires:	python%{pyver}dist(openpyxl)
Requires:	python%{pyver}dist(rjsmin)
Requires:	python%{pyver}dist(python-stdnum)
Requires:	python%{pyver}dist(vobject)
Requires:	python%{pyver}dist(xlsxwriter)
Requires:	python%{pyver}dist(zeep)
Requires:	python%{pyver}dist(asn1crypto)
Requires:	python%{pyver}dist(attrs)
Requires:	python%{pyver}dist(babel)
Requires:	python%{pyver}dist(beautifulsoup4)
Requires:	python%{pyver}dist(cbor2)
Requires:	python%{pyver}dist(certifi)
Requires:	python%{pyver}dist(chardet)
Requires:	python%{pyver}dist(cryptography)
Requires:	python%{pyver}dist(python-dateutil)
Requires:	python%{pyver}dist(docopt)
Requires:	python%{pyver}dist(docutils)
Requires:	python%{pyver}dist(freezegun)
Requires:	python%{pyver}dist(greenlet)
Requires:	python%{pyver}dist(h11)
Requires:	python%{pyver}dist(idna)
Requires:	python%{pyver}dist(pillow)
Requires:	python%{pyver}dist(isodate)
Requires:	python%{pyver}dist(jinja2)
Requires:	python%{pyver}dist(python-ldap)
Requires:	python%{pyver}dist(libsass)
Requires:	python%{pyver}dist(lxml)
Requires:	python%{pyver}dist(lxml-html-clean)
Requires:	python%{pyver}dist(python-magic)
Requires:	python%{pyver}dist(markupsafe)
Requires:	python%{pyver}dist(passlib)
Requires:	python%{pyver}dist(platformdirs)
Requires:	python%{pyver}dist(polib)
Requires:	python%{pyver}dist(psutil)
Requires:	python%{pyver}dist(psycopg2)
Requires:	python%{pyver}dist(pyopenssl)
Requires:	python%{pyver}dist(pypdf)
Requires:	python%{pyver}dist(pyserial)
Requires:	python%{pyver}dist(pytz)
Requires:	python%{pyver}dist(pyusb)
Requires:	python%{pyver}dist(qrcode)
Requires:	python%{pyver}dist(reportlab)
Requires:	python%{pyver}dist(requests)
Requires:	python%{pyver}dist(requests-file)
Requires:	python%{pyver}dist(requests-toolbelt)
Requires:	python%{pyver}dist(six)
Requires:	python%{pyver}dist(zope.event)
Requires:	python%{pyver}dist(zope.interface)
Requires:	python%{pyver}dist(urllib3)
Requires:	python%{pyver}dist(werkzeug)
Requires:	python%{pyver}dist(xlrd)
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

%build
%py_build

%install
%py_install

addons=$(find %{buildroot}%{python_sitelib} %{buildroot}%{python_sitearch} -type d -path '*/odoo/addons' | head -1)
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
ExecStart=/usr/bin/python -m odoo --config /etc/odoo/odoo.conf
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
%{python_sitelib}/odoo
%{python_sitelib}/odoo-*.egg-info
%{_bindir}/odoo
%dir %attr(0750,odoo,odoo) /var/lib/odoo
%dir %attr(0750,odoo,odoo) /var/log/odoo
%dir %{_sysconfdir}/odoo
%attr(0640,root,odoo) %config(noreplace) %{_sysconfdir}/odoo/odoo.conf
%{_unitdir}/odoo.service
%{_sysusersdir}/odoo.conf
%{_tmpfilesdir}/odoo.conf

%files nginx
%config(noreplace) %{_sysconfdir}/nginx/sites-available/odoo.conf
