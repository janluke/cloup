==========
Change Log
==========

..  V0.X.X (in development)
    =======================
    **Requirements**
    **Incompatible changes**
    **Deprecated**
    **Compatible changes and features**


V0.5.0 (2021-02-10)
===================
**Requirements**

- Drop support to Python 3.5.

**Deprecated**

- ``GroupSection`` was renamed as ``Section``.

**Compatible changes and features**

- Added a subpackage for defining **constraints** on parameters groups
  (including ``OptionGroup``'s).
- The code for adding support to option groups was extracted to ``OptionGroupMixin``.
- Most of the code for adding support to subcommand sections was extracted to
  ``SectionMixin``.

**Project changes**

- Migrated from TravisCI to GitHub Actions.


v0.4.0 (2020-01-10)
===================

**Requirements**

- This is the last release officially supporting Python 3.5.

**Compatible changes and features**

- Changed the internal (non-public) structure of the package.
- Minor code improvements.

**Repository-wise:**

- New documentation (hosted by ReadTheDocs)
- Tox, TravisCI, Makefile completely rewritten.


v0.3.0 (2020-03-26)
===================
Backward incompatible API changes
---------------------------------
- ``option_groups`` decorator now takes options as positional arguments ``*options``;
- ``Group.section`` decorator now takes sections as positional arguments ``*sections``;
- ``align_sections_help`` was renamed to ``align_sections``;
- ``GroupSection.__init__() sorted_`` argument was renamed to ``sorted``.

Other changes
-------------
- Additional signature for ``option_group``: you can pass the ``help`` argument
  as 2nd positional argument.
- Aligned option groups (option ``align_option_groups`` with default ``True``).
- More refactoring and testing.


v0.2.0 (2020-03-11)
===================
- [Feature] Add possibility of organizing subcommands of a cloup.Group in
  multiple help sections.
- Various code improvements.
- Backward incompatible change:
    - rename ``CloupCommand`` and ``CloupGroup`` resp. to just ``Command`` and ``Group``.


v0.1.0 (2020-02-25)
===================
- First release on PyPI.
