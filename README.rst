SARAMIS: Simulation Assets for Robotic-Assisted and Minimally Invasive Surgery
===============================

.. image:: /docs/static/main_fig.png
Author: Nina Montana Brown

SARAMIS is developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.


Data
----------

SARAMIS data may be provisionally downloaded at the following links:

* https://saramis.s3.eu-north-1.amazonaws.com/abdomen.tar.gz
* https://saramis.s3.eu-north-1.amazonaws.com/amos.tar.gz
* https://saramis.s3.eu-north-1.amazonaws.com/total.tar.gz
* https://saramis.s3.eu-north-1.amazonaws.com/metadata.tar.gz
* https://saramis.s3.eu-north-1.amazonaws.com/rl_expt.tar.gz


Reproducing SARAMIS
----------

* Labelling and Analysis: full instructions to run the labelling, meshing, tetrahedralisation, texturing, and analysis of the SARAMIS dataset are included at the
`labelling instructions`_ portion of the docs.

* RL Experiment: full instructions to run the training of a navigation agent are included in the `RL experiment`_ section of the docs.

Developing
----------

Cloning
^^^^^^^

You can clone the repository using the following command:

::

    git clone https://github.com/NMontanaBrown/saramis


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


Licensing and copyright
-----------------------

Copyright 2023 University College London.
SARAMIS code is released under the BSD-3 license. Please see the `license file`_ for details.
SARAMIS data is released under CC-BY-NC-SA license. Please see the paper and Supplementary Materials for full details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/NMontanaBrown/saramis
.. _`RL experiment`: https://github.com/NMontanaBrown/saramis/docs/RL
.. _`labelling instructions`: https://github.com/NMontanaBrown/saramis/docs/labelling
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/NMontanaBrown/saramis/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/NMontanaBrown/saramis/blob/master/LICENSE

