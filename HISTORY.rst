=======
History
=======
0.3.0 (2020-03-26)
------------------
* Backward incompatible API changes

  - ``option_groups`` decorator now takes options as positional arguments ``*options``;
  - ``Group.section`` decorator now takes sections as positional arguments ``*sections``;
  - ``align_sections_help`` was renamed to ``align_sections``;
  - ``GroupSection.__init__() sorted_`` argument was renamed to ``sorted``.

* Additional signature for ``option_group``: you can pass the ``help`` argument
  as 2nd positional argument.
* Aligned option groups (option ``align_option_groups`` with default ``True``).
* More refactoring and testing.


0.2.0 (2020-03-11)
------------------

* Rename CloupCommand and CloupGroup resp. to just Command and Group
* [Feature] Add possibility of organizing subcommands of a cloup.Group in multiple help sections
* Various code improvements


0.1.0 (2020-02-25)
------------------

* First release on PyPI.
