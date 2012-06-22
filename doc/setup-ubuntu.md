## Setup instructions for Ubuntu 12.04

These are setup instructions from scratch for an Ubuntu 12.04 single-machine configuration.

### Required packages

```
sudo su
apt-get install make python-scipy python-matplotlib

wget https://www.djangoproject.com/download/1.3.1/tarball/
tar xzvf Django-1.3.1.tar.gz
cd Django-1.3.1.tar.gz
python setup.py install

apt-get install python-setuptools rabbitmq-server
easy_install celery django-celery
```