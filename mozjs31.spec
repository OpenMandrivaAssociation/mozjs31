%global		pre_release		.rc0

Summary:	JavaScript interpreter and libraries
Name:		mozjs31
Version:	31.2.0
Release:	3%{?dist}
License:	MPLv2.0 and BSD and GPLv2+ and GPLv3+ and LGPLv2.1 and LGPLv2.1+
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey/Releases/31
Source0:	https://people.mozilla.org/~sstangl/mozjs-%{version}%{pre_release}.tar.bz2
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	readline-devel
BuildRequires:	/usr/bin/zip
BuildRequires:	/usr/bin/python

# Patches from 0ad
Patch0:		FixForOfBailouts.diff
Patch1:		FixTraceLoggerBuild.diff
Patch2:		FixTraceLoggerFlushing.diff

%description
JavaScript is the Netscape-developed object scripting language used in millions
of web pages and server applications worldwide. Netscape's JavaScript is a
super set of the ECMA-262 Edition 3 (ECMAScript) standard scripting language,
with only mild differences from the published standard.

%package devel
Summary: Header files, libraries and development documentation for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%prep
%setup -q -n mozjs-%{version}/js/src
%patch0 -p3
%patch1 -p3
%patch2 -p3

%if 0%{?fedora} > 22
# Correct failed to link tests due to hardened build
sed -i 's|"-O2"|"-O2 -fPIC"|' configure
%endif

%build
# Need -fpermissive due to some macros using nullptr as bool false
export CFLAGS="%{optflags} -fpermissive"
export CXXFLAGS="$CFLAGS"
%configure \
	--with-system-nspr \
	--enable-threadsafe \
	--enable-readline \
	--enable-xterm-updates \
	--enable-shared-js \
	--enable-gcgenerational \
	--enable-optimize \
	--with-system-zlib \
	--enable-system-ffi \
	--with-system-icu \
	--without-intl-api
# Not build smp safe
make

%install
make install DESTDIR=%{buildroot}

chmod a-x  %{buildroot}%{_libdir}/pkgconfig/*.pc

# Do not install binaries or static libraries
rm -f %{buildroot}%{_libdir}/*.a %{buildroot}%{_bindir}/js*

# Install files, not symlinks to build directory
pushd %{buildroot}%{_includedir}
    for link in `find . -type l`; do
	header=`readlink $link`
	rm -f $link
	cp -p $header $link
    done
popd
cp -p js/src/js-config.h %{buildroot}%{_includedir}/mozjs-31

%check
# Some tests will fail
tests/jstests.py -d -s --no-progress ../../js/src/js/src/shell/js || :

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license ../../LICENSE
%doc ../../README
%{_libdir}/*.so

%files devel
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-31

%changelog
* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 31.2.0-3
- Rebuilt for GCC 5 C++11 ABI change

* Sun Mar 15 2015 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 31.2.0-2
- Update licenses
- Remove INSTALL from devel package

* Sat Mar 14 2015 pcpa <paulo.cesar.pereira.de.andrade@gmail.com> - 31.2.0-1
- Initial mozjs31 spec.