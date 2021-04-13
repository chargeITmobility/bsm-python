# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


import pkgutil
import warnings

from .sunspec.core import device as sdevice


class _Pathlist:
    def read(self, filename):
        # Testing for the existence of resources with exception handling is
        # pretty akward. Suggestions for improvement are welcome.
        try:
            data = pkgutil.get_data(__package__, 'bsm/models/' + filename)
        except OSError:
            # Callers expect None to be returned in case the requested file was
            # not found.
            data = None
        return data


# Attempt to add BSM models to pySunSpec by setting our resource provider.
if sdevice.file_pathlist is None:
    sdevice.file_pathlist = _Pathlist()
else:
    warnings.warn('file_pathlist is not None. '
        'Cowardly refusing to set ours for loading BSM models. '
        'No BSM models will be available.')
