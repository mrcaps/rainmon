## Setup instructions for Windows 7

These are setup instructions from scratch for a Windows 7 single-machine configuration.

### Required packages

 * Install numpy and scipy. There are a number of ways to do this:
   * Easy, but work best without another Python install
     * Recommended: Python(x,y) (http://code.google.com/p/pythonxy/wiki/Downloads)
     * EPD (a free version is available here: http://www.enthought.com/products/epd_free.php)
   * A bit more complicated, but works with existing Python distribution
     * Install numpy from here: http://sourceforge.net/projects/numpy/files/
     * Install scipy from here: http://sourceforge.net/projects/scipy/files/
 * Install RabbitMQ: http://www.rabbitmq.com/download.html (requires Erlang)
 * You will need `make`. Installing Python(x,y) above will install this for you.
 * `easy_install celery django-celery`
     * If celery has trouble building (e.g. not finding `vcvarsall.bat`, trying an earlier version may help, like `easy_install celery==2.5.5`)