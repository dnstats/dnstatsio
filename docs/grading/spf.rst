SPF Grading
===========
SPF grading starts getting a ceiling from the final qualifier. Then the grading
method will use :py:meth:`dnstats.dnsvlidate.spf.validate` to ensue the record
is valid. If the record is invalid the grading method shall return 0, this is
due to RFC 7208, Section 4.6.


Policy Grading
--------------
================ =============
Policy             Grade
================ =============
Fail             100
Soft-fail        75
Neutral          50
Default Neutral  40
================ =============

Demerits
--------
