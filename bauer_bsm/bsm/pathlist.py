# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from pathlib import Path
import pkgutil


"""
Implements the read interface used by pySunSpecs file_pathlist for adding more
source directories for SMDX model files.
"""
class Pathlist:
    def __init__(self):
        self.loaders = []


    def add_loader(self, loader):
        self.loaders.append(loader)


    def read(self, filename):
        data = None

        for loader in self.loaders:
            data = loader.read(filename)
            # The loader which returns the first data wins.
            if data is not None:
                break

        return data


"""
Data loader for package resources. It provides the read interface for
pySunSpec's pathlist interface used for loading SMDX data from
additional/alternative sources.
"""
class PackageLoader:
    def __init__(self, package, models_path):
        self.package = package
        self.models_path = Path(models_path)


    def read(self, filename):
        # Testing for the existence of resources with exception handling is
        # pretty akward. Suggestions for improvement are welcome.
        try:
            path = self.models_path / filename
            data = pkgutil.get_data(self.package, str(path))
        except OSError:
            # Callers expect None to be returned in case the requested file was
            # not found.
            data = None
        return data
