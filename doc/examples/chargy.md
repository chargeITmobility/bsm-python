# chargeIT mobility Chargy and Custom Formats

> This is a pre-release describing a format which is currently agreed upon. The
> final format will likely differ.

[Signed Snapshot](snapshots.md) data from the BSM-WS36A could also be
transformed into custom formats which are not directly supported by the meter.
For example, the JSON format used by chargeIT mobility's
[Chargy](https://github.com/chargeITmobility/ChargyDesktopApp).

This is typically done by taking the signed snapshot data from the meter. Key
to using this data without the need for re-signing it (in a certified
environment) is to provide all necessary data needed to re-create the [abstract
data representation](snapshots.md#abstract-data-representation) used to compute
the snapshot's message digest. In essence:

- Value, scale factor, and DLMS unit code for numerical values

- Length and the byte representation for strings

[Snapshot Verification](snapshots.md#snapshot-verification) gives details on
that.


## Example

### Overview

This example shows how to generate data for chargeIT mobility's
[Chargy](https://github.com/chargeITmobility/ChargyDesktopApp) JSON format. It
is based on the same charging process already used for the examples in [Open
Charge Metering Format (OCMF)](ocmf.md) and [Electric Vehicle
Charging](ev-charging.md).


### Preparation

Setup the meter and create start and end snapshots as described in [Charging
Scenario](ev-charging.md#charging-scenario).


### Reading Data from Meter

When preparation is done done, the following [model
instances](modbus-interface.md#model-instances) provide the necessary data for
generating Chargy's JSON format. This is general information from the models:

- [_Common_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml)
  providing nameplate information
- [_Signing Meter_](../../bauer_bsm/bsm/models/smdx_64900.xml) providing public
  key and software versions

And snapshot data from one of the snapshot pairs. Either the switching snapshots:

- [_Signed Turn-On Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml)
- [_Signed Turn-Off Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml)

Or the non-switching snapshots:

- [_Signed Start Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml)
- [_Signed End Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml)

This example uses the switching snapshots and would work in analog for the non-switching ones.


#### Nameplate Information

Reading the nameplate information from the common model is straight forward:
```
$ bsmtool get cb
common:
    Mn: BAUER Electronic
    Md: BSM-WS36A-H01-1311-0000
    Opt: None
    Vr: 1.9:32CA:AFF4
    SN: 21070006
    DA: 42
```
```
--> 2a 03 9c44 0042 ada5
<-- 2a 03 84 424155455220456c656374726f6e69630000000000000000000000000000000042534d2d57533336412d4830312d313331312d3030303000000000000000000000000000000000000000000000000000312e393a333243413a414646340000003231303730303036000000000000000000000000000000000000000000000000002a8000 890d
```


#### Version Information and Public Key

Software version information and the meter's public key can be read from the Signing Meter instance:
```
$ bsmtool get bsm
bsm:
    fixed:
        ErrM: 00000000
        SNM: 21070006
        SNC: 000b57000060caa1
        VrM: 1.9:32CA:AFF4
        VrC: 6d1dd3c
        MA1: 001BZR1521070006
[...]
        Meta1: contract-id: rfid:12345678abcdef
        Meta2: evse-id: DE*BDO*E8025334492*2
        Meta3: csc-sw-version: v1.2.34
        NPK: 48
        BPK: 91
    repeating blocks blob:
        PK (der): 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254
```
```
--> 2a 03 9d07 0050 dd80
<-- 2a 03 a0 30303030303030303231303730303036000000000000000030303062353730303030363063616131312e393a333243413a4146463400000036643164643363000000000000000000303031425a523135323130373030303646303644314400000000000000000000000000a0000000000420000059c1001c7e795feee49f003c00000afe001c7e6b00010000ffffffffffffffff8000ffffffffffffffff8000 8e27
--> 2a 03 9d57 0078 dd8f
<-- 2a 03 f0 636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000657673652d69643a2044452a42444f2a45383032353333343439322a320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 4ec6
--> 2a 03 9dcf 0064 5da9
<-- 2a 03 c8 6373632d73772d76657273696f6e3a2076312e322e333400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030005b3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c72540000000000 95c8
```
Section [Public Key](snapshots.md#public-key) describes the interpretation of
the public key data in detail.


#### Snapshot Data

The following sections describe how to read snapshot data and interpret key
data points:

- [Creating the Signed Turn-On Snapshot](ev-charging.md#creating-the-signed-turn-on-snapshot)
- [Key Start Snapshot Data Points](ev-charging.md#key-start-snapshot-data-points)
- [Creating the Signed Turn-Off Snapshot](ev-charging.md#creating-the-signed-turn-off-snapshot)
- [Key End Snapshot Data Points](ev-charging.md#key-end-snapshot-data-points)

So we just show the interpreted snapshot data one more time:
```
$ bsmtool get-snapshot stons
bsm_snapshot:
    fixed:
        Typ: 1
        St: 0
        RCR: None
        TotWhImp: 52440 Wh
        W: 0.0 W
        MA1: 001BZR1521070006
        RCnt: 22978
        OS: 1867397 s
        Epoch: 1609491627 s
        TZO: 60 min
        EpochSetCnt: 2814
        EpochSetOS: 1867371 s
        DI: 1
        DO: 0
        Meta1: contract-id: rfid:12345678abcdef
        Meta2: evse-id: DE*BDO*E8025334492*2
        Meta3: csc-sw-version: v1.2.34
        Evt: 0
        NSig: 48
        BSig: 72
    repeating blocks blob:
        Sig: 3046022100abf6b2c50a4021f58d075e1df434dc96f1625df66142ec32c6ab831942631c3e022100f863e4aeccee44755302a38b4a08431835b645247b1db2cfecceaa7fe017cb4a
```
```
$ bsmtool get-snapshot stoffs
bsm_snapshot:
    fixed:
        Typ: 2
        St: 0
        RCR: 160 Wh
        TotWhImp: 52610 Wh
        W: 0.0 W
        MA1: 001BZR1521070006
        RCnt: 22979
        OS: 1867722 s
        Epoch: 1609491952 s
        TZO: 60 min
        EpochSetCnt: 2814
        EpochSetOS: 1867371 s
        DI: 1
        DO: 0
        Meta1: contract-id: rfid:12345678abcdef
        Meta2: evse-id: DE*BDO*E8025334492*2
        Meta3: csc-sw-version: v1.2.34
        Evt: 0
        NSig: 48
        BSig: 70
    repeating blocks blob:
        Sig: 3044022062f36e0583471d4f438da9da549be550cdbdfa4f9d77f3d4c53339f18c66850a02200e997ccb47cb33b1fb6c504b081b097cb65231b041c9f882122cc8298f575501
```


### Chargy JSON Format

#### Overview

The charging data to be validated by Chargy gets passed as a JSON document,
like for example [`ev-charging-chargy.json`](data/ev-charging-chargy.json)
focussed on electric vehicle charging.

The root object contains a context marker (`@context`), a unique document ID
(`@id`), information about the place where charging took place
(`chargePointInfo`), the actual charging station used (`chargingStationInfo`),
and the snapshot data in the array `signedMeterValues`:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/charging-station-json-v1",
  "@id": "29596515-a37d-433c-a217-4be8e9d090ed",
  "chargePointInfo": { ... },
  "chargingStationInfo": { ... },
  "signedMeterValues": [ ...]
}
```

The BSM Tool supports creating sample documents from already successfully
created start and end snapshots via:
```
$ bsmtool chargy stons stoffs
```
See [`chargy_command`](../../bauer_bsm/cli/bsmtool.py#L399) and
[`generate_chargy_json`](../../bauer_bsm/exporter/chargy.py#L289) for the code
generating this sample documents.

Let's have a look at the root object's fields in the following sections.


#### Document Identification

The context marker is meant for identifying this type of document so that
processing it does not require guessing the actual document type. Instead,
assumptions about its structure could be made from knowing the type.
```json
"@context": "https://www.chargeit-mobility.com/contexts/charging-station-json-v1"
```
As of now, this URL just serves as an identifier and no schema information
could be retrieved from it.

The document ID uniquely identifies a certain document or so to speak, a
charging process. This value is not provided by the meter and needs to be
generated for each document. It could be an UUID for example:
```json
"@id": "29596515-a37d-433c-a217-4be8e9d090ed"
```

#### Place Information

The charge point information object
[`chargePointInfo`](data/ev-charging-chargy.json#L4) provides information about
the place where charging took place. This includes coordinates for easily
displaying the location, an address, and the EVSE ID of the charging point:
```json
"chargePointInfo": {
  "placeInfo": {
    "geoLocation": {
      "lat": 48.03552,
      "lon": 10.50669
    },
    "address": {
      "street": "Breitenbergstr. 2",
      "town": "Mindelheim",
      "zipCode": "87719"
    }
  },
  "evseId": "DE*BDO*E8025334492*2"
}
```
This is another piece of information which needs to be added when generating
the JSON document. It is not provided by the meter. If the EVSE should be
signed by the meter, it could be put into one of the meter's metadata points
and will additionally appear within the snapshot data in
[`signedMeterValues`](data/ev-charging-chargy.json#L227).


#### Snapshot Data

##### Overview

Finally, the array [`signedMeterValues`](data/ev-charging-chargy.json#L25)
contains snapshot data. Each item of this array represents a snapshot where the
first item is the start snapshot and the last one the end snapshot.

In contrast to [Document Identification](chargy.md#document-identification) and
[Place Information](chargy.md#place-information) which needs to be filled in by
the entity generating the Chargy JSON document, the data presented here is
completely taken from the meter.


##### Snapshot Objects

The JSON representation of a snapshot contains in analog to the root object a
context marker and a snapshot ID. For being unique, the latter contains the
meter ID [_MA1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L210) and the
snapshot's response counter
[_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185). For example:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/bsm-ws36a-json-v0",
  "@id": "001BZR1521070003-22107",
  "time": "2021-01-01T10:00:27+01:00",
  "meterInfo": { ... },
  "contract": { ... },
  "measurementId": 22978,
  "value": { ... },
  "additionalValues": [ ... ],
  "signature": "..."
}
```

Let's examine the remaining fields in the following sections more in detail.


##### Snapshot Identification

There are two fields representing the point in time the snapshot was created:

The point in time when the snapshot was created is given by `time` in [ISO
8601](https://en.wikipedia.org/wiki/ISO_8601) format
```json
"time": "2021-01-01T10:00:27+01:00"
```
which is a different representation of the values given by the data points as
epoch time and timezone offset:

- [_Epoch_](../../bauer_bsm/bsm/models/smdx_64901.xml#L227)
- [_TZO_](../../bauer_bsm/bsm/models/smdx_64901.xml#L232)

In case the snapshot contains invalid time information, `time` is omitted.

The field `measurementId` provides the meter's response counter
[_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L214) which is unique for
every created snapshot:
```json
"measurementId": 22978
```


##### Meter Information

The field [`meterInfo`](data/ev-charging-chargy.json#L30) provides an object
with information for identifying the meter:
```json
"meterInfo": {
  "firmwareVersion": "1.9:32CA:AFF4, 6d1dd3c",
  "publicKey": "3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254",
  "meterId": "001BZR1521070006",
  "manufacturer": "BAUER Electronic",
  "type": "BSM-WS36A-H01-1311-0000"
},
```
This object is generated from the following data points:

- `firmwareVersion` combining the software version information from
  [_VrM_](../../bauer_bsm/bsm/models/smdx_64900.xml#L58) and
  [_VrC_](../../bauer_bsm/bsm/models/smdx_64900.xml#L66)
- `publicKey` providing the meter's public key data from
  [_PK_](../../bauer_bsm/bsm/models/smdx_64900.xml#L220)
- `meterId` providing the meter ID
  [_MA1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L210)
- `manufacturer` providing the manufacturer name
  [_Mn_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml#L20)
- `type` providing the model name
  [_Md_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml#L25)


##### Customer Identification

The object [`contract`](data/ev-charging-chargy.json#L37) provides customer
identification if this is set to one of the metadata fields, in the tagged form
`contract-id: TYPE:ID`. For example, setting
_Meta1_](../../bauer_bsm/bsm/models/smdx_64900.xml#L245) to
```
contract-id: rfid:12345678abcdef
```
will result in the following contract information:
```json
"contract": {
  "id": "12345678abcdef",
  "type": "rfid"
}
```
If the tag is present, but the format of this data is not understood, it all
gets provided as `id`. In case no metadata is tagged with `contract-id:`, then
`contract` will be `null`.


##### Snapshot Data Point Values

The object [`value`](data/ev-charging-chargy.json#L42) gives the meter's
reference cumulative register
[_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) as primary value for
energy consumption.  For example:
```json
"value": {
  "measurand": {
    "id": "1-0:1.8.0*198",
    "name": "RCR"
  },
  "measuredValue": {
    "scale": 0,
    "unit": "WATT_HOUR",
    "unitEncoded": 30,
    "value": 0,
    "valueType": "UnsignedInteger32"
  }
},
}
```
The `measurand` objects gives describes the measurand by its name (data point
ID) and an OBIS ID (where available). The latter is not provided by the meter
and needs to be [inferred from the data point
ID](../../bauer_bsm/exporter/chargy.py#L22) when generating the JSON document.

The `measuredValue` object describes its actual value recorded in the snapshot.
This is the information required for rebuilding the [abstract data
representation](snapshots.md#abstract-data-representation) for signature
verification.

- `scale` is the scale factor exponent _s_ for a scale factor 10^_s_. This
  is either the value of the associated scale factor data point or zero for
  numerical values not having an explicit scale factor assigned.

- `unit` is a textual representation of the data point's unit which does not
  go into abstract data representation

- `unitEncoded` is the DLMS code of the unit assigned with this value.
  Numerical data points which do not have an explicit unit assigned in the
  model will have the DLMS unit code 255 for _unitless_ as used by the meter in
  such a case.

- `value` is the unscaled integer value of the measurand

- `valueType` describes the data type used for the abstract data
  representation. It's either _Integer32_, _UnsignedInteger_, or _String_
  referring to the actual type used for the abstract data representation.

- `valueEncoding` gives the string encoding used for abstract data
  representation. The encodings `UTF-8` and `ISO-8859-1` are supported as of
  now.

Fields not explicitly given are assumed to be `null` when processing the data.

But `value` represents just one snapshot data point. For signature
verification, all [relevant snapshot data
points](../../bauer_bsm/bsm/models/smdx_64901.xml) are provided in the array
`addtionalValues` in the order they contributed to the signed message digest.
The follow the structure of `value` and the reference cumulative register is
included for indicating its position.


##### Abstract Data Representation Example

The [`value` object from the end snapshot](data/ev-charging-chargy.json#L273)
```json
"value": {
  "measurand": {
    "id": "1-0:1.8.0*198",
    "name": "RCR"
  },
  "measuredValue": {
    "scale": 0,
    "unit": "WATT_HOUR",
    "unitEncoded": 30,
    "value": 160,
    "valueType": "UnsignedInteger32"
  }
},
```
with a raw value of 160 = 0xa0, a scale factor exponent 0, and the unit code 30
= 0x1e would translate to to the abstract representation:
```
000000a0 00 1e
```

The string from _Meta1_
```json
{
  "measurand": {
    "name": "Meta1"
  },
  "measuredValue": {
    "unitEncoded": 255,
    "value": "contract-id: rfid:12345678abcdef",
    "valueType": "String",
    "valueEncoding": "ISO-8859-1"
  }
},
```
would simply translate to its length and string value encoded as [ISO
8859-1/Latin 1](https://en.wikipedia.org/wiki/ISO/IEC_8859-1):
```
00000020 636f6e74726163742d69643a20726669643a3132333435363738616263646566
```



##### Signature

Finally, `signature` provides the snapshot's signature data as described in
[Signature](snapshots.md#signature).



#### Signature Verification

To verify the signature of a snapshot from `signedMeterValues`, build the
[abstract data representation](snapshots.md#abstract-data-representation) and
follow the procedures given in [Snapshot
Verification](snapshots.md#snapshot-verification).

Several pieces of information from the snapshots are also presented in the
unsigned part of a Chargy JSON document. To completely verify the document,
these pieces have to be checked against their source from the actual snapshot
data in the `additionalValues` array. In case of the above JSON format these
are:

- `.chargePointInfo.evseId` if it matches the value tagged with `evse-id` from
  one of the metadata fields

- `.chargingStationInfo.controllerSoftware` if it matches the value tagged with
  `csc-sw-version` supplied in one of the metadata fields

- `.signingMeterValues[].time` if it properly represents the time given by
  _Epoch_ and _TZO_ in the snapshot data

- `.signedMeterValues[].meterInfo.meterId` matches the value of _MA1_ from the
  snapshot data

- `.signedMeterValues[].contract` if it properly represents the value tagged
  with `contract-id` supplied in one of the metadata fields

- `.signedMeterValues[].measurementId` if it matches the response counter
  _RCnt_ from the snapshot data
