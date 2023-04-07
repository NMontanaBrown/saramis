SARAMIS
===============================

.. image:: https://github.com/NMontanaBrown/saramis/raw/master/project-icon.png
   :height: 128px
   :width: 128px
   :target: https://github.com/NMontanaBrown/saramis
   :alt: Logo

.. image:: https://github.com/NMontanaBrown/saramis/badges/master/build.svg
   :target: https://github.com/NMontanaBrown/saramis/pipelines
   :alt: GitLab-CI test status

.. image:: https://github.com/NMontanaBrown/saramis/badges/master/coverage.svg
    :target: https://github.com/NMontanaBrown/saramis/commits/master
    :alt: Test coverage

.. image:: https://readthedocs.org/projects/saramis/badge/?version=latest
    :target: http://saramis.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status



Author: Nina Montana Brown

SARAMIS is developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.

SARAMIS is tested on Python 3.9 but should support other modern Python versions.


Developing
----------

Cloning
^^^^^^^

You can clone the repository using the following command:

::

    git clone https://github.com/NMontanaBrown/saramis


Running tests
^^^^^^^^^^^^^
Pytest is used for running unit tests:
::

    pip install pytest
    python -m pytest


Linting
^^^^^^^

This code conforms to the PEP8 standard. Pylint can be used to analyse the code:

::

    pip install pylint
    pylint --rcfile=tests/pylintrc saramis


Installing
----------

You can pip install directly from the repository as follows:

::

    pip install git+https://github.com/NMontanaBrown/saramis



Using SARAMIS and it's functionalities will require the compilation of some libraries locally, or the use of a Docker image.
For more information, see the 'docs/install' folder.

Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Useful links
^^^^^^^^^^^^

* `Source code repository`_
* `Documentation`_


Licensing and copyright
-----------------------

Copyright 2023 University College London.
SARAMIS is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/NMontanaBrown/saramis
.. _`Documentation`: https://saramis.readthedocs.io
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/NMontanaBrown/saramis/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/NMontanaBrown/saramis/blob/master/LICENSE

