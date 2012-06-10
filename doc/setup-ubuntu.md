## Setup instructions for Ubuntu 12.04

These are setup instructions from scratch for an Ubuntu 12.04 single-machine configuration.

```
sudo su
apt-get install python-scipy
apt-get install python-matplotlib

wget https://www.djangoproject.com/download/1.3.1/tarball/
tar xzvf Django-1.3.1.tar.gz
cd Django-1.3.1.tar.gz
python setup.py install

apt-get install python-setuptools
apt-get install rabbitmq-server
easy_install celery django-celery

apt-get install git
apt-get install make
git clone https://github.com/mrcaps/826
cd 826
mkdir etc/tmp
```

To see one of the analyses from the paper (e.g. the case explored in Fig. 8 and Fig. 9),
```
cp -r data/cache-cloud-disk-oct12-oct16 etc/tmp/cache/demo
```

then,
```
make celerystart &
make serverstart &
```

and open a browser window to
```
http://localhost:8000/
```