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

- [_Signed Turn-On Snapshot_](../../bauer_bsm/bsm/models/smdx_64902.xml)
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
    Vr: 1.8:33C4:DB63
    SN: 21070003
    DA: 42
```
```
--> 2a 03 9c44 0042 ada5
<-- 2a 03 84 424155455220457c656374726f6e69630000000000000000000000000000000042534d2d57533336412d4830312d313331312d3030303000000000000000000000000000000000000000000000000000312e383a333343343a444236330000003231303730303033000000000000000000000000000000000000000000000000002a8000 273a
```


#### Version Information and Public Key

Software version information and the meter's public key can be read from the Signing Meter instance:
```
$ bsmtool get bsm

bsm:
    fixed:
        ErrM: 00000000
        SNM: 21070003
        SNC: 000b57000060caaf
        VrM: 1.8:33C4:DB63
        VrC: 08d1aa3
        MA1: 001BZR1521070003
[...]
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        NPK: 48
        BPK: 91
    repeating blocks blob:
        PK (der): 3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254
```
```
--> 2a 03 9d07 0050 dd80
<-- 2a 03 a0 30303030303030303231303730303033000000000000000030303062353730303030363063616166312e383a333343343a4442363300000030386431616133000000000000000000303031425a52313532313037303030334632324334330000000000000000000000000000000000001a5a0000565a001beb725f7ecc3b007800002f8e001beb6600010000ffffffffffffffff8000ffffffffffffffff8000 ec49
--> 2a 03 9d57 0078 dd8f
<-- 2a 03 f0 63686172676549542075702031322a342c2069643a203132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000064656d6f206461746120320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 f371
--> 2a 03 9dcf 0064 5da9
<-- 2a 03 c8 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030005b3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c72540000000000 3c73
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
        TotWhImp: 88200 Wh
        W: 0.0 W
        MA1: 001BZR1521070003
        RCnt: 22107
        OS: 1829766 s
        Epoch: 1602145359 s
        TZO: 120 min
        EpochSetCnt: 12174
        EpochSetOS: 1829734 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 304502201a40c702753d715cc37e5aabbf706ed409e1aa01f8f19996b192a3276adecd72022100a4818e85690f00946c56569b92453ad9bf118fa3ae2a636629cdb8b89123f041
```
```
$ bsmtool get-snapshot stoffs
bsm_snapshot:
    fixed:
        Typ: 2
        St: 0
        RCR: 150 Wh
        TotWhImp: 88350 Wh
        W: 0.0 W
        MA1: 001BZR1521070003
        RCnt: 22108
        OS: 1830064 s
        Epoch: 1602145657 s
        TZO: 120 min
        EpochSetCnt: 12174
        EpochSetOS: 1829734 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 3045022100d7070dc074c9188ec1b957cb7a6b3a37d0c416b3c9f9eb49c01087c4a95e16e9022025aaee48fa55f93ed507d7565458fdfa118b1aa73632055401a9e324e1f28a20
```


### Chargy JSON Format

#### Overview

The charging data to be validated by Chargy gets passed as a JSON document,
like for example [`ev-charging-chargy.json`](data/ev-charging-chargy.json)
focussed on electric vehicle charging.

The root object contains a context marker (`@context`), a unique document ID
(`@id`), information about the place where charging took place (`placeInfo`)
and the snapshot data in the array `signedMeterValues`:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/charging-station-json-v0",
  "@id": "34158336-3909-48b2-bb6d-2dff2a87d9b4",
  "placeInfo": { ... },
  "signedMeterValues": [ ... ] "
}
```

The BSM Tool supports creating sample documents from already successfully
created start and end snapshots via:
```
$ bsmtool chargy stons stoffs
```
See [`chargy_command`](../../bauer_bsm/cli/bsmtool.py#L347) and
[`generate_chargy_json`](../../bauer_bsm/exporter/chargy.py#205) for the code
generating this sample documents.

Let's have a look at the root object's fields in the following sections.


#### Document Identification

The context marker is meant for identifying this type of document so that
processing it does not require in-depth checking of the document structure
beforehand.
```json
"@context": "https://www.chargeit-mobility.com/contexts/charging-station-json-v0"
```
As of now, this URL just serves as an identifier and no schema
information could be retrieved from this URL.

The document ID uniquely identifies a certain document or so to speak, a
charging process. This value is not provided by the meter and needs to be
generated for each document. It could be an UUID for example.
```json
"@id": "34158336-3909-48b2-bb6d-2dff2a87d9b4"
```

#### Place Information

The place information object [`placeInfo`](data/ev-charging-chargy.json#L4) provides information about the
charging point. This includes coordinates for easily displaying the location,
an address and the EVSE ID of the charging point:
```json
"placeInfo": {
  "geoLocation": {
    "lat": 48.03552,
    "lon": 10.50669
  },
  "address": {
    "street": "Breitenbergstr. 2",
    "town": "Mindelheim",
    "zipCode": "87719"
  },
  "evseId": "DE*BDO*E8025334492*2"
}
```
This is another piece of information which needs to be added when generating
the JSON document. It is not provided by the meter.


#### Snapshot Data

##### Overview

Finally, the array [`signedMeterValues`](data/ev-charging-chargy.json#L16)
contains snapshot data. Each item of this array represents a snapshot where the
first item is the start snapshot and the last one the end snapshot.

In contrast to [Document Identification](chargy.md#document-identification) and
[Place Information](chargy.md#place-information) which needs to be filled in by
the entity generating the Chargy JSON document, the data presented here is
completely taken from the meter.


##### Snapshot Objects

The JSON representation of a snapshot contains in analog to the root object a
context marker and a snapshot ID. For being unique, the latter contains the
meter ID [_MA1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L194) and the
snapshot's response counter
[_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L198). For example:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/bsm-ws36a-json-v0",
  "@id": "001BZR1521070003-22107",
  "timestamp": 1602145359,
  "timesstampLocal": { ... },
  "meterInfo": { ... },
  "contract": { ... },
  "measurementId": 22107,
  "value": { ... },
  "additionalValues": [ ... ],
  "signature": "..."
}
```

Let's examine the remaining fields in the following sections more in detail.


##### Snapshot Identification

There are two fields representing the point in time the snapshot was created:
```json
"timestamp": 1602145359,
"timestampLocal": {
  "timestamp": 1602152559,
  "localOffset": 120
},
```
`timestamp` gives the epoch time
[_Epoch_](../../bauer_bsm/bsm/models/smdx_64901.xml#L211) of its creation and
`timestampLocal` a localized timestamp and the timezone offset
[_TZO_](../../bauer_bsm/bsm/models/smdx_64901.xml#L216). In case the meter has
no valid epoch time information, these values will be `null`.

The field `measurementId` provides the meter's response counter
[_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L198) which is unique for
every created snapshot:
```json
"measurementId": 22107
```


##### Meter Information

The field [`meterInfo`](data/ev-charging-chargy.json#L25) provides an object
with information for identifying the meter
```json
"meterInfo": {
  "firmwareVersion": "1.8:33C4:DB63, 08d1aa3",
  "publicKey": "3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254",
  "meterId": "001BZR1521070003",
  "manufacturer": "BAUER Electronic",
  "type": "BSM-WS36A-H01-1311-0000"
},
```
with the following fields:

- `firmwareVersion` combining the software version information from
  [_VrM_](../../bauer_bsm/bsm/models/smdx_64900.xml#L58) and
  [_VrC_](../../bauer_bsm/bsm/models/smdx_64900.xml#L66)
- `publicKey` providing the meter's public key data from
  [_PK_](../../bauer_bsm/bsm/models/smdx_64900.xml#L220)
- `meterId` providing the meter ID
  [_MA1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L194)
- `manufacturer` providing the manufacturer name
  [_Mn_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml#L20)
- `type` providing the model name
  [_Md_](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml#L25)


##### Customer Identification

The object [`contract`](data/ev-charging-chargy.json#L32) provides customer
identification from [_Meta1_](../../bauer_bsm/bsm/models/smdx_64900.xml#L245).
As the BSM-WS36A does not know about the identification medium, `type` always
reads as `null`.
```json
"contract": {
  "id": "chargeIT up 12*4, id: 12345678abcdef",
}
```
In case _Meta1_ was not set when creating the snapshot, `id` will be `null`
too.


##### Snapshot Data Point Values

The object [`value`](data/ev-charging-chargy.json#L37) gives the meter's
reference cumulative register
[_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L169) as primary value for
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
}
```
The `measurand` objects gives describes the measurand by its name (data point
ID) and an OBIS ID (where available). The latter is not provided by the meter
and needs to be [inferred from the data point
ID](../../bauer_bsm/exporter/chargy.py#21) when generating the JSON document.

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

The [`value` object from the end snapshot](data/ev-charging-chargy.json#L282)
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
    "value": 150,
    "valueType": "UnsignedInteger32"
  }
},
```
with a raw value of 150 = 0x96, a scale factor exponent 0, and the unit code 30
= 0x1e would translate to to the abstract representation:
```
00000096 00 1e
```

The string from _Meta1_
```json
{
  "measurand": {
    "name": "Meta1"
  },
  "measuredValue": {
    "unitEncoded": 255,
    "value": "chargeIT up 12*4, id: 12345678abcdef",
    "valueType": "String",
    "valueEncoding": "ISO-8859-1"
  }
},
```
would simply translate to its length and string value encoded as [ISO
8859-1/Latin 1](https://en.wikipedia.org/wiki/ISO/IEC_8859-1):
```
00000024 63686172676549542075702031322a342c2069643a203132333435363738616263646566
```



##### Signature

Finally, `signature` provides the snapshot's signature data as described in
[Signature](snapshots.md#signature).



#### Signature Verification

To verify the signature of a snapshot from `signedMeterValues`, build the
[abstract data representation](snapshots.md#abstract-data-representation) and
follow the procedures given in [Snapshot
Verification](snapshots.md#snapshot-verification).
