=========
Changelog
=========

..  v0.X.X (in development)
    =======================
    New features and enhancements
    -----------------------------
    Bug fixes
    ---------
    Breaking changes
    ----------------
    Deprecated
    ----------

Newer releases
==============
Release notes are now only on GitHub: https://github.com/janluke/cloup/releases.

v1.0.2 (2022-11-04)
=======================
- Skip constraints checking when passing ``--help`` to a subcommand. :issue:`129`

v1.0.1 (2022-09-22)
=======================
- Show a helpful error message when some tries to use command decorators without
  parenthesis. :pr:`128`

v1.0.0 (2022-07-17)
===================
- Drop support for Python 3.6. Python 3.6 ha reached end-of-life in Dec 2021 and
  it's not officially supported by Click 8. From https://pypistats.org/packages/cloup,
  I can see that about 37% of people are still using Python 3.6. If you can't
  upgrade, you should still be able to use Cloup by installing the ``dataclasses``
  backport package and using a compatible version of Click.

- Drop support for Click 7.

- Run tests on Python 3.10.

--------------------------------------------------------------------------------

v0.15.1 (2022-06-26)
====================

Bug fixes
---------
- Fix type of ``type`` argument of ``@option`` and ``@argument``. Specifically,
  tuple types weren't correctly described.
- Reimplement ``@argument`` and ``@option`` without calling the corresponding
  Click methods (:pr:`124`):

  - make decorators returned by ``@argument`` reusable by not relying on bugged
    Click implementation
  - remove unnecessary copy of ``**attrs`` in ``@option``.

v0.15.0 (2022-06-16)
====================
New features and enhancements
-----------------------------
- Renamed ``Argument.help_record`` to ``Argument.get_help_record``. :pr:`116`
- Fixed typos and some type annotations. :pr:`116`
- In mixins, moved call to ``super()`` at the beginning of ``__init__``. :pr:`119`.
- Made Cloup pass ``mypy --strict``. :pr:`122`

Bug fixes
---------
- The title of the default option group was "Other options" when the only other
  parameter help section was "Positional arguments". It's now "Options". :pr:`120`

Breaking changes
----------------
- Renamed ``Argument.help_record`` to ``Argument.get_help_record``.
- In mixins, moved call to ``super()`` at the beginning of ``__init__``. :pr:`119`.

--------------------------------------------------------------------------------

v0.14.0 (2022-05-09)
====================
New features and enhancements
-----------------------------
- You can show a "Positional arguments" help section by passing a non-empty
  ``help`` description for at least one of the arguments of a command/group.
  :pr:`113`
- ``cloup.Group`` now extends ``cloup.Command`` and, as a consequence, supports
  option groups and constraints. :pr:`113`
- ``GroupedOption`` is now an alias of ``cloup.Option``.
- Add the new ``params`` Click argument to ``@command`` and ``@group``
  signatures. This argument is supported only for click >= 8.1.0. See
  https://github.com/pallets/click/pull/2203.

Breaking changes
----------------
- ``BaseCommand`` was removed. This shouldn't cause any issue to anybody.
- ``cloup.Group`` extends ``cloup.Command``, similarly as ``click.Group``
  extends ``click.Command``.
- ``OptionGroupMixin.format_options`` was renamed to ``format_params``. This
  means you can't just mix it with ``click.Command`` to print help sections for
  option groups, you have to override ``format_help`` and call ``format_params``.
- The new ``format_params`` doesn't call ``super().format_commands`` as
  ``format_options`` did: that's what Click does and Cloup (reluctantly) did.
  Now, instead, ``cloup.Command`` calls ``format_params`` in ``format_help`` and
  then, for multi-commands, calls ``format_commands`` directly.
- ``ConstraintMixin.format_help`` was removed. This means you can't just mix it
  with a click.Command to make it print the "Constraints" help section, you need
  to call ``format_constraints`` explicitly in your command ``format_help``.

--------------------------------------------------------------------------------

v0.13.1 (2022-05-08)
====================
- Since version 8.1.0, Click does not normalize the command attributes ``help``,
  ``short_help`` and ``epilog`` while Cloup assumed them to be normalized as
  in previous releases. This lead to Cloup printing non-normalized help and
  epilog text when using click >= 8.1.0.

v0.13.0 (2022-02-14)
====================
- Add shortcuts for ``click.Path`` types which uses ``pathlib.Path``
  as ``path_type`` by default:
  - ``cloup.path``
  - ``cloup.dir_path`` (``file_okay=False``)
  - ``cloup.file_path`` (``dir_okay=False``)

--------------------------------------------------------------------------------

v0.12.1 (2021-10-14)
====================
- Fix: when ``OptionGroupMixin`` is mixed with ``Group``, subcommands weren't shown.

v0.12.0 (2021-09-17)
====================
- Feature: when a subcommand is mistyped, show "did you mean <subcommand>?".
- Doc fixes.

--------------------------------------------------------------------------------

v0.11.0 (2021-08-05)
====================

No major changes in this release, just refinements.

- Attributes of parametric constraints are now public. :pr:`82`
- Slightly changed the ``repr()`` of ``RequireExactly(3)``:
  from ``RequireExactly(n=3)`` to ``RequireExactly(3)``.
- Minor code refactoring.
- Docs fixes and improvements.

--------------------------------------------------------------------------------

v0.10.0 (2021-07-14)
====================

New features and enhancements
-----------------------------
- New feature: subcommand aliases. :issue:`64` :pr:`75`

- Command decorators: improvements to type hints and other changes (:pr:`67`):

  - mypy can now infer the exact type of the instantiated command based on the
    ``cls`` argument. --- Unfortunately, this required the use of ``@overload`` to
    work around a mypy limitation
  - in ``@group``, allow ``cls`` to be any ``click.Group`` --- previously it had to
    be a subclass of ``cloup.Group``
  - in ``Group.command`` and ``Group.group`` add type hints and make all arguments
    except ``name`` keyword-only. Technically this is a (minor) incompatibility
    with the ``click.Group`` superclass, but it's coherent with Cloup's
    ``@command`` and ``@group``
  - add Cloup-specific arguments to the signature of ``@command``; if the developer
    uses one of such arguments with a ``cls`` that doesn't support them, Cloup
    augments the resulting ``TypeError`` with extra information.

- Export Click types from Cloup namespace for convenience. :issue:`72`

- In dark and light themes, the epilog is now left unstyled by default. :issue:`62`

Bug fixes
---------
- ``SectionMixin.add_section`` called ``super().add_command`` rather than
  ``self.add_command``. This caused ``add_command`` in subclasses not to be
  called. :issue:`69`

- Fix ``Context.check_constraints_consistency`` not being propagated to descendant
  contexts. :issue:`74`

Breaking changes
----------------
- In ``Group.command`` and ``Group.group`` all arguments except ``name`` are now
  keyword-only.

- The ``name`` parameter/attribute of ``OptionGroup`` was renamed to ``title``.

- In ``SectionMixin`` (thus, in ``Group``), added a ``ctx: Context`` attribute
  to make_commands_help_section and format_subcommand_name to support the
  ``show_subcommand_aliases`` setting.

--------------------------------------------------------------------------------

v0.9.1 (2021-07-03)
===================
- Fixed bug: shell completion breaking because of Cloup checking constraints
  despite ``ctx.resilient_parsing=True``
- Added public attributes to ``ConstraintMixin``: ``optgroup_constraints``,
  ``param_constraints`` and ``all_constraints``.
- Cleaned up code and added other type hints (to internal code).
- Docs fixes and improvements. Fixed dark theme styling.


v0.9.0 (2021-06-30)
===================

Fixed bugs
----------
- ``Context.show_constraints`` not having effect because of wrong default for
  ``Command.show_constraint``. :issue:`49`

- ``Command`` (``OptionGroupMixin``) raising error if ``params`` is not provided.
  :issue:`58`

New features and enhancements
-----------------------------
- Add detailed type hints for ``@argument``, ``@option``, ``@command`` and ``@group``.
  This should greatly improve IDE code completion. :pr:`47`, :pr:`50`

- You can now use **constraints as decorators** (or ``@constrained_params``) to
  constrain a group of "contiguous" parameters without repeating their names
  (see :ref:`Constraints as decorators <constraints-as-decorators>`). This is
  a breaking change (see section below). :issue:`8`

- Added the ``require_any`` and ``require_one`` constraints (as aliases). :issue:`57`

- Simplify and improve the ``error`` argument of ``Rephraser``
  (see :ref:`Rephrasing constraints <rephrasing-constraints>`). :pr:`54`

- The formatter setting ``row_sep`` can now take a ``RowSepPolicy`` that decides
  whether and which row separator to use for each definition list independently,
  e.g. based on the number of definitions taking multiple lines
  (see: :ref:`Row separators <row-separators>`). :issue:`37`

- Added method ``format_subcommand_name(name, cmd)`` to ``SectionMixin`` to
  facilitate it combination with other Click extensions that override
  ``format_commands()``. :issue:`59`

- ``@option_group`` and ``Section`` now show a better error message when one forgets
  to provide the name/title as first argument.

- Fixed/improved some type hints and added others.

Breaking changes
----------------
- Calling a constraint -- previously a shortcut to the :meth:`~Constraint.check`
  method -- now returns a decorator. Use the method :meth:`Constraint.check`
  to check a constraint inside a function. :issue:`8`

- The semantics of ``row_sep`` changed. Now, it defaults to ``None`` and must
  not end with ``\n``, since the formatter writes a newline automatically
  after it. So, ``row_sep=""`` now corresponds to an empty line between rows.
  :issue:`41`

- In ``@command`` and ``@group`` make all arguments but ``name`` keyword-only.
  :issue:`46`

- In ``Context.settings`` and ``HelpFormatter.settings``, use a ``MISSING``
  constant instead of ``None`` as a flag for "empty" arguments. :issue:`40`

- ``Constraint.toggle_consistency_checks`` was replaced with a ``Context``
  setting called ``check_constraints_consistency``. :issue:`33`

- ``ConstraintViolated`` requires more parameters now. :pr:`54`

Docs
----
- Restyling to improve readability: increased font size and vertical spacing,
  decreased line width. Restyled the table of contents on the right side. Ecc.
- Reorganized and rewrote several parts.

--------------------------------------------------------------------------------

v0.8.1-2 (2021-05-25)
=====================

(I had to release v0.8.2 just after v0.8.1 to fix a docs issue)

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


New features and enhancements
-----------------------------
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

Breaking changes
----------------
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
New features and enhancements
-----------------------------
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

New features and enhancements
-----------------------------
- Slightly improved return type (hint) of command decorators.
- Minor refactoring of ConstraintMixin.
- Improved the documentation.

Breaking changes
----------------
- Removed the deprecated ``GroupSection`` as previously announced.
  Use the new name instead: ``Section``.
- In ``Group.group()`` and ``Group.command``, the argument ``section`` was moved
  after the ``cls`` argument so that the signatures are now fully compatible with
  those of the parent class (the Liskov substitution principle is now satisfied).
  If you (wisely) passed ``section`` and ``cls`` as keyword arguments in your
  code, you don't need to change anything.

--------------------------------------------------------------------------------

v0.5.0 (2021-02-10)
===================
Requirements
------------
- Drop support to Python 3.5.

New features and enhancements
-----------------------------
- Added a subpackage for defining **constraints** on parameters groups
  (including ``OptionGroup``'s).
- The code for adding support to option groups was extracted to ``OptionGroupMixin``.
- Most of the code for adding support to subcommand sections was extracted to
  ``SectionMixin``.

Deprecated
----------
- ``GroupSection`` was renamed as ``Section``.

Project changes
---------------
- Migrated from TravisCI to GitHub Actions.

--------------------------------------------------------------------------------

v0.4.0 (2021-01-10)
===================

Requirements
------------
- This is the last release officially supporting Python 3.5.

New features and enhancements
-----------------------------
- Changed the internal (non-public) structure of the package.
- Minor code improvements.

Project changes
---------------
- New documentation (hosted by ReadTheDocs)
- Tox, TravisCI, Makefile completely rewritten.

--------------------------------------------------------------------------------

v0.3.0 (2020-03-26)
===================
Breaking changes
----------------
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
