.. highlight:: none

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

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
