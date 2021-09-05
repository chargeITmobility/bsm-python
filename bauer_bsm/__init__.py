# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


import warnings

from .bsm.pathlist import PackageLoader, Pathlist
from .sunspec.core import device as sdevice


# Attempt to add BSM models to pySunSpec by setting our resource provider.
if sdevice.file_pathlist is None:
    pathlist = Pathlist()
    pathlist.add_loader(PackageLoader(__package__, 'bsm/models/'))

    sdevice.file_pathlist = pathlist
else:
    warnings.warn('file_pathlist is not None. '
        'Cowardly refusing to set ours for loading BSM models. '
        'No BSM models will be available.')
