## Net-SNMP on Ubuntu - compile and install

Used this instruction; did NOT use apt for the installation.

[Net-Snmp on Ubuntu - Net-SNMP Wiki](http://www.net-snmp.org/wiki/index.php/Net-Snmp_on_Ubuntu)

Critical to install the Perl development libraries

```
sudo apt-get install libperl-dev
```

Then just basically download net-snmp ta

```
./configure
```

or use the following to avoid the interactive questions:

```
./configure --with-default-snmp-version="3" --with-sys-contact="@@no.where" --with-sys-location="Unknown" --with-logfile="/var/log/snmpd.log" --with-persistent-directory="/var/net-snmp"
```

Then compile it:

```
make
```

Can test the compilation which runs a variety of tests to see what functionality has been incorporated and if it works.

```
make test
```

The time I ran it there some errors that I ignored for the moment.

Then install the code

```
sudo make install
```

Tidy up

```
make clean
make distclean
```

For the net-snmp applications to work we need to add an export command to our .bashrc" file otherwise you get runtime errors.  In my case the steps go like this.  Can then check it also is working (after logging out and back in.

```
> cd
/home/vagrant
> echo export LD_LIBRARY_PATH=/usr/local/lib >> .bashrc


vagrant@tnstelegraf:~$ snmpget --version
NET-SNMP version: 5.9.1
```

Finally, we need to set up the persistent-directory "/var/net-snmp" that we specified with ./configure above, else we get an error from snmptrap (at least).

```
sudo mkdir /var/net-snmp/
sudo chmod 777 /var/net-snmp/
```
