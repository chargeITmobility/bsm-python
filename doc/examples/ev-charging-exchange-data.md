# Electric Vehicle Charging Exchange Data

## Overview

There are many options for integrating the BSM-WS36A into electric vehicle
charging infrastructure. It facilitates this by providing signed data in two
output formats:

1. Its [proprietary snapshot format](snapshots.md)
    - Where the actually signed data is based on an abstract representation
      snapshot data
    - Allowing to translate snapshot data in other forms where the abstract
      representation could be reconstructed from
2. [OCMF](ocmf.md)
    - Derived from the former
    - "Signed as seen" and therefor with an individual signature
    - Passed on literally until verification

This allows it to be used as a turn-key solution with chargeIT mobility's
solutions (charging controller, backend, frontend, and Chargy for validation)
and easily integrates with others.

![EV Charging Exchange Data](img/ev-charging-exchange-data.png)


