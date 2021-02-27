
Constraints
===========
.. currentmodule:: cloup.constraints
.. highlight:: none


Overview
--------

A :class:`Constraint` is essentially a **validator for groups of parameters** that:

- has a textual description (:meth:`Constraint.help`)
- when unsatisfied raises an :exc:`~click.UsageError` with an appropriate error
  message that is handled and displayed by Click
- it's easily composable with other constraints using logical operators
  and you can easy change its description and/or error message
  (see `Combining and rephrasing`_).

Constraints are **well-integrated with option groups but decoupled from them.**
Indeed, you can use them to validate *any* group of parameters by providing
their (destination) names (see `Specifying parameters by name`_).

**Constraints can also be applied conditionally**, e.g. based on the value of
a parameter (see `Conditional constraints`_).

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

======================= ==========================================================
``require_all``         Requires all parameters to be set.
----------------------- ----------------------------------------------------------
``accept_none``         Requires all parameters to be unset.
----------------------- ----------------------------------------------------------
``all_or_none``         Satisfied if either all or none of the parameters are set.
----------------------- ----------------------------------------------------------
``mutually_exclusive``  A rephrased version of ``AcceptAtMost(1)``.
======================= ==========================================================

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
-----------------------

:class:`If` allows to define conditional constraints::

    If(condition, then, [else_])

- ``condition`` is either a concrete instance of :class:`~conditions.Predicate`
  or the name of a parameter; passing the name is a shortcut for ``IsSet(name)``
- ``then`` is an instance of ``Constraint``
- ``else_`` is another instance of ``Constraint`` or ``None``.

Available predicates can be imported from ``cloup.constraints`` and are:

.. autosummary::
    IsSet
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


Usage with @option_group
------------------------
As you have probably seen in the :doc:`option-groups` section, you can easily apply
a constraint to an option group by setting the ``constraint`` (keyword-only)
argument or ``@option_group`` (or ``OptionGroup``):

.. code-block:: python

    @option_group(
        'Output options',
        option('--four / --no-four', help='1st output option'),
        option('--five', help='2nd output option'),
        option('--six', help='3rd output option'),
        constraint=RequireAtLeast(1),
    )

This code produces the following help section, whose title contains the
constraint description between square brackets::

    Output options [at least 1 required]:
      --four / --no-four    1st output option
      --five TEXT           2nd output option
      --six TEXT            3rd output option


If you don't want to show the constraint description, you can use the method
:meth:`~Constraint.hidden`:

.. code-block:: python

    @option_group(
        ...
        constraint=RequireAtLeast(1).hidden(),
    )


Specifying parameters by name
-----------------------------
You can apply a constraint on any group of parameters providing their
**destination names**, i.e. the names of the function arguments they are mapped
to (by Click). For example:

=============================================== ===================
Declaration                                     Destination name
=============================================== ===================
``@option('-o')``                               ``o``
``@option('-o', '--out-path')``                 ``out_path``
``@option('-o', '--out-path', 'output_path')``  ``output_path``
=============================================== ===================

This is useful when you need to apply a constraint on a group of parameters for
which no ``OptionGroup`` is defined.

You have two (non-equivalent) options:

#. using the ``@cloup.constraint`` decorator
#. using the constraint as a function inside the command callback
   (a ``Constraint`` is indeed *callable*).

Usage with @constraint
~~~~~~~~~~~~~~~~~~~~~~
In essence, ``@cloup.constraint`` allows to include a constraint as part
of the command "metadata", which opens new possibilities with respect to just
using the constraint as a function:

- it becomes possible to document the constraints in a section of the help page;
  note that this is disabled by default and can be enabled passing
  ``show_constraints=True`` to ``@command()`` (or ``cloup.Command``);

- the sanity checks performed to detect *your* mistakes can be performed *before*
  parsing, just after the constraints applied to option groups are checked
  (see `Validation protocol`_); this is not of huge importance but a nice-to-have.

The signature is simple:

.. code-block:: python

    @constraint(constr: Constraint, params: Iterable[str])

where ``params`` is a list of parameter **destination names**; for example,
an option ``--input-file`` is mapped (by Click) to the name ``input_file``  by default.

Here's a meaningless example just to show how to use the API:

.. code-block:: python

    @command('cmd', show_constraints=True)
    @option('--opt-1')
    @option('--opt-2')
    @option('--opt-3')
    @option('--opt-4')
    @option('--opt-5')
    @constraint(mutually_exclusive, ['opt_1', 'opt_2'])
    @constraint(If('opt_1', then=RequireExactly(1)), ['opt_3', 'opt_5'])
    def cmd(opt_1, opt_2, opt_3, opt_4, opt_5):
        print('ciao')

Passing ``show_constraints=True`` as above will produce the following section at
the bottom of the command help::

    Constraints:
      {--opt-1, --opt-2}  mutually exclusive
      {--opt-3, --opt-4}  exactly 1 required if --opt-1 is set

Even in this case, you can still hide a specific constraint by calling the method
:meth:`~Constraint.hidden` on it.

Usage inside functions
~~~~~~~~~~~~~~~~~~~~~~
You may consider this option if you are not interested in documenting constraints
in the help page *and* you find it more readable than ``@constraint``.

.. code-block:: python

    from cloup.constraint import If, RequireExactly, mutually_exclusive

    # ...
    def cmd(opt_1, opt_2, opt_3, opt_4, opt_5):

        mutually_exclusive(['opt_1', 'opt_4'])

        If(Equal('opt_1', 'value'), then=RequireExactly(1))([
            'opt_2', 'opt_3'
        ])

Calling a constraint is equivalent to call its :meth:`~Constraint.check` method.

.. important::
    The ``check()`` method **needs** a ``click.Context`` to work. Nonetheless,
    you are not required to provide it explicitly because the current context is
    automatically obtained using :func:`click.get_current_context`. This works as
    long as you call ``check()`` (or the constraint itself) in places where an
    a Click context is guaranteed to be defined.

Why do you need to pass the parameter names and not their values?
That's because values are not enough to generate an error message
explaining which parameters don't satisfy the constraint. Knowing
their names, Cloup can reference both the ``Parameter`` instances
and their values in the current :class:`click.Context`.

Combining and rephrasing
------------------------
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
``'{param_list}'``, which will be replaced by a comma-separated list of
parameters.

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
producing constraints having a prettier ``__repr__`` (showed in consistency errors):

.. code-block:: python

    >>> AcceptBetween(1, 3)
    AcceptBetween(1, 3)

    >>> accept_between(1, 3)
    Rephraser(help='at least 1 required, at most 3 accepted')

These differences are unimportant in most cases, so feel free to use functions
in your code if you prefer it.

Finally, if all this is not convenient for your case, just extend ``Constraint``,
it's pretty easy. Use the code of existing constraints as a guide.


Validation protocol
-------------------

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

\*Disabling consistency checks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can safely skip this section since disabling consistency checks is a
micro-optimization likely to be completely irrelevant in practice.

Current consistency checks should not have any relevant impact on performance,
so they are enabled by default. Nonetheless, they are completely useless in
production, so I added the possibility to turn them off (globally) using the
class method :meth:`Constraint.toggle_consistency_checks`. Just because I could.

To disable them only in production, you should set an environment variable in the
system you use for development, say ``PYTHON_ENV="dev"``; then you can put the
following code in the entry-point of your program:

.. code-block:: python

    import os

    # Enable consistency checks only if PYTHON_ENV is defined and equal to 'dev'
    Constraint.toggle_consistency_checks(
        os.getenv('PYTHON_ENV') == 'dev'
    )

Have I already mentioned that this is probably not worth the effort?

Feature support
---------------

.. note::
    If you use command classes/decorators redefined by Cloup, you can skip
    this section.

To support constraints, a ``Command`` must inherit from :class:`ConstraintMixin`.
It's worth noting that ``ConstraintMixin`` integrates with ``OptionGroupMixin``
but it **doesn't** require it to work.

To use the ``@constraint`` decorator, you must currently use ``@cloup.command``
as command decorator. Using ``@click.command(..., cls=cloup.Command)`` won't
work. This may change in the future though.
