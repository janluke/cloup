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
4. If the maintainer agrees, fork the repository, create a branch, implement the change,
   and open a pull request linked to the issue.

Starting with an issue avoids duplicated work and gives maintainers and contributors
a place to settle API and compatibility decisions before code is written.

Development
-----------

Set up a development environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cloup uses `Hatch <https://hatch.pypa.io/latest/>`_ for isolated Python
environments and `Task <https://taskfile.dev/>`_ as its project command interface.

To set up a development environment you have two options:

1. (recommended) use the Dev Container configuration provided with the repository;
   this is the quickest option when Docker is available. The dev container also
   includes the experimental Task build with the TUI described in the box below.

2. Install them manually.

.. admonition:: Experimental TUI for Task

    Cloup's maintainer uses an experimental build of Task including a TUI he's authored
    and submitted as a `PR <https://github.com/go-task/task/pull/3015>`_. The TUI greatly
    improves DX when running tasks with parallel dependencies.

    If you use the Dev Container, it comes pre-installed. If you chose the manual setup
    route, download it from the `task-tui releases page
    <https://github.com/janluke/task-tui/releases>`_ as described below. Refer to the
    PR description for how to use it.

    .. image:: https://github.com/user-attachments/assets/07e4d5d1-61aa-4554-b281-ae258ae18c3b
        :alt: Proposed Task TUI showing the task navigator and a selected task's output
        :target: https://github.com/go-task/task/pull/3015

Option 1: using the Dev Container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The repository includes a `Dev Container <https://containers.dev/>`_ configuration
for clients such as Visual Studio Code and GitHub Codespaces. It requires Docker
when run locally.

All you have to do is open the repository folder in the container. For example,
in Visual Studio Code, make sure you have the
`Dev Container Extension <https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers>`_
installed; then follow
`these simple steps <https://code.visualstudio.com/docs/devcontainers/containers#_quick-start-open-an-existing-folder-in-a-container>`_.

After the container is created, the ``dev`` Python virtual environment is created
automatically (using ``task env``). If you use Visual Studio Code, the IDE comes
already configured to use the Python interpreter in this environment. In other IDEs,
you will have to select it manually; its location inside the container is::

    ~/.local/share/cloup/dev/bin/python

The container provides two Task executables:

* ``task`` is an official released build used for the project commands.
* ``task-tui`` is a pinned `build <https://github.com/janluke/task-tui/releases>`_
  of the experimental TUI written by Cloup's maintainer, which was submitted as a
  `PR <https://github.com/go-task/task/pull/3015>`_.

Run the experimental build directly with ``task-tui --tui`` or use its ``tui``
alias. The stable ``task`` command remains unchanged.

Option 2: manual setup
^^^^^^^^^^^^^^^^^^^^^^

Install Hatch
"""""""""""""

You can install hatch with either pipx or uv:

.. tab-set::

    .. tab-item:: Using uv

        .. code-block:: console

            uv tool install hatch

    .. tab-item:: Using pipx

        .. code-block:: console

            pipx install hatch

Hatch creates environments automatically when their commands are first used.
By default, Hatch environments are stored in Hatch's global data directory.
If you prefer to store them in each project/repository folder, under a ``.hatch/``
subfolder, run:

.. code-block:: console

    $ hatch config set dirs.env.virtual .hatch

Install Task
""""""""""""

To install the canonical Task, you can either follow the
`official installation guide <https://taskfile.dev/docs/installation>`_ for your OS
or install it through the **unofficial** Python package:

.. tab-set::

    .. tab-item:: Using uv

        .. code-block:: console

            $ uv tool install "go-task-bin>=3.46.1"

    .. tab-item:: Using pipx

        .. code-block:: console

            $ pipx install "go-task-bin>=3.46.1"

(Optional) Install Task with TUI
""""""""""""""""""""""""""""""""

Builds are published on the `task-tui releases page
<https://github.com/janluke/task-tui/releases>`_ for Linux, macOS, and Windows.

Download the archive for your platform and extract ``task-tui`` into a
directory on your ``PATH``. On Linux with an x86-64 processor:

.. code-block:: console

   $ mkdir -p "$HOME/.local/bin"
   $ curl -fsSL https://github.com/janluke/task-tui/releases/latest/download/task-tui_linux_amd64.tar.gz \
       | tar -xz -C "$HOME/.local/bin" task-tui

Replace ``linux_amd64`` with ``linux_arm64``, ``darwin_amd64`` or
``darwin_arm64`` as needed; the Windows archives are ``.zip`` files.

Consider adding the `tui` alias to your shell's startup file, such as ``~/.bashrc``
or ``~/.zshrc``:

.. code-block:: bash

   alias tui='task-tui --tui'

The build is installed under a distinct name, so it does not replace the
canonical ``task`` executable. To update it later, download a newer release the
same way.


Set up a Python venv for your IDE
"""""""""""""""""""""""""""""""""

Even if Hatch creates environments automatically when needed, you probably
still want to set a Python environment for your IDE.

To create the ``dev`` environment and print its location, run:

.. code-block:: console

    $ task env

Select the reported Python interpreter in your IDE.
The environment contains Cloup in editable mode together with the test, coverage,
and typing dependencies, so it can run tests and type checks directly from the IDE.

Using Task
~~~~~~~~~~

Run ``task --list`` to see all available project commands.

Invoke one project task by name, for example:

.. code-block:: console

    $ task fix

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
``TASK_CONCURRENCY`` environment variable. For example, to run tasks sequentially:

.. code-block:: console

    $ task --concurrency 1 qa:all

For contiguous, failure-focused logs, use Task's grouped output:

.. code-block:: console

    $ task --output group --output-group-error-only qa:all

Using the experimental Task TUI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When running tasks that execute multiple tasks in parallel, it's very useful to
be able to inspect the output of each one separately in a UI.

The Dev Container includes a pinned build of the branch as ``task-tui``; run it with
the ``tui`` alias while keeping the official release available as ``task``, e.g.:

.. code-block:: console

    tui qa:all

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
     - Fix lint violations and format the code with Ruff.
   * - ``task typing``
     - Type-check the code in the development environment.
   * - ``task typing:all``
     - Type-check in every Python and Click compatibility environment.

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

Use ``task qa`` during routine development. Run ``task qa:all`` for changes that
may affect supported Python or Click versions.

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

Regenerate an affected lockfile after changing a locked environment:

.. code-block:: console

    $ hatch env lock ENV_NAME

Use ``--upgrade`` or ``--upgrade-package <package>`` only when intentionally
upgrading locked dependencies:

.. code-block:: console

    $ hatch env lock ENV_NAME --upgrade

Commit each changed ``pylock.*.toml`` file with the configuration change that
required it, or as part of a clearly identified intentional dependency refresh.

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
Before requesting review, run the appropriate QA command described above. Also run
``task build`` after changing packaging, project metadata, package layout, or build
hooks.
