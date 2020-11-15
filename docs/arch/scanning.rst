Scanning Arch
-------------

The section will explain how the scan process works. It will setup through the process.

Kick off
~~~~~~~~
The scan is kicked off by Celery Beat, exact time can be found in the beat setup method for celery.py. Beat calls
:meth:`dnstats.celery.do_run`. :meth:`dnstats.celery.do_run` makes a run. If ``DNSTATS_ENV`` is ``Development`` the
run will only run for top few hundred or so sites. If that is not set the scan will scan the whole one million sites.
This method also sends the start of scan email. Once the email as been sent :meth:`dnstas.celery.launch_run` is called
with the id of the run just created.

Queuing
~~~~~~~
Now that :meth:`dnstas.celery.launch_run` has been called the run is looked up. This method grabs the site needs for
the scan. Next the list of sites is broken into lists of 10,000 sites. We loop over the list of lists, the outer loop.
In a inner loop we celery chain of :meth:`dnstas.celery.site_stat` into  :meth:`dnstas.celery.process_result`. Each
group of 10,000 is in a celery group. Once the the outer loop is done the server ends a done with scanning message.


Scanning
~~~~~~~~
All of the scanning is sent to the ``gevent`` queue. The name has made when I was tryng to use gevent for forking
model for the scans, but that failed. The ``gevent`` queue should have lots of power. As of writing I 10 worker vms
with 6 celery worker each that have 25 concurrency each. Since this task is mostly network bound this makes sense.

Only thing that should happen in this stage is do dns look ups. All analysis should happen in later stages. The
:meth:`dnstas.celery.site_stat` returns a ``dict`` and then celery passes this to
:meth:`dnstas.celery.process_result`.

Process Results
~~~~~~~~~~~~~~~
This stage uses the ``celery`` (default) queue. This queue is much less powershell than the ``gevent`` (scanning) queue.
In production I have about 10 celery vms with 1 celery worker with about 20 concurrency each.

In this stage celery passes the ``dict`` from :meth:`dnstas.celery.site_stat` into
:meth:`dnstas.celery.process_result`. The first stage is build the :class:`dnstats.models.SiteRun` and then save it.
Next, all the grading methods are called async, i.e. enqueues the grading jobs.

Grading
~~~~~~~
This stage uses the ``celery`` queue.

The grading method gets the :class:`dnstats.models.SiteRun` based on the passed :class:`dnstats.models.SiteRun` id
passed. Then it gets the site. Does the grading logic and updates the :class:`dnstats.models.SiteRun` with the grades.
Once the grading is saved the remarks (or errors from the grading and validation process) are saved to the database.
