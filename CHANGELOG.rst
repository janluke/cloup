==========
Change Log
==========

v0.3.0 (2020-03-26) - API changes and aligned option groups
===========================================================

Backward incompatible API changes
---------------------------------

- ``option_groups`` decorator now takes options as positional arguments ``*options``;
- ``Group.section`` decorator now takes sections as positional arguments ``*sections``;
- ``align_sections_help`` was renamed to ``align_sections``;
- ``GroupSection.__init__() sorted_`` argument was renamed to ``sorted``.

Other changes
-------------
* Additional signature for ``option_group``: you can pass the ``help`` argument
  as 2nd positional argument.
* Aligned option groups (option ``align_option_groups`` with default ``True``).
* More refactoring and testing.


v0.2.0 (2020-03-11) - Introducing Group sections
================================================

* [Feature] Add possibility of organizing subcommands of a cloup.Group in
  multiple help sections.
* Backward incompatible change:
    - rename ``CloupCommand`` and ``CloupGroup`` resp. to just ``Command`` and ``Group``.
* Various code improvements.


v0.1.0 (2020-02-25) - First release
===================================
