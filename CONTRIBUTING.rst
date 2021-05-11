.. highlight:: none

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/janLuke/cloup/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

cloup could always use more documentation, whether as part of the
official cloup docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/janLuke/cloup/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `cloup` for local development.

1. Fork the `cloup` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/cloup.git
    $ cd cloup

3. Create a development virtual environment in `venv` folder. If you have tox
   and Python 3.8 installed, you can create one with all dependencies running::

    $ tox -e dev

   Otherwise, you can create one with ``venv``
   (`see here for more <https://docs.python.org/3/library/venv.html>`_)::

    $ python -m venv /venv

   then activate it (the right command depends on the platform/shell you are using)::

    $ source venv/bin/activate[.fish|.csh]  # bash | fish ...
    $ venv/Scripts/activate.{bat|ps1}       # Windows (cmd | Powershell)

   and install the requirements::

    $ pip install requirements/dev.txt

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass linting, mypy
   and tests running tox::

    $ tox -p         # run all tests (env) in parallel
    $ tox -e <env>   # run only the specified env

   Alternatively, you can use ``make`` to run commands only in your dev environment
   if you have it installed. Run ``make help`` or read the ``Makefile`` to see
   the available commands.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for all Python versions supported by cloup. Check
   https://travis-ci.com/janLuke/cloup/pull_requests
   and make sure that the tests pass for all supported Python versions.
