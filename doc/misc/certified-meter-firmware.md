# Overview Certified Meter Firmware Releases

# Overview

The BSM-WS36A-H01-1311-0000 provides firmware information for its meter and
communication module separately. They have individual controllers and are
therefor running individual firmware.

Information about the firmware running on these controllers is provided in two
ways:

- At the meter's display, at different views
    - Meter module firmware info at _Software Version_
    - Communication module firmware info at _Meter Address_/_Zähleradresse_
      cycling through the following pieces
        - The first four digits of the firmware revision prefixed with `F0`
        - The first eight digits of the firmware hash prefixed with `F1` and
          `F2`

- Via its Modbus interface where it could be read from three different data
  points
    - The meter module's firmware info in [_bsm_](../examples/modbus-interface.md#model-instances)/[_VrM_](../../bauer_bsm/bsm/models/smdx_64900.xml#L58)
    - The communication module's firmware revision in [_bsm_](../examples/modbus-interface.md#model-instances)/[_VrC_](../../bauer_bsm/bsm/models/smdx_64900.xml#L66)
    - The communication module's firmware hash in the BLOB [_cfwh_](../examples/modbus-interface.md#model-instances)/[_B_](../../bauer_bsm/bsm/models/smdx_64902.xml#L25)

The meter module presents its firmware information as a combined string of
release, revision, and firmware hash. The communication module provides
revision and firmware hash separately.

The following sections contain the certified firmware releases for this meter.


# Meter Module 1.8 and Communication Module 1.1

## Changelog

- Add non-switching snapshots _Signed Start Snapshot_ and _Signed End Snapshot_


## Meter Module

- Revision 1.8:23DB:9D6A


## Communication Module

- Revision
    - 08d1aa312bb0b367f1ed23a433abb92a97844c5e
    - Short representation at data point _bsm_/_VrC_: 08d1aa3
    - Short representation at the meter display: `F008D1`
- Firmware Hash
    - d1922c43218d12e13743486fd41bb105c716534b9390eccaa5723402e7b2169d
    - Completely provided at repeating data point _cfwh_/_B_
    - Short representation at meter display: `F1D192` and `F22C43`


# Meter Module 1.9 and Communication Module 1.2

## Changelog

- Add IEC-61851-compliant charging cycle using DOE for final contactor control
  (enabling the contactor to close is done using _Signed Turn-On Snapshot_ and
  to open via _Signed Turn-Off Snapshot_)


## Meter Module

- Revision 1.9:32CA:AFF4


## Communication Module

- Revision
    - 6d1dd3cbb90636f2a7105ef1cc29d9d7852704eb
    - Short representation at data point _bsm_/_VrC_: 6d1dd3c
    - Short representation at the meter display: `F061D1`
- Firmware Hash
    - fc99b5088ccf8d9754bcc6d2df6354140388cd3599f8f85f3a7d9e3fa0fa3c7c
    - Completely provided at repeating dta point _cfwh_/_B_
    - Short representation at meter display: `F1FC99` and `F2B508`


# Meter Module 1.9 and Communication Module 1.3

## Changelog

- Harmonize output for energy values
    - Only digits shown on the meter display are provided
    - Meter display shows values in kWh with two decimal digits
    - SunSpec models contain values in Wh with a scale factor of 10^1 = 10
    - OCMF data contains values in kWh with two decimal digits
- Data points _Meta2_ and _Meta3_ added to OCMF output
    - Previously only _Meta1_ was present there as _ID_
    - OCMF data now contains _Meta2_ and _Meta3_ as _X2_ and _X3_ if non-empty
- Response counter _RCnt_ is no longer increased on every startup
    - Snapshots created before and after a power cycle now contain subsequent
      counter values _n_ and _(n + 1)_
- Meter display permanently illuminated
    - Previously the meter display was illuminated only during an active
      charging process


## Meter Module

- Revision 1.9:32CA:AFF4


## Communication Module

- Revision
    - 01d484fff6a5ee086b3728a4b255582dd344d196
    - Short representation at data point _bsm_/_VrC_: 01d484f
    - Short representation at the meter display: `F001D4`
- Firmware Hash
    - 11b49f84cf423009674d78f0af72a39a2a59b49e2a46e9ed587d48a54434531d
    - Completely provided at repeating dta point _cfwh_/_B_
    - Short representation at meter display: `F111B4` and `F29F84`
