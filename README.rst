================
IsoNet plugin
================

This plugin allows to use IsoNet programs within the Scipion framework

`IsoNet <https://github.com/IsoNet-cryoET/IsoNet/>`_ stand for ISOtropic reconstruction of Electron Tomography.
It train deep neural networks to reconstruct meaningful contents in the missing wedge for electron tomography
increase signal-to-noise ratio using the information learned from the original tomogram. The software requires
tomograms as input. Observing at about 30A resolutions, the IsoNet generated tomograms are largely isotropic.


You will need to use `3.0.0 <https://scipion-em.github.io/docs/release-3.0.0/docs/scipion-modes/how-to-install.html>`_ version of Scipion to run these protocols.


Protocols
==========

* **Isotropic Reconstruction**: Isotropic Reconstruction of Electron Tomograms with Deep Learning

**Latest plugin version**
==========================
**v3.0.0**
-----------
* **new**     :  First plugin version


**Installing the plugin**
=========================

In order to install the plugin follow these instructions:

1. **Install the plugin**

.. code-block::

     scipion installp -p scipion-em-isonet

or through the **plugin manager** by launching Scipion and following **Configuration** >> **Plugins**

**To install in development mode**

- Clone or download the plugin repository

.. code-block::

          git clone https://github.com/scipion-em/scipion-em-isonet.git

- Install the plugin in developer mode.

.. code-block::

  scipion installp -p local/path/to/scipion-em-isonet --devel


===============
Buildbot status
===============

Status devel version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/isonet_devel.svg

Status production version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/isonet_prod.svg


==================
IsoNet References
==================
The publication associated with IsoNet can be found `here <https://www.biorxiv.org/content/10.1101/2021.07.17.452128v1>`_:


