Getting Started
===============
Make sure you have at least version 3.8 of Python before starting.

1. Setup virtual environment
-----------------------------
Please make sure you have ``python3-virtualenv`` package installed.

.. code-block:: bash

    python3 -m virtualenv venv
    source venv/bin/activate
    make install

This will create virtual environment with all required dependencies.

2. Run server
-------------
Before running the development server, you should set path to database:

.. code-block::

    export DATABASE_URI=sqlite:///explorebaduk.sqlite3

To run development server, execute command:

.. code-block::

    python run_api.py

To see additional arguments, use:

.. code-block::

    python run_api.py --help

3. Run tests
------------
To run tests, execute command:

.. code-block::

    pytest tests --cov=explorebaduk --cov-report html

It will generate test report, which you can find at ``htmlcov/index.html``
