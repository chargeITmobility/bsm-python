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
generating Chargy's JSON format:

| Label                    | Model                                                                                                         | Notes                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Common                   | [common](https://github.com/sunspec/models/blob/8b44dc5c77e601b6acbb8c3153fb4e54ae3617e9/smdx/smdx_00001.xml) | nameplate information            |
| Signing Meter            | [bsm](../../bauer_bsm/bsm/models/smdx_64900.xml)                                                              | public key and software versions |
| Signed Turn-On Snapshot  | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml)                                                    | start snapshot data              |
| Signed Turn-Off Snapshot | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml)                                                    | end snapshot data                |


#### Nameplate Information

Reading the nameplate information from the common model is straight forward:
```
$ bsmtool get cb
common:
    Mn: BAUER Electronic
    Md: BSM-WS36A-H01-1311-0000
    Opt: None
    Vr: 1.7:97B4:505A
    SN: 20200007
    DA: 42
```
```
--> 2a 03 9c44 0042 ada5
<-- 2a 03 84 424155455220456c656374726f6e69630000000000000000000000000000000042534d2d57533336412d4830312d313331312d3030303000000000000000000000000000000000000000000000000000312e373a393742343a353035410000003230323030303037000000000000000000000000000000000000000000000000002a8000 ab75
```


#### Version Information and Public Key

Software version information and the meter's public key can be read from the Signing Meter instance:
```
$ bsmtool get bsm
bsm:
    fixed:
        ErrM: 00000000
        SNM: 20200007
        SNC: 000b57000060cb05
        VrM: 1.7:97B4:505A
        VrC: d939f6f
        MA1: 001BZR1520200007
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
<-- 2a 03 a0 30303030303030303230323030303037000000000000000030303062353730303030363063623035312e373a393742343a3530354100000064393339663666000000000000000000303031425a5231353230323030303037303430303432000000000000000000000000009600000000024f00000811000563955feee5e8003c000000e00005624000010000000563855feee5d8003c000563845feee5d7003c ca44
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

- [Creating the Signed Turn-Off Snapshot](ev-charging.md#creating-the-signed-turn-on-snapshot)
- [Key Start Snapshot Data Points](ev-charging.md#key-start-snapshot-data-points)
- [Creating the Signed Turn-Off Snapshot](ev-charging.md#creating-the-signed-turn-off-snapshot)
- [Key End Snapshot Data Points](ev-charging.md#key-end-snapshot-data-points)

So we just show the interpreted snapshot data one more time:
```
$ bsmtool get stons
bsm_snapshot:
    fixed:
        Typ: 1
        St: 0
        RCR: None
        TotWhImp: 14430 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 2064
        OS: 352851 s
        Epoch: 1609491622 s
        TZO: 60 min
        EpochSetCnt: 224
        EpochSetOS: 352832 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 70
    repeating blocks blob:
        Sig: 304402201bfb63da4a6ea54d5dec4579cb029d435b9391e85587905d740d711867650860022008f16665b60dedeccb0bb061c49b8bb68e24754c600269f6a74bd020e72caf2e
```
```
$ bsmtool get stoffs
bsm_snapshot:
    fixed:
        Typ: 2
        St: 0
        RCR: 150 Wh
        TotWhImp: 14590 Wh
        W: 0.0 W
        MA1: 001BZR1520200007
        RCnt: 2065
        OS: 353162 s
        Epoch: 1609491933 s
        TZO: 60 min
        EpochSetCnt: 224
        EpochSetOS: 352832 s
        DI: 1
        DO: 0
        Meta1: chargeIT up 12*4, id: 12345678abcdef
        Meta2: demo data 2
        Meta3: None
        Evt: 0
        NSig: 48
        BSig: 70
    repeating blocks blob:
        Sig: 304402204fb0de8e38e9e23ebe52e2b15397fe1313cd4753b88b0920b58edad6127448a80220408a02dc0f65545637201f912c7e0107669149f60722e8365ba0b1f5f25936bb
```


### Chargy JSON Format

#### Overview

The charging data to be validated by Chargy gets passed as a JSON document,
like for example [`ev-charging-chargy.json`](data/ev-charging-chargy.json)
focussed on electric vehicle charging.

The root object contains a context marker (`@context`), a unique document ID
(`@id`), information about the place where charging took place (`placeInfo`)
and the snapshot data in the array `@signedMeterValues`:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/charging-station-json-v0",
  "@id": "75446ca2-0865-4684-8d24-b0b60486f686",
  "placeInfo": { ... },
  "signedMeterValues": [ ... ] "
}
```

The BSM Tool supports creating sample documents from already successfully
created start and end snapshots via:
```
$ bsmtool chargy
```
See [`chargy_command`](../../bauer_bsm/cli/bsmtool.py#L347) and
[`generate_chargy_json`](../../bauer_bsm/exporter/chargy.py#205) for the code
generating this sample documents.

Let's have a look at the root object's fields in the following sections.


#### Type and Document Identification

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
"@id": "75446ca2-0865-4684-8d24-b0b60486f686"
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


##### Snapshot Objects

The JSON representation of a snapshot contains in analog to the root object a
context marker and a snapshot ID. For being unique, the latter contains the
meter ID [_MA1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L194) and the
snapshot's response counter
[_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L198). For example:
```json
{
  "@context": "https://www.chargeit-mobility.com/contexts/bsm-ws36a-json-v0",
  "@id": "001BZR1520200007-2064",
  "timestamp": 1609491622,
  "timesstampLocal": { ... },
  "meterInfo": { ... },
  "contract": { ... },
  "measurementId": 2064,
  "value": { ... },
  "additionalValues": [ ...  ],
  "signature": "..."
}
```

Let's examine the remaining fields in the following sections more in detail.


##### Snapshot Identification

There are two fields representing the point in time the snapshot was created:
```json
"timestamp": 1609491622,
"timesstampLocal": {
  "timestamp": 1609491622,
  "localOffset": 60
}
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
"measurementId": 2064
```


##### Meter Information

The field [`meterInfo`](data/ev-charging-chargy.json#L25) provides an object
with information for identifying the meter
```json
"meterInfo": {
  "firmwareVersion": "1.7:97B4:505A, d939f6f",
  "publicKey": "3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254",
  "meterId": "001BZR1520200007",
  "manufacturer": "BAUER Electronic",
  "type": "BSM-WS36A-H01-1311-0000"
}
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
  "type": null
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

But `value` represents just one snapshot data point. For signature
verification, all [relevant snapshot data
points](../../bauer_bsm/bsm/models/smdx_64901.xml) are provided in the array
`addtionalValues` in the order they contributed to the signed message digest.
The follow the structure of `value` and the reference cumulative register is
included for indicating its position.


##### Signature

Finally, `signature` provides the snapshot's signature data as described in
[Signature](snapshots.md#signature).



#### Signature Verification

To verify the signature of a snapshot from `signedMeterValues`, build the
[abstract data representation](snapshots.md#abstract-data-representation) and
follow the procedures given in [Snapshot
Verification](snapshots.md#snapshot-verification).
