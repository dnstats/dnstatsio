Postgres Install
================
The default Postgres config is not really suitable for the DNStats work download. The follow are some changes
that should help.


postgresql.conf
---------------
1. Setup max_connections
Default 300, should be set to 500 or 1000 for DNStats.

2. shared_buffers
Set to 128 MB

pg_hba.conf
-----------
See `Postgresql docs <https://www.postgresql.org/docs/current/auth-pg-hba-conf.html>`_.