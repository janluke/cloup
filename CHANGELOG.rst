==========
Change Log
==========

..  V0.X.X (in development)
    =======================
    **Requirements**
    **Incompatible changes**
    **Deprecated**
    **Compatible changes and features**


V0.5.0 (in development)
=======================
**Requirements**

- Drop support to Python 3.5.

**Incompatible changes**

- ``@cloup.command`` and ``@cloup.group`` don't take a ``cls`` argument anymore.
  Just use the analogous ``click`` decorators if you need to pass a custom class.

**Deprecated**

- ``GroupSection`` was renamed as ``Section``.

**Compatible changes and features**

- **Constraints**. You can now define constraints on option groups and group of
  parameters in general.
- Support to option groups is now implemented in ``OptionGroupMixin``.
- Support to subcommand sections is now implemented in ``SectionMixin``.


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
