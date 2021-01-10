==========
Change Log
==========

v0.4.0 (2020-01-10)
===================
This is the last release officially supporting Python 3.5.

Package-wise:

* changed the internal (non-public) structure of the package
* no new features or public API changes
* minor code improvements and fixes.

Repository-wise:

* new documentation (hosted by ReadTheDocs)
* tox, TravisCI, Makefile completely rewritten.


v0.3.0 (2020-03-26)
===================
Backward incompatible API changes
---------------------------------
* ``option_groups`` decorator now takes options as positional arguments ``*options``;
* ``Group.section`` decorator now takes sections as positional arguments ``*sections``;
* ``align_sections_help`` was renamed to ``align_sections``;
* ``GroupSection.__init__() sorted_`` argument was renamed to ``sorted``.

Other changes
-------------
* Additional signature for ``option_group``: you can pass the ``help`` argument
  as 2nd positional argument.
* Aligned option groups (option ``align_option_groups`` with default ``True``).
* More refactoring and testing.


v0.2.0 (2020-03-11)
===================
* [Feature] Add possibility of organizing subcommands of a cloup.Group in
  multiple help sections.
* Various code improvements.
* Backward incompatible change:
    - rename ``CloupCommand`` and ``CloupGroup`` resp. to just ``Command`` and ``Group``.


v0.1.0 (2020-02-25)
===================
* First release on PyPI.
