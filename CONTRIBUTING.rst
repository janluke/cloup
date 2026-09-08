Contributing
============

Thank you for considering a contribution to Cloup.

Getting started
---------------

Please discuss a proposed change before opening a pull request:

1. Search the `issue tracker <https://github.com/janLuke/cloup/issues>`_ for an
   existing report or proposal.
2. Open an issue describing the problem, the desired behavior, and your proposed
   approach.
3. Wait for a maintainer to confirm that the change is appropriate and agree on
   its scope.
4. If the maintainer agrees, create a branch, implement the change, and open a
   pull request linked to the issue.

Starting with an issue avoids duplicated work and gives maintainers and contributors
a place to settle API and compatibility decisions before code is written.

Development
-----------

Prerequisites
~~~~~~~~~~~~~

Cloup uses `Hatch <https://hatch.pypa.io/latest/>`_ for isolated Python
environments and `Task <https://taskfile.dev/>`_ as its project command interface.
Install both as isolated tools:

.. code-block:: console

    $ pipx install hatch
    $ pipx install "go-task-bin>=3.46.1"

The equivalent UV commands are:

.. code-block:: console

    $ uv tool install hatch
    $ uv tool install "go-task-bin>=3.46.1"

``go-task-bin`` is an unofficial Python package that distributes the Task binary.
See Task's `official installation guide <https://taskfile.dev/docs/installation>`_
for the other supported installation methods.

Hatch can install and manage the required Python interpreters, so a separate tool
such as pyenv is not required.
It creates environments automatically when their commands are first used.
To store them under ``.hatch/`` in the repository instead of Hatch's global data
directory, run:

.. code-block:: console

    $ hatch config set dirs.env.virtual .hatch

Set up the development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone your fork and enter the repository:

.. code-block:: console

    $ git clone https://github.com/<your-username>/cloup.git
    $ cd cloup

Create the ``dev`` environment with Python 3.10 and print its location:

.. code-block:: console

    $ task env

Select the reported Python interpreter in your IDE.
The environment contains Cloup in editable mode together with the test, coverage,
and typing dependencies, so it can run tests and type checks directly from the IDE.

Run ``task --list`` to see all available project commands.

Using Task
~~~~~~~~~~

Invoke one project task by name, for example:

.. code-block:: console

    $ task lint

When several task names are provided on the command line, Task runs them
sequentially by default.
Use ``--parallel`` to run independent requested tasks concurrently:

.. code-block:: console

    $ task --parallel lint docs

Dependencies declared by a single task run concurrently by default, so aggregate
commands such as ``task test:all`` and ``task qa:all`` need no ``--parallel`` flag.
Use ``--failfast`` when one failure should cancel the other running tasks:

.. code-block:: console

    $ task --failfast qa:all

The project does not impose a concurrency limit.
Set one for a particular run with ``task --concurrency N COMMAND`` or the
``TASK_CONCURRENCY`` environment variable.
Parallel output is prefixed with the task that produced it.

Code quality
~~~~~~~~~~~~

Use the following commands while developing:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Command
     - Purpose
   * - ``task check``
     - Lint the code and check its formatting style.
   * - ``task fix``
     - Lint in fix mode and format the code.
   * - ``task lint [-- --fix]``
     - Lint the code with Ruff, optionally fixing violations.
   * - ``task format``
     - Format the code with Ruff.
   * - ``task typing``
     - Type-check the code in the development environment.
   * - ``task typing:all``
     - Type-check in every Python and Click compatibility environment.

Ruff enforces Pyflakes rules, stable non-formatting pycodestyle rules, and warnings.
Whitespace and hard line-length rules that overlap with ``ruff format`` are left to
the formatter, which uses the existing 90-character target. In particular, the
former ``E241`` and ``E251`` exceptions are no longer needed, ``W191`` is omitted
because it conflicts with the formatter, and Ruff does not implement the obsolete
``W503`` rule.

Testing
~~~~~~~

The primary development environment and every test environment expose the same test
and typing scripts.
The test matrix covers every supported Python version with the latest compatible
Click release, plus older supported Click release lines on the latest Python.
This ensures that type checking observes the same dependencies and standard library
as the corresponding test run.

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Command
     - Purpose
   * - ``task test``
     - Run tests with the development environment.
   * - ``task test:all``
     - Run every Python and Click compatibility environment in parallel.
   * - ``task test-envs:upgrade-click``
     - Upgrade Click to the latest release allowed by each test environment.
   * - ``task cov``
     - Run tests in the development environment and generate terminal and HTML
       coverage reports.
   * - ``task cov:all``
     - Collect coverage from every test environment in parallel and combine the
       results.

Use ``--`` before arguments that should be forwarded to pytest.
For example, stop after the first failure with:

.. code-block:: console

    $ task test -- -x

For example, run the full test matrix sequentially with:

.. code-block:: console

    $ task --concurrency 1 test:all

Quality assurance workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The aggregate tasks are the recommended checks before submitting changes:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Command
     - Purpose
   * - ``task qa``
     - Run lint and formatting checks first, then type checking, tests, and
       documentation using the primary environments.
   * - ``task qa:all``
     - Run lint, formatting, and documentation checks plus typing and tests in every
       test environment.

Use ``task qa`` during routine development and ``task qa:all`` before opening or
updating a pull request.

For contiguous, failure-focused logs, use Task's grouped output:

.. code-block:: console

    $ task --output group --output-group-error-only qa:all

An `open Task pull request <https://github.com/go-task/task/pull/3015>`_ from
Cloup's maintainer proposes a built-in ``task --tui`` interface.
Besides launching tasks, it executes their task graph inside the TUI, gives every
task invocation a separately inspectable output pane, and can copy or save an
individual task's output—or save all outputs into separate files.
The feature is not part of a released Task version yet, and its interface may change
while the pull request is under review.

.. image:: https://github.com/user-attachments/assets/07e4d5d1-61aa-4554-b281-ae258ae18c3b
   :alt: Proposed Task TUI showing the task navigator and a selected task's output
   :target: https://github.com/go-task/task/pull/3015


Documentation
~~~~~~~~~~~~~

Build the documentation and treat warnings as errors with:

.. code-block:: console

    $ task docs

Start a live-reloading server that watches the documentation and package sources
with:

.. code-block:: console

    $ task docs:serve

Pass ``-a`` after ``--`` when changing CSS or other static files so Sphinx rebuilds
every page:

.. code-block:: console

    $ task docs:serve -- -a

Dependencies
~~~~~~~~~~~~

Development dependencies belong to their corresponding environments in
``hatch.toml``.
The development and Python test environments deliberately resolve compatible
versions afresh so scheduled CI can detect dependency compatibility problems.
Reproducibility-sensitive lint, documentation, and package-checking environments use
committed PEP 751 lockfiles.

Regenerate affected lockfiles after changing a locked environment:

.. code-block:: console

    $ hatch env lock

Use ``--upgrade`` only when intentionally upgrading locked dependencies:

.. code-block:: console

    $ hatch env lock --upgrade

Commit every changed ``pylock.*.toml`` file together with its ``hatch.toml`` change.

Building distributions
~~~~~~~~~~~~~~~~~~~~~~

Build the source distribution and wheel and validate their metadata with:

.. code-block:: console

    $ task build

Pull requests
-------------

Keep pull requests focused on the scope agreed in the issue.
Include tests for behavioral changes and update user documentation when the public
API or documented behavior changes.
Before requesting review, run ``task qa:all`` and ``task build``.
