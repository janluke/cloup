
.. currentmodule:: cloup.constraints
.. highlight:: none

Constraints
===========

Overview
--------
A :class:`Constraint` is essentially a validator for groups of parameters that
has a textual description (:meth:`Constraint.help`) and when unsatisfied raises
an :exc:`~click.UsageError` with an appropriate error message, which is handled
and displayed by Click.

Constraints are well-integrated with option groups but decoupled from them.
Indeed, you can use them to constrain groups of any kind of parameters,
including positional arguments.

Constraints can also be applied conditionally (see `Conditional constraints`_).

There are three ways to define a constraint, each covering a different scenario:

.. list-table::
    :widths: 10 10
    :header-rows: 1

    * - Scenario
      - Method
    * - I want to apply a constraint to *all* options of an ``@option_group``.
      - Use the ``constraint`` parameter of ``@option_group``.
        See `Integration with @option_group`_.
    * - I want to constrain a group of *nearby* parameters (eventually a subgroup
        of an option group) without assigning them their own help section.
      - Use the constraint itself as a decorator or, equivalently, the
        ``@constrained_params`` decorator.
        See `Using constraints as decorators`_. (\*)
    * - As previous scenario, but the parameters are not nearby so you can't
        nest them inside another decorator.
      - Use the ``@constraint`` decorator and list those parameters by name.
        See `The @constraint decorator`_.

(\*) These are just syntactic sugar on top of ``@constraint`` which save you to
list parameters by name (thus avoiding replication).


Implemented constraints
-----------------------
``cloup`` uses the following convention:

- **parametric** constraints are *subclasses* of ``Constraint`` and so they are camel-cased;
- **non-parametric** constraints are *instances* of ``Constraint`` and so they are
  snake-cased.

Parametric constraints
~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    RequireExactly
    RequireAtLeast
    AcceptAtMost
    AcceptBetween

Non-parametric constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~

=========================== ============================================================
:data:`require_all`          Requires all parameters to be set.
--------------------------- ------------------------------------------------------------
:data:`accept_none`          Requires all parameters to be unset.
--------------------------- ------------------------------------------------------------
:data:`all_or_none`          Satisfied if either all or none of the parameters are set.
--------------------------- ------------------------------------------------------------
:data:`mutually_exclusive`   A rephrased version of ``AcceptAtMost(1)``.
=========================== ============================================================

When is a parameter considered to be "set"?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Cloup uses the following policy:

- if the value is ``None``, the parameter is unset;
- a parameter that takes multiple values is set if at least one value is provided;
- a boolean **flag** is set only if ``True`` (since the default value is ``False``);
- a boolean **non-flag** option is set if not ``None``, even if it's ``False``.

.. admonition:: Possible sources of a value

    Cloup validates the values available in ``Context.params`` dictionary after
    parsing. The source of an option value can be (from higher to lowest priority):

    - the command-line user input
    - an environment variable (if you enabled it)
    - `Context.default_map <https://click.palletsprojects.com/en/5.x/commands/#overriding-defaults>`_
    - the default value of the option (if defined).

Conditional constraints
~~~~~~~~~~~~~~~~~~~~~~~

:class:`If` allows to define conditional constraints::

    If(condition, then, [else_])

- ``condition`` can be;

  - a concrete instance of :class:`~conditions.Predicate`
  - a parameter name; this is a shortcut for ``IsSet(param_name)``
  - a list/tuple of parameter names; this is a shortcut for ``AllSet(*param_names)``.

- ``then`` is the constraint checked when the condition is true.
- ``else_`` is an optional constraint checked when the condition is false.

Available predicates can be imported from ``cloup.constraints`` and are:

.. autosummary::
    IsSet
    AllSet
    AnySet
    Equal

For example:

.. code-block:: python

    from cloup.constraints import (
        If, RequireAtLeast, require_all, accept_none,
        IsSet, Equal
    )

    # If parameter with name "param" is set,
    # then require all parameters, else forbid them all
    If('param', then=require_all, else_=accept_none)

    # Equivalent to:
    If(IsSet('param'), then=require_all, else_=accept_none)

    # If "arg" and "opt" are both set, then require exactly 1 param
    If(['arg', 'opt'], then=RequireExactly(1))

    # Another example... of course the else branch is optional
    If(Equal('param', 'value'), then=RequireAtLeast(1))

Predicates have an associated ``description`` and can be composed
with the logical operators

- ``~`` (not),
- ``&`` (and),
- ``|`` (or).

For example:

.. code-block:: python

    predicate = ~IsSet('foo') & Equal('bar', 'value')
    # --foo is not set and --bar="value"


The @constraint decorator
------------------------------------------
Using the :func:`cloup.constraint` decorator, you can apply a constraint to any
group of parameters (both arguments and options) providing their
**destination names**, i.e. the names of the function arguments they are mapped
to (by Click). For example:

=============================================== ===================
Declaration                                     Name
=============================================== ===================
``@option('-o')``                               ``o``
``@option('-o', '--out-path')``                 ``out_path``
``@option('-o', '--out-path', 'output_path')``  ``output_path``
=============================================== ===================

Here's a meaningless example just to show how to use the API:

.. code-block:: python

    @command('cmd', show_constraints=True)
    @option('--one')
    @option('--two')
    @option('--three')
    @option('--four')
    @constraint(
        mutually_exclusive, ['one', 'two']
    )
    @constraint(
        If('one', then=RequireExactly(1)), ['three', 'four']
    )
    def cmd(one, two, three, four):
        print('ciao')

.. _show-constraints:

If you set the ``command`` parameter ``show_constraints`` to ``True``,
the following section is shown at the bottom of the command help::

    Constraints:
      {--one, --two}     mutually exclusive
      {--three, --four}  exactly 1 required if --one is set

Even in this case, you can still hide a specific constraint by using the method
:meth:`~Constraint.hidden`.

Note that ``show_constraint`` can also be set in the ``context_settings`` of
your root command. Of course, the context setting can be overridden by each
individual command.


Using constraints as decorators
-------------------------------
``@constraint`` is powerful but has some drawbacks:

- it requires to replicate (once again) the name of the constrained parameters;
- it doesn't visually group the involved parameters together in the same way
  ``@option_group`` does (with nesting).

Even though ``@constraint`` is unavoidable in some cases, it can be avoided when
the parameters to constrain are "contiguous", which is often the case.
In such case, you can use your constraint as a decorator:

.. code-block:: python

    @mutually_exclusive(
        option('--one'),
        option('--two'),
        option('--three'),
    )

    # WARNING: this is not valid in Python < 3.9 because of the double call
    @RequireAtLeast(1)(
        option('--one'),
        option('--two'),
        option('--three'),
    )

.. attention::
    In Python < 3.9, the expressions on the right of `@` is required to be a
    "dotted name, optionally followed by a single call"
    (see `PEP 614 <https://www.python.org/dev/peps/pep-0614/#motivation>`_),
    meaning that ``@RequireAtLeast(1)(...)`` **won't work**, since it makes
    two calls. To make it work, you first need to assign the constraint to
    a variable.

Equivalently, you can use the decorator :func:`cloup.constrained_params`:

.. code-block:: python

    @constrained_params(
        RequireAtLeast(1),
        option('--one'),
        option('--two'),
        option('--three'),
    )

Both forms desugar to the following:

.. code-block:: python

    @constraint(RequireAtLeast(1), ['one', 'two', 'three'])
    @option('--one')
    @option('--two')
    @option('--three')

.. _option-group-and-constraints:

Integration with @option_group
------------------------------
As you have probably seen in the :doc:`option-groups` section, you can easily
apply a constraint to an option group by setting the ``constraint`` argument of
``@option_group`` (or ``OptionGroup``):

.. code-block:: python

    @option_group(
        'Option group title',
        option('-o', '--one', help='an option'),
        option('-t', '--two', help='a second option'),
        option('--three', help='a third option'),
        constraint=RequireAtLeast(1),
    )

This code produces the following help section with the constraint description
between square brackets on the right of the option group name::

    Option group title: [at least 1 required]
      -o, --one TEXT  an option
      -t, --two TEXT  a second option
      --three TEXT    a third option

If the constraint description doesn't fit into the section heading line, it is
printed on the next line::

    Option group title:
      [this is a very long constraint description that doesn't fit into the heading line]
      -o, --one TEXT  an option
      -t, --two TEXT  a second option
      --three TEXT    a third option

If the constraint is violated, the following error is shown::

    Error: at least 1 of the following parameters must be set:
      --one (-o)
      --two (-t)
      --three

You can customize both the help description and the error message of a constraint
using the method :meth:`Constraint.rephrased` (see `Combining and rephrasing constraints`_
for more).

If you simply want to hide the constraint description in the help, you can use
the method :meth:`Constraint.hidden`:

.. code-block:: python

    @option_group(
        ...
        constraint=RequireAtLeast(1).hidden(),
    )

Constraining part of an option group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can use constraints as decorators even inside ``@option_group`` to constrain
one or multiple subgroups:

.. code-block:: python

    @option_group(
        "Number options",
        RequireAtLeast(1)(
            option('--one'),
            option('--two')
        ),
        option('--three')
    )

Note that in this case, the problem described in the attention box above with
decorators in Python < 3.9 does not exist since we are not using ``@``.

The above code is equivalent to:

.. code-block:: python

    @option_group(
        "Number options",
        option('--one'),
        option('--two')
        option('--three')
    )
    @constraint(RequireAtLeast(1), ['one', 'two'])


Combining and rephrasing constraints
------------------------------------
The available constraints should cover 99% of use cases but if you want to
combine them or even just change their description and/or the error message,
you can do that with very little code:

- **to combine constraints** you can use the logical operators ``&`` and ``|``;
  both their validation logic and their description will be combined
- **to edit the description and/or the error message** of a constraint,
  you can use the method :meth:`~Constraint.rephrased`, which wraps the original
  constraint with a :class:`Rephraser`
- **to define a new constraint type wrapping another** constraint with
  minimal boilerplate, you can extend :class:`~WrapperConstraint`.

Let's see some examples from Cloup itself.

.. code-block:: python

    all_or_none = (require_all | accept_none).rephrased(
        help='provide all or none',
        error='either all or none of the following parameters must be set:\n{param_list}',
    )

``rephrased()`` requires at least one argument between ``help`` and ``error``.
When rephrasing an error, you can pass a format string containing
``'{param_list}'``, which will be replaced by a nicely formatted 2-space indented
list of parameter names (one line per parameter).

Let's see how you can define a new parametric constraint now:

.. code-block:: python

    # Option 1: use WrapperConstraint.
    # WrapperConstraint is useful for defining a new constraint type
    # It delegates all methods to the wrapped constraint so you can
    # override only the methods you need to override.
    class AcceptBetween(WrapperConstraint):
        def __init__(self, min: int, max: int):
            # [...]
            self._min = min
            self._max = max
            # the min and max kwargs will be used for the __repr__
            super().__init__(RequireAtLeast(min) & AcceptAtMost(max), min=min, max=max)

        def help(self, ctx: Context) -> str:
            return f'at least {self._min} required, at most {self._max} accepted'

    # Option 2: use a function.
    def accept_between(min, max):
       return (RequireAtLeast(min) & AcceptAtMost(max)).rephrased(
           help=f'at least {min} required, at most {max} accepted'
       )

Cloup uses ``WrapperConstraint`` internally to stick to the convention described
in `Implemented constraints`_ and because it has some minor advantages like
producing constraints having a prettier ``__repr__`` (shown in consistency errors):

.. code-block:: python

    >>> AcceptBetween(1, 3)
    AcceptBetween(1, 3)

    >>> accept_between(1, 3)
    Rephraser(help='at least 1 required, at most 3 accepted')

These differences are unimportant in most cases, so feel free to use functions
in your code if you prefer it.

Finally, if all this is not convenient for your case, just extend ``Constraint``,
it's pretty easy. Use the code of existing constraints as a guide.

\*Validation protocol
---------------------

A constraint performs two types of checks and there's a method for each type:

- :meth:`~Constraint.check_consistency` – performs sanity checks meant to detect
  mistakes of the developer; as such, they are performed *before* argument
  parsing (when possible); for example, if you try to apply a
  ``mutually_exclusive`` constraint to an option group containing multiple
  required options, this method will raise ``UnsatisfiableConstraint``

- :meth:`~Constraint.check_values` – performs user input validation and,
  when unsatisfied, raises a ``ConstraintViolated`` error with an appropriate
  message; ``ConstrainedViolated`` is a subclass of ``click.UsageError`` and,
  as such, is handled by Click itself by showing the command usage and the
  error message.

Using a constraint as a function is equivalent to call the method
:meth:`~Constraint.check`, which performs (by default) both kind of checks,
unless consistency checks are disabled (see below).

When you add constraints through ``@option_group``, ``OptionGroup`` and
``@constraint``, this is what happens:

- constraints are checked for consistency *before* parsing
- input is parsed and processed; all values are stored by Click in the ``Context``
  object, precisely in ``ctx.params``
- constraints validate the parameter values.

In all cases, constraints applied to option groups are checked before those
added through ``@constraint``.

If you use a constraint inside a callback, of course, consistency checks can't
be performed before parsing. All checks are performed together after parsing.

Disabling consistency checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can safely skip this section since disabling consistency checks is a
micro-optimization likely to be completely irrelevant in practice.

Current consistency checks should not have any relevant impact on performance,
so they are enabled by default. Nonetheless, they are completely useless in
production, so I added the possibility to turn them off (globally) passing
``check_constraints_consistency=False`` as part of your ``context_settings``.
Just because I could.

To disable them only in production, you should set an environment variable in
your development machine, say ``PYTHON_ENV="dev"``; then you can put the
following code at the entry-point of your program:

.. code-block:: python

    import os
    from cloup import Context

    SETTINGS = Context.setting(
        check_constraints_consistency=(os.getenv('PYTHON_ENV') == 'dev')
        # ... other settings ...
    )

    @group(context_settings=SETTINGS)
    # ...
    def main(...):
        ...

Have I already mentioned that this is probably not worth the effort?

\*Feature support
-----------------

.. note::
    If you use command classes/decorators redefined by Cloup, you can skip
    this section.

To support constraints, a ``Command`` must inherit from :class:`ConstraintMixin`.
It's worth noting that ``ConstraintMixin`` integrates with ``OptionGroupMixin``
but it **doesn't** require it to work.

To use the ``@constraint`` decorator, you must currently use ``@cloup.command``
as command decorator. Using ``@click.command(..., cls=cloup.Command)`` won't
work. This may change in the future though.
