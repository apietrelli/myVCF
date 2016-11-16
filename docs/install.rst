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

.. code-block:: shell

  cd path/to/working/dir
  git clone https://github.com/apietrelli/myVCF.git

The command will create a directory named :code:`myVCF/` containing the desktop application

.. note::
    To download :code:`git` tool for Unix/MAC operating system

    .. code:: shell

      # MAC
      brew install git
      # Ubuntu/Debian Unix OS
      apt-get install git
    for Windows users, you can download the git software from the `Git homepage <https://git-scm.com/download/win>`_ and use the same command as for Unix/MAC user by using `GitBASH <https://git-for-windows.github.io/>`_


Install requirements
--------------------

The application is developed using Python/Django framework and use :code:`sqlite` as database platform.
Please verify the installation of Python and sqlite on your computer.

Python 2.7
^^^^^^^^^^

All the myVCF tool is based on **Python 2.7** language. Please verify the installation of python.

If you are not sure or you need to install it, please follow the notes below about the installation depending on your operating system.

**Unix (Debian system)**

Using terminal, install :code:`python2.7`

.. code-block:: shell

  sudo apt-get install python2.7

You can test the installation in terminal

.. code-block:: shell

  $> python
  Python 2.7.5 (default, Mar  9 2014, 22:15:05)
  [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>>

**MAC**

Open the terminal and install :code:`python2.7` with :code:`brew`

.. code-block:: shell

  brew install python2.7

You can test the installation in terminal

.. code-block:: shell

  $> python
  Python 2.7.5 (default, Mar  9 2014, 22:15:05)
  [GCC 4.2.1 Compatible Apple LLVM 5.0 (clang-500.0.68)] on darwin
  Type "help", "copyright", "credits" or "license" for more information.
  >>>

**Windows**

You can download the :code:`python2.7` package from `Python project site <https://www.python.org/downloads/>`_

.. warning:: Please download the **Python2.7** package NOT the Python3

sqlite
^^^^^^


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
