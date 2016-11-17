.. _install_label:

How to install myVCF
====================

Download myVCF
--------------

You can download **myVCF** package from:

- **Compressed package**

1. Go to `myVCF homepage <https://apietrelli.github.io/myVCF/>`_
2. Click on one of the button present in the header page
3. Extract the compressed file into your working directory
4. At the end of the process you will have a directory named :code:`myVCF/` containing the desktop application

- **GitHub**

If you have GitHub installed in your computer, you can clone the project directly on your working directory

1. Open the terminal and type:

.. note::
  For MAC users, you can fin the terminal app by searching through Spotlight and type :code:`terminal` and click on the application

.. code-block:: shell

  $> cd path/to/working/dir
  $> git clone https://github.com/apietrelli/myVCF.git

The command will create a directory named :code:`myVCF/` containing the desktop application

.. note::
    To download :code:`git` tool for Unix/MAC operating system

    .. code:: shell

      # Ubuntu/Debian Unix OS
      $> sudo apt-get install git
      # MAC
      $> brew install git
    for Windows users, you can download the git software from the `Git homepage <https://git-scm.com/download/win>`_ and use the same command as for Unix/MAC user by using `GitBASH <https://git-for-windows.github.io/>`_


Install requirements
--------------------

The application is developed using Python/Django framework and use :code:`sqlite` as database platform.
Please verify the installation of Python and sqlite on your computer.

Python 2.7
^^^^^^^^^^

All the myVCF tool is based on **Python 2.7** language. Please verify the installation of python.

If you are not sure or you need to install it, please follow the notes below about the installation depending on your operating system.

**Unix (Ubuntu/Debian system)**

Using terminal, install :code:`python2.7` using :code:`apt-get`

.. code-block:: shell

  $> sudo apt-get install python2.7

**MAC**

Open the terminal and install :code:`python2.7` with :code:`brew`

.. Note::
  You can find the shell terminal in MAC OS by typing :code:`terminal` in Spotlight textbox and click on the application.

.. code-block:: shell

  # Terminal application
  $> brew install python2.7

You can test the installation in the terminal

.. code-block:: shell

  $> python
  Python 2.7.5 (default, Mar  9 2014, 22:15:05)
  [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>>
  >>>quit()

**Windows**

You can download the :code:`python2.7` package from `Python project site <https://www.python.org/downloads/>`_

.. warning:: Please download the **Python2.7** package **NOT** Python3.x

sqlite
^^^^^^

The storage of VCF data has been implemented by using :code:`sqlite` as backend database. This cross-platform solution allows the end-user to workaround some configuration steps mandatory with other database system.

Please following this instructions to install :code:`sqlite` depending on your operating system

**Unix (Ubuntu/Debian system)/MAC**

1. Open the :code:`terminal`
2. Install :code:`sqlite3` package

.. code-block:: shell

  # Ubuntu/Debian Unix OS
  $> sudo apt-get install sqlite3
  # MAC OS
  $> brew install sqlite3

3. Launch :code:`sqlite3` from shell

.. code-block:: shell

  $> sqlite3
  SQLite version 3.7.13 2012-07-17 17:46:21
  Enter ".help" for instructions
  Enter SQL statements terminated with a ";"
  sqlite>
  # Quit from the sqlite3 shell
  sqlite> .q

**Windows**

1. Download the :code:`sqlite` from the web site https://sqlite.org/download.html

.. warning::

  Check your Windows version installed (32 or 64 bit) to correctely download the right :code:`sqlite3` package from the web site

  To check your system click on:

  **Start** > **Control panel** > **System**

  and check the version.



Python Library
^^^^^^^^^^^^^^

**Unix/MAC**

1. Open terminal
2. Go to :code:`myVCF/` dir
3. Execute this command:

.. code-block:: shell

  pip install -r requirements.txt

Verify the installation by typing::

  python manage.py shell

Launch the application
----------------------

Finally, you're ready to start the webserver::

    python manage.py runserver

Visit http://127.0.0.1:8000/ in your browser to see how it looks.
