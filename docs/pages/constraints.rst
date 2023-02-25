
.. currentmodule:: cloup.constraints
.. highlight:: none

Constraints
===========

Overview
--------
A :class:`Constraint` is essentially a validator for groups of parameters.
When unsatisfied, a constraint raises a :exc:`click.UsageError` with an
appropriate error message, which is handled and displayed by Click.

Each constraint also has an associated description (:meth:`Constraint.help`)
that can optionally be shown in the ``--help`` of a command.
You can easily override both the help description and the error message if you
want (see `Rephrasing constraints`_).

Constraints can be combined with logical operators (see `Defining new constraints`_)
and can also be applied conditionally (see `Conditional constraints`_).


Implemented constraints
-----------------------

Parametric constraints
~~~~~~~~~~~~~~~~~~~~~~
Parametric constraints are *subclasses* of ``Constraint`` and so they are
camel-cased;

.. autosummary::
    RequireExactly
    RequireAtLeast
    AcceptAtMost
    AcceptBetween

Non-parametric constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~
Non-parametric constraints are *instances* of ``Constraint`` and so they are
snake-cased (``like_this``). Most of these are instances of parametric constraints
or (rephrased) combinations of them.

=========================== ============================================================
:data:`accept_none`          Requires all parameters to be unset.
--------------------------- ------------------------------------------------------------
:data:`all_or_none`          Satisfied if either all or none of the parameters are set.
--------------------------- ------------------------------------------------------------
:data:`mutually_exclusive`   A rephrased version of ``AcceptAtMost(1)``.
--------------------------- ------------------------------------------------------------
:data:`require_all`          Requires all parameters to be set.
--------------------------- ------------------------------------------------------------
:data:`require_any`          Alias for ``RequireAtLeast(1)``.
--------------------------- ------------------------------------------------------------
:data:`require_one`          Alias for ``RequireExactly(1)``.
=========================== ============================================================

When is a parameter considered "set"?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Basically, Cloup considers a parameter to be "set" when its value differs from
the one assigned by Click when the parameter is not provided neither by the
CLI user nor by the developer.

.. list-table::
    :header-rows: 1
    :widths: 10 7 10 10
    :align: center

    * - Param type
      - Click default
      - It's set if
      - Note
    * - string
      - ``None``
      - ``value is not None``
      - even if empty
    * - number
      - ``None``
      - ``value is not None``
      - even if zero
    * - boolean non-flag
      - ``None``
      - ``value is not None``
      - even if ``False``
    * - boolean flag
      - ``False``
      - ``value is True``
      -
    * - tuple
      - ``()``
      - ``len(value) > 0``
      -

In the future, this policy may become configurable at the context and parameter
level.

Conditional constraints
~~~~~~~~~~~~~~~~~~~~~~~

:class:`If` allows you to define conditional constraints::

    If(condition, then, [else_])

- **condition** -- can be:

  - a concrete instance of :class:`~conditions.Predicate`
  - a parameter name; this is a shortcut for ``IsSet(param_name)``
  - a list/tuple of parameter names; this is a shortcut for ``AllSet(*param_names)``.

- **then** -- the constraint checked when the condition is true.
- **else_** -- an optional constraint checked when the condition is false.

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

Predicates have an associated ``description`` and can be composed with the
logical operators ``&`` (and), ``|`` (or) and ``~`` (not). For example:

.. code-block:: python

    predicate = ~IsSet('foo') & Equal('bar', 'value')
    # --foo is not set and --bar="value"


Applying constraints
--------------------

Constraints are well-integrated with option groups but decoupled from them:
you can apply them to any group of parameters, eventually including positional
arguments.

There are three ways to apply a constraint:

1. setting the parameter ``constraint`` of ``@option_group`` (or ``OptionGroup``)
2. using the ``@constraint`` decorator and specifying parameters by name
3. using the constraint as a decorator that takes parameter decorators as
   arguments (similarly to ``@option_groups``, but supporting ``argument`` too);
   this is just convenient *syntax sugar* on top of ``@constraint`` that can be
   used in some circumstances.

As you'll see, Cloup handles slightly differently the constraints applied to
option groups, but only in relation to the ``--help`` output.

Usage with @option_group
~~~~~~~~~~~~~~~~~~~~~~~~
As you have probably seen in the :doc:`option-groups` chapter, you can easily
apply a constraint to an option group by setting the ``constraint`` argument of
``@option_group`` (or ``OptionGroup``):

.. code-block:: python
    :emphasize-lines: 6

    @option_group(
        'Option group title',
        option('-o', '--one', help='an option'),
        option('-t', '--two', help='a second option'),
        option('--three', help='a third option'),
        constraint=RequireAtLeast(1),
    )

This code produces the following help section with the constraint description
between square brackets on the right of the option group title::

    Option group title: [at least 1 required]
      -o, --one TEXT  an option
      -t, --two TEXT  a second option
      --three TEXT    a third option

If the constraint description doesn't fit into the section heading line, it is
printed on the next line::

    Option group title:
      [this is a long description that doesn't fit into the title line]
      -o, --one TEXT  an option
      -t, --two TEXT  a second option
      --three TEXT    a third option

If the constraint is violated, the following error is shown::

    Error: at least 1 of the following parameters must be set:
      --one (-o)
      --two (-t)
      --three

You can customize both the help description and the error message of a constraint
using the method :meth:`Constraint.rephrased` (see `Rephrasing constraints`_).

If you simply want to hide the constraint description in the help, you can use
the method :meth:`Constraint.hidden`:

.. code-block:: python

    @option_group(
        ...
        constraint=RequireAtLeast(1).hidden(),
    )


The ``@constraint`` decorator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using the :func:`cloup.constraint` decorator, you can apply a constraint to any
group of parameters (arguments and options) providing their **destination names**,
i.e. the names of the function arguments they are mapped to (by Click).
For example:

=============================================== ===================
Declaration                                     Name
=============================================== ===================
``@option('-o')``                               ``o``
``@option('-o', '--out-path')``                 ``out_path``
``@option('-o', '--out-path', 'output_path')``  ``output_path``
=============================================== ===================

Here's a meaningless example just to show how to use the API:

.. code-block:: python

    from cloup import argument, command, constraint, option
    from cloup.constraints import If, RequireExactly, mutually_exclusive

    @command('cmd', show_constraints=True)
    @argument('arg', required=False)
    @option('--one')
    @option('--two')
    @option('--three')
    @option('--four')
    @constraint(
        mutually_exclusive, ['arg', 'one', 'two']
    )
    @constraint(
        If('one', then=RequireExactly(1)), ['three', 'four']
    )
    def cmd(arg, one, two, three, four):
        print('ciao')

.. _show-constraints:

If you set the ``command`` parameter ``show_constraints`` to ``True``,
the following section is shown at the bottom of the command help::

    Constraints:
      {ARG, --one, --two}  mutually exclusive
      {--three, --four}    exactly 1 required if --one is set

Even in this case, you can still hide a specific constraint by using the method
:meth:`~Constraint.hidden`.

Note that ``show_constraint`` can also be set in the ``context_settings`` of
your root command. Of course, the context setting can be overridden by each
individual command.

.. _constraints-as-decorators:

Constraints as decorators
~~~~~~~~~~~~~~~~~~~~~~~~~
``@constraint`` is powerful but has some drawbacks:

- it requires to replicate (once again) the name of the constrained parameters;
- it doesn't visually group the involved parameters with nesting
  (as ``@option_group`` does with options).

As an answer to these issues, Cloup introduced the possibility to use
constraints themselves as decorators, with an usage similar to that of
``@option_group``.
However, note that there are cases when ``@constraint`` is your only option.

This feature is just a layer of syntax sugar on top of ``@constraint``. The
following:

.. code-block:: python

    @mutually_exclusive(
        option('--one'),
        option('--two'),
        option('--three'),
    )

is equivalent to:

.. code-block:: python

    @option('--one')
    @option('--two')
    @option('--three')
    @constraint(mutually_exclusive, ['one', 'two', 'three'])

.. admonition:: Syntax limitation in Python < 3.9
    :name: attention-python-decorators
    :class: attention

    In Python < 3.9, the expression on the right of the operator ``@``
    is required to be a "dotted name, optionally followed by a single call"
    (see `PEP 614 <https://peps.python.org/pep-0614/#motivation>`_).
    This means that you can't instantiate a parametric constraint on the right
    of ``@``, because the resultant expressions would make two calls, e.g.:

    .. code-block:: python

        # This is a syntax error in Python < 3.9
        @RequireExactly(2)(  # 1st call to instantiate the constraint
            ...              # 2nd call to apply the constraint
        )

    To work around this syntax limitation you can assign your constraint to a
    variable before using it as a decorator:

    .. code-block:: python

        require_two = RequireExactly(2)   # somewhere in the code

        @require_two(
            option('--one'),
            option('--two'),
            option('--three'),
        )

    or, in alternative, you can use the ``@constrained_params`` decorator
    described below.

The ``@constrained_params`` decorator may turn useful to work around the just
described syntax limitation in Python < 3.9 or simply when your constraint is
long/complex enough that it'd be weird to use it as a decorator:

.. code-block:: python

    @constrained_params(
        RequireAtLeast(1),
        option('--one'),
        option('--two'),
        option('--three'),
    )

.. _constraint-inside-option-group:

You can use constraints as decorators even inside ``@option_group`` to constrain
one or multiple subgroups:

.. code-block:: python
    :emphasize-lines: 3-6

    @option_group(
        "Number options",
        RequireAtLeast(1)(
            option('--one'),
            option('--two')
        ),
        option('--three')
    )

    # equivalent to:

    @option_group(
        "Number options",
        option('--one'),
        option('--two')
        option('--three')
    )
    @constraint(RequireAtLeast(1), ['one', 'two'])

Note that the syntax limitation affecting Python < 3.9 described in the
:ref:`attention box <attention-python-decorators>` above does not apply in this case
since we are not using ``@`` here.

.. _rephrasing-constraints:

Rephrasing constraints
----------------------
You can override the help description and/or the error message of a constraint
using the :meth:`~Constraint.rephrased` method. It takes two arguments:

- **help** -- if provided, overrides the help description. It can be:

  - a string
  - a function ``(ctx: Context, constr: Constraint) -> str``

  If you want to hide this constraint from the help, pass ``help=""`` or use
  the method :meth:`~Constraint.hidden`.

- **error** -- if provided, overrides the error message. It can be:

  - a string, eventually a ``format`` string whose fields are stored and
    documented as attributes in :class:`ErrorFmt`.

  - a function ``(err: ConstraintViolated) -> str``
    where :exc:`ConstraintViolated` is an exception object that fully describes
    the violation of a constraint, including fields like ``ctx``, ``constraint``
    and ``params``.

An example from Cloup
~~~~~~~~~~~~~~~~~~~~~
Cloup itself makes use of rephrasing a lot for defining non-parametric constraints,
for example:

.. code-block:: python

    mutually_exclusive = AcceptAtMost(1).rephrased(
        help='mutually exclusive',
        error=f'the following parameters are mutually exclusive:\n'
              f'{ErrorFmt.param_list}'
    )

Example: adding extra info to the original error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sometimes you just want to add extra info before or after the original error
message. In that case, you can either pass a function or using ``ErrorFmt.error``:

.. code-block:: python

    # Using function (err: ConstraintViolated) -> str
    mutually_exclusive.rephrased(
        error=lambda err: f'{err}\n'
                          f'Use --renderer, the other options are deprecated.
    )

    # Using ErrorFmt.error
    from cloup.constraint import ErrorFmt

    mutually_exclusive.rephrased(
        error=f'{ErrorFmt.error}\n'
              f'Use --renderer, the other options are deprecated.
    )


Defining new constraints
------------------------
The available constraints should cover 99% of use cases but if you need it, it's
very easy to define new ones. Here are your options:

- you can use the **logical operators** ``&`` and ``|`` to combine existing
  constraints and then eventually:

  - use the ``rephrased`` method described in the previous section

  - or subclass :class:`~WrapperConstraint` if you want to define a new
    parametric ``Constraint`` class wrapping the result

- just subclass ``Constraint``; look at existing implementations for guidance.

Example 1: logical operator + rephrasing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This is how Cloup defines ``all_or_none`` (this example may be out-of-date):

.. code-block:: python

    all_or_none = (require_all | accept_none).rephrased(
        help='provide all or none',
        error=f'the following parameters must be provided all together '
              f'(or none should be provided):\n'
              f'{ErrorFmt.param_list}',
    )

Example 2: defining a new parametric constraint
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Option 1 -- Just use a function.*

.. code-block:: python

    def accept_between(min, max):
       return (RequireAtLeast(min) & AcceptAtMost(max)).rephrased(
           help=f'at least {min} required, at most {max} accepted'
       )

    >>> accept_between(1, 3)
    Rephraser(help='at least 1 required, at most 3 accepted')

*Option 2 -- WrapperConstraint.* This is useful when you want to define a new
constraint type. ``WrapperConstraint`` delegates all methods to the wrapped
constraint so you can override only the methods you need to override.

.. code-block:: python

    class AcceptBetween(WrapperConstraint):
        def __init__(self, min: int, max: int):
            # [...]
            self._min = min
            self._max = max
            # whatever you pass as **kwargs is used in the __repr__
            super().__init__(
                RequireAtLeast(min) & AcceptAtMost(max),
                min=min, max=max,  # <= included in the __repr__
            )

        def help(self, ctx: Context) -> str:
            return f'at least {self._min} required, ' \
                   f'at most {self._max} accepted'


    >>> AcceptBetween(1, 3)
    AcceptBetween(1, 3)


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
