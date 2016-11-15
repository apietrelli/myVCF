.. _install_label:

How to install myVCF
====================

Download myVCF
--------------

You can download **myVCF** package from:

Compressed package
^^^^^^^^^^^^^^^^^^
1. Go to the project `homepage <https://apietrelli.github.io/myVCF/>`_
2. Click on one of the button
3. Extract the compressed file into your working directory

GitHub
^^^^^^

If you have GitHub installed in your computer, you can clone the project directly on your working directory

1. Open the terminal/CGWin and type:

.. code-block:: shell

  git clone https://github.com/apietrelli/myVCF.git

The command will download the entire package and you will be ready to install requirements

.. note::
    To download :code:`git` tool for Unix/MAC operating system

    .. code:: shell

      # MAC
      brew install git
      # Ubuntu/Debian Unix OS
      apt-get install git

Install requirements
--------------------

Tested and developed under Linux/MAC operating system, but also suitable for Windows user with some modification

Unix/MAC
^^^^^^^^

1. Open terminal
2. Go to myVCF dir
3. Execute this command:

.. code-block:: shell

  pip install -r /path/to/requirements.txt

Verify the installation by typing this

.. code-block:: shell

  python manage.py shell

Windows
^^^^^^^


Launch the application
----------------------
