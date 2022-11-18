=======================
Scipion isonet plugin
=======================

This is a template plugin for **scipion**

==========================
Steps to adapt this plugin
==========================

IMPORTANT: To simplify the instructions all the commands would refer to an hypothetical new plugin name called "coolem".
Note that you must replace "isonet" by your plugin name.

**Clone it:**

.. code-block::

    git clone git@github.com:scipion-em/scipion-em-isonet.git scipion-em-coolem

**Reset the git repo**

.. code-block::

    cd scipion-em-coolem
    rm -rf .git
    git init

**Empty CHANGES.txt**

.. code-block::

    rm CHANGES.txt && touch CHANGES.txt

**Rename "myplugin" to coolem (IDE might help here)**

.. code-block::

    mv myplugin coolem

**Tidy up imports**

Tip 1: IDE refactrization should rename at once the classes and the imports
Tip 2: Search in your IDE for "myplugin" and replace by *"coolem"*

coolem/protocols/protocol_hello_world.py:
 class MyPluginPrefixHelloWorld --> class CoolemPrefixHelloWorld

coolem/protocol/__init__.py:
 from .protocol_hello_world import MyPluginPrefixHelloWorld --> from .protocol_hello_world import CoolemPrefixHelloWorld

coolem/wizards/wizard_hello_world.py:
 _targets = [(MyPluginPrefixHelloWorld, ['message'])]  -->     _targets = [(CoolemPrefixHelloWorld, ['message'])]
 class MyPluginPrefixHelloWorldWizard --> class CoolemPrefixHelloWorldWizard

coolem/wizards/__init__.py:
 from .wizard_hello_world import MyPluginPrefixHelloWorldWizard  --> from .wizard_hello_world import CoolemPrefixHelloWorldWizard

protcocols.conf: rename MyPluginPrefixHelloWorld --> CoolemPrefixHelloWorld


setup.py:
 update almost all values: name, description, ...

 be sure to update package data
.. code-block::

    package_data={  # Optional
       'coolem': ['icon.png', 'protocols.conf'],
    }

  and the entry point
.. code-block::

    entry_points={
        'pyworkflow.plugin': 'coolem = coolem'
    }

**Install the plugin in devel mode**

.. code-block::

    scipion3 installp -p /home/me/scipion-em-coolem --devel

TIP: If installation fails, you can access pip options like:

.. code-block::

    scipion3 python -m pip ... (list, install, uninstall)

**Customize it**
    replace icon.png with your logo.
    update the bibtex.py with your reference.

**Get rid of this content and keep the readme informative**

