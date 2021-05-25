=========
Changelog
=========

..  v0.X.X (in development)
    =======================
    Incompatible changes
    --------------------
    Deprecated
    ----------
    Compatible changes
    ------------------


v0.8.1 (2021-05-25)
===================
- Work around a minor Click 8.0.1 `issue <https://github.com/pallets/click/issues/1925>`_
  with boolean options which caused some Cloup tests to fail.

- Cosmetic: use a nicer logo and add a GitHub "header" including it.

- Slightly improved readme, docs and examples.


v0.8.0 (2021-05-19)
===================

Project changes
---------------

- Cloup license changed from MIT to 3-clause BSD, the one used by Click.
- Added a donation button.

Incompatible changes
--------------------

These incompatible changes don't affect the most "external" API used by most
clients of this library.

- Formatting methods of ``OptionGroupMixin`` and ``SectionMixin`` now expects
  the ``formatter`` to be a ``cloup.HelpFormatter``.
  If you used a custom ``click.HelpFormatter``, you'll need to change your code
  if you want to use this release. If you used ``click-help-colors``, keep in
  mind that the new formatter has built-in styling capabilities so you don't
  need ``click-help-colors`` anymore.

- ``OptionGroupMixin.format_option_group`` was removed.

- ``SectionMixin.format_section`` was removed.

- The class ``MultiCommand`` was removed, being useless.

- The ``OptionGroupMixin`` attribute ``align_option_groups`` is now ``None`` by default.
  Functionally, nothing changes: option groups are aligned by default.

- The ``SectionMixin`` attribute ``align_sections`` is now ``None`` by default.
  Functionally, nothing changes: subcommand sections are aligned by default.

- The ``ConstraintMixin`` attribute ``show_constraints`` is now ``None`` by default.
  Functionally, nothing changes: constraints are **not** shown by default.


Compatible changes
------------------

- Cloup now uses its own ``HelpFormatter``:

  * it supports alignment of multiple definition lists, so Cloup doesn't have to
    rely on a hack (padding) to align option groups and alike

  * it adds theming of the help page, i.e. styling of several elements of the
    help page

  * it has an additional way to format definition lists (implemented with the
    method ``write_linear_dl``) that kicks in when the available width for the
    standard 2-column format is not enough (precisely, when the width available
    for the 2nd column is below ``formatter.col2_min_width``)

  * it adds several attributes to fine-tune and customize the generated help:
    ``col1_max_width``, ``col_spacing`` and ``row_sep``

  * it fixes a couple of Click minor bugs and decides the column width of
    definition lists in a slightly smarter way that makes a better use of the
    available space.

- Added a custom ``Context`` that:

  * uses ``cloup.HelpFormatter`` as formatter class by default
  * adds a ``formatter_settings`` attributes that allows to set the default
    formatter keyword arguments (the same argument can be given to a command to
    override these defaults). You can use the static method
    ``HelpFormatter.settings`` to create such a dictionary
  * allows to set the default value for the following ``Command``/``Group`` args:

    * ``align_option_groups``,
    * ``align_sections``
    * ``show_constraints``

  * has a ``Context.setting`` static method that facilitates the creation of a
    ``context_settings`` dictionary (you get the help of your IDE).

- Added a base class ``BaseCommand`` for ``Command`` and ``Group`` that:

  - extends ``click.Command``
  - back-ports Click 8.0 class attribute ``context_class`` and set it to ``cloup.Context``
  - adds the ``formatter_settings`` argument

- Hidden option groups. An option group is hidden either if you pass
  ``hidden=True`` when you define it or if all its contained options are hidden.
  If you set ``hidden=True``, all contained options will have their ``hidden``
  attribute set to ``True`` automatically.

- Adds the conditions ``AllSet`` and ``AnySet``.

  * The ``and`` of two or more ``IsSet`` conditions returns an ``AllSet`` condition.
  * The ``or`` of two or more ``IsSet`` conditions returns an ``AnySet`` condition.

- Changed the error messages of ``all_or_none`` and ``accept_none``.

- The following Click decorators are now exported by Cloup: ``argument``,
  ``confirmation_option``, ``help_option``, ``pass_context``, ``pass_obj``,
  ``password_option`` and ``version_option``.

Docs
----
- Switch theme to ``furo``.
- Added section "Help formatting and theming".
- Improved all sections.

--------------------------------------------------------------------------------

v0.7.1 (2021-05-02)
===================
- Fixed a bug with ``&`` and ``|`` ``Predicate`` operators giving ``AttributeError``
  when used.
- Fixed the error message of ``accept_none`` which didn't include ``{param_list}``.
- Improved ``all_or_none`` error message.
- Minor docs fixes.


v0.7.0 (2021-03-24)
===================
Compatible changes
------------------

- In constraint errors, the way the parameter list is formatted has changed.
  Instead of printing a comma-separated list of single labels:

  * each parameter is printed on a 2-space indented line and
  * both the short and long name of options are printed.

  See the relevant `commit <https://github.com/janLuke/cloup/commit/0280323e481bcca2b941a49c9133b06685e4bbe1>`_.

- Minor improvements to code and docs.

--------------------------------------------------------------------------------

v0.6.1 (2021-03-01)
===================
This patch release fixes some problems in the management and releasing of
the package.

- Add a ``py.typed`` file to ship the package with type hints (PEP 561).
- Use ``setuptools-scm`` to automatically manage the version of the package
  *and* the content of the source distribution based on the git repository:

  * the source distribution now matches the git repository, with the only
    exception of ``_version.py``, which is not tracked by git; it's generated by
    ``setuptools-scm`` and included in the package;

  * tox.ini and Makefile were updated to account for the fact that ``_version.py``
    doesn't exist in the repository before installing the package.

- The new attribute ``cloup.__version_tuple__`` stores the version as a tuple
  (of *at least* 3 elements).


v0.6.0 (2021-02-28)
===================
Incompatible changes
--------------------

- Removed the deprecated ``GroupSection`` as previously announced.
  Use the new name instead: ``Section``.
- In ``Group.group()`` and ``Group.command``, the argument ``section`` was moved
  after the ``cls`` argument so that the signatures are now fully compatible with
  those of the parent class (the Liskov substitution principle is now satisfied).
  If you (wisely) passed ``section`` and ``cls`` as keyword arguments in your
  code, you don't need to change anything.

Compatible changes
------------------

- Slightly improved return type (hint) of command decorators.
- Minor refactoring of ConstraintMixin.
- Improved the documentation.

--------------------------------------------------------------------------------

v0.5.0 (2021-02-10)
===================
Requirements
------------

- Drop support to Python 3.5.

Deprecated
----------

- ``GroupSection`` was renamed as ``Section``.

Compatible changes
------------------

- Added a subpackage for defining **constraints** on parameters groups
  (including ``OptionGroup``'s).
- The code for adding support to option groups was extracted to ``OptionGroupMixin``.
- Most of the code for adding support to subcommand sections was extracted to
  ``SectionMixin``.

Project changes
---------------

- Migrated from TravisCI to GitHub Actions.

--------------------------------------------------------------------------------

v0.4.0 (2021-01-10)
===================

Requirements
------------

- This is the last release officially supporting Python 3.5.

Compatible changes
------------------

- Changed the internal (non-public) structure of the package.
- Minor code improvements.

Project changes
---------------

- New documentation (hosted by ReadTheDocs)
- Tox, TravisCI, Makefile completely rewritten.

--------------------------------------------------------------------------------

v0.3.0 (2020-03-26)
===================
Incompatible changes
--------------------
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

--------------------------------------------------------------------------------

v0.2.0 (2020-03-11)
===================
- [Feature] Add possibility of organizing subcommands of a cloup.Group in
  multiple help sections.
- Various code improvements.
- Backward incompatible change:
    - rename ``CloupCommand`` and ``CloupGroup`` resp. to just ``Command`` and ``Group``.

--------------------------------------------------------------------------------

v0.1.0 (2020-02-25)
===================
- First release on PyPI.
