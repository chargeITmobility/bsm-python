# BSM Python library and command line tool
#
# Copyright (C) 2020 chargeIT mobility GmbH
#
# SPDX-License-Identifier: Apache-2.0


from ..bsm import config
from ..bsm.client import BsmClientDevice, SnapshotStatus, SunSpecBsmClientDevice


def generate_ocmf_xml(client, read_data=True):
    """
    Generates an OCMF XML document from signed turn-on and turn-off
    snapshots.

    The XML document gets returned as byte data for declaring and using
    identical encoding. In case that one of the snapshots is not valid,
    None will be returned.
    """
    # Allow passing both types of BSM clients.
    if isinstance(client, SunSpecBsmClientDevice):
        client = client.device
    assert isinstance(client, BsmClientDevice)

    bsm = client.model_aliases['bs_meter']
    ostons = client.model_aliases['ocmf_signed_turn_on_snapshot']
    ostoffs = client.model_aliases['ocmf_signed_turn_off_snapshot']
    result = None

    if read_data:
        bsm.read_points()
        ostons.read_points()
        ostoffs.read_points()

    ostons_status = ostons.points[config.OCMF_STATUS_DATA_POINT_ID].value
    ostons_data = ostons.points[config.OCMF_DATA_DATA_POINT_ID].value
    ostoffs_status = ostoffs.points[config.OCMF_STATUS_DATA_POINT_ID].value
    ostoffs_data = ostoffs.points[config.OCMF_DATA_DATA_POINT_ID].value

    if ostons_status == SnapshotStatus.VALID \
        and ostoffs_status == SnapshotStatus.VALID:

        # Don't read BSM model instance containing the public key data
        # again. If requested, this has been done above.
        der = client.get_public_key(read_data=False).hex()

        template = \
            '<?xml version="1.0" encoding="{encoding}" standalone="yes"?>\n' \
            '<values>\n' \
            '  <value transactionId="1" context="Transaction.Begin">\n' \
            '    <signedData format="OCMF" encoding="plain">{ostons}</signedData>\n' \
            '    <publicKey encoding="plain">{pk}</publicKey>\n' \
            '  </value>\n' \
            '  <value transactionId="1" context="Transaction.End">\n' \
            '    <signedData format="OCMF" encoding="plain">{ostoffs}</signedData>\n' \
            '    <publicKey encoding="plain">{pk}</publicKey>\n' \
            '  </value>\n' \
            '</values>\n'

        values = {
                # XML seems to define encoding names to be upper-case.
                'encoding': config.PYSUNSPEC_STRING_ENCODING.upper(),
                'pk': der,
                'ostons': ostons_data,
                'ostoffs': ostoffs_data,
            }

        # Generate data in the same encoding as pySunSpec's fixed one as
        # string data got set and signed in this one.
        result = template.format(**values).encode(config.PYSUNSPEC_STRING_ENCODING)

    return result
