Install
=======

#. Install Dependencies
    You will need the following packages:

    - Python 3.7 or later
    - Python3 headers
        - ``python3-dev`` on Debian/Ubuntu
        - ``python-devel`` on Fedora/Centos/
    - pip
        - python3-pip
    - Libevent headers
        ``libevent-devel`` on Fedora/Centos
    - postgresql
        - ``postgresql-server``
        - ``postgresql-contrib``
        - ``postgresql``
    - RabbitMQ
        - See https://www.rabbitmq.com/download.html

#. Ensure Postgres and RabbitMQ are running

#. Create Database
In a ``psql` shell run

      create user dnstats with password 'changeme!';
      create database dnstats owner dnstats;

See the Postgres doc for more details on how to configure Postgres.

#. Clone the repo::

    git clone git@git.assignitapp.com:dnstats/dnstats.git

#. Change into the repo::

    cd dnstats

#. Copy config::

    cp dnstats.src.env dnstats.env

#. Edit dnstats.src.env

   Update ``AMQP``, ```DB`,`` and ``CELERY_BACKEND``

#. Install virtualenv::

    pip3 install virtualenv --user

#. Create virtualenv::

    virtualenv -p python3 venv

#. Active venv::

    source venv/bin/activate

#. Install Python Dependencies::

    pip install -r requirements.txt

#. Load config::

    source sendgrid.env

#. Seed Database::

    python -m dnstats.db.seed

#. Start celery::

    celery -A dnstats.celery worker

#. Run Task for seeding sites