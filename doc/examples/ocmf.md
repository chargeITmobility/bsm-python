# Open Charge Metering Format (OCMF)

[Signed Snapshots](snapshots.md) shows how to create and work with snapshots.
For each of them, the BSM-WS36A provides an additional representation in the
[Open Charge Metering Format
(OCMF)](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format).

The OCMF representation is generated from the actual snapshot data when reading
from the appropriate model. It contains a subset of the snapshot's information,
presents the same time information and response counter and gets signed individually.


## Snapshots and Their Associated OCMF Representation

Each line in the following table shows a snapshot with its associated OCMF
representation:

| Snapshot                 | Snapshot Model                                             | OCMF Representation           | OCMF Model                                             |
| ------------------------ | ---------------------------------------------------------- | ----------------------------- | ------------------------------------------------------ |
| Signed Current Snapshot  | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) | OCMF Signed Current Snapshot  | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml) |
| Signed Turn-On Snapshot  | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) | OCMF Signed Turn-On Snapshot  | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml) |
| Signed Turn-Off Snapshot | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) | OCMF Signed Turn-Off Snapshot | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml) |
| Signed Start Snapshot    | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) | OCMF Signed Start Snapshot    | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml) |
| Signed End Snapshot      | [bsm\_snapshot](../../bauer_bsm/bsm/models/smdx_64901.xml) | OCMF Signed End Snapshot      | [bsm\_ocmf](../../bauer_bsm/bsm/models/smdx_64903.xml) |

[Model Instances](modbus-interface.md#model-instances) shows these model
instances.


## Getting the OCMF Representation

Create the snapshot as shown in [Snapshot
Creation](snapshots.md#snapshot-creation) and just read its associated OCMF
model instance afterwards.


## Snapshot Data in OCMF

The OCMF representation includes
[_Meta1_](../../bauer_bsm/bsm/models/smdx_64901.xml#L33) as customer
identification data which needs to be set appropriately. The other metadata
fields _Meta2_ and _Meta2_ are provided as _X2_ and _X3_, if set.

The BSM-WS36A uses the reference cumulative register (OBIS ID 1-0:1.8.0\*198,
data point RCR) as _RV_ for the energy consumption in OCMF output. This
register gets reset when creating a _Signed Turn-On State_ and shows the actual
energy consumption at the time of crating _Signed Turn-Off Snapshot_. The
positive active energy (OBIS ID 1-0:1.8.0\*255, data point _TotWhImp_) is
included for informational purpose as _XV_.


## Example

### Preparation

Set time and some meta data:
```
$ bsmtool set bsm/epoch=1657267200 bsm/tzo=120
```
```
--> 2a 10 9d44 0003 06 62c7e4000078 8d85
<-- 2a 10 9d44 0003 e9aa
```
```
$ bsmtool set 'bsm/meta1=contract-id: rfid:12345678abcdef' 'bsm/meta2=evse-id: DE*BDO*E8025334492*2' 'bsm/meta3=csc-sw-version: v1.2.34'
```
```
--> 2a 10 9d57 0078 f0 636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000657673652d69643a2044452a42444f2a45383032353333343439322a320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 195c
<-- 2a 10 9d57 0078 584c
--> 2a 10 9dcf 0032 64 6373632d73772d76657273696f6e3a2076312e322e33340000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 f0c8
<-- 2a 10 9dcf 0032 5854
```

### Create Snapshot and Get OCMF Representation

- Trigger creating  _Signed Current Snapshot_ (not its OCMF representation)
    ```
    $ bsmtool create-snapshot scs
    ```
    ```
    --> 2a 10 9e4c 0001 02 0002 bca5
    <-- 2a 10 9e4c 0001 e9ed
    ```

- Poll snapshot status as shown in [Snapshot
  Creation](snapshots.md#snapshot-creation)


- When ready, read its OCMF representation from _OCMF Signed Current Snapshot_
    ```
    $ bsmtool get oscs
    bsm_ocmf:
        Typ: 0
        St: 0
        O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070006","GV":"1.9:32CA:AFF4, f1d3d06","PG":"T4278","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070006","IS":true,"IT":"UNDEFINED","ID":"contract-id: rfid:12345678abcdef","X2":"evse-id: DE*BDO*E8025334492*2","X3":"csc-sw-version: v1.2.34","RD":[{"TM":"2022-07-08T10:06:49,000+0200 S","TX":"C","RV":0.15,"RI":"1-0:1.8.0*198","RU":"kWh","XV":100.00,"XI":"1-0:1.8.0*255","XU":"kWh","XT":0,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3045022053d866c0085483057b3fb43aec935b53bf593a2eddcd1844a8e85d8a10bcebca022100ca22a89f45d7378ba1a3f48c5b5a390b3a15faf9dd3b2302e7a9b83e141ec212"}
    ```
    ```
    --> 2a 03 a341 0002 b040
    <-- 2a 03 04 00000000 6131
    --> 2a 03 a343 007d 5060
    <-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353231303730303036222c224756223a22312e393a333243413a414646342c2066316433643036222c225047223a225434323738222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353231303730303036222c224953223a747275652c224954223a22554e444546494e4544222c224944223a22636f6e747261 5a14
    --> 2a 03 a3c0 007d a188
    <-- 2a 03 fa 63742d69643a20726669643a3132333435363738616263646566222c225832223a22657673652d69643a2044452a42444f2a45383032353333343439322a32222c225833223a226373632d73772d76657273696f6e3a2076312e322e3334222c225244223a5b7b22544d223a22323032322d30372d30385431303a30363a34392c3030302b303230302053222c225458223a2243222c225256223a302e31352c225249223a22312d303a312e382e302a313938222c225255223a226b5768222c225856223a3130302e30302c225849223a22312d303a312e382e302a323535222c225855223a226b5768222c225854223a302c225254223a2241 e3a5
    --> 2a 03 a43d 007d 310c
    <-- 2a 03 fa 43222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a2233303435303232303533643836366330303835343833303537623366623433616563393335623533626635393361326564646364313834346138653835643861313062636562636130323231303063613232613839663435643733373862613161336634386335623561333930623361313566616639646433623233303265376139623833653134316563323132227d00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 233c
    --> 2a 03 a4ba 0079 80e6
    <-- 2a 03 f2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 443c
    ```


## Comparing Snapshot and OCMF Payload

### _Signed Current Snapshot_

This is the regular snapshot data which could be read from the meter.
```
$ bsmtool get scs
bsm_snapshot:
    fixed:
        Typ: 0
        St: 0
        RCR: 150.0 Wh
        TotWhImp: 100000.0 Wh
        W: 0.0 W
        MA1: 001BZR1521070006
        RCnt: 4278
        OS: 519624 s
        Epoch: 1657267609 s
        TZO: 120 min
        EpochSetCnt: 3139
        EpochSetOS: 519219 s
        DI: 1
        DO: 0
        Meta1: contract-id: rfid:12345678abcdef
        Meta2: evse-id: DE*BDO*E8025334492*2
        Meta3: csc-sw-version: v1.2.34
        Evt: 0
        NSig: 48
        BSig: 71
    repeating blocks blob:
        Sig: 3045022100c72ce46d0c5810427eeefdfb477a5444aaac8e403b83017eed840f8eb3bc311302207136629f96464773456895a330165154df038d91f61656c0a7f8607ee06c68b2
```
```
--> 2a 03 9e4b 0064 1dc4
<-- 2a 03 c8 000000000000000f00002710000100000001303031425a5231353231303730303036000010b60007edc862c7e599007800000c430007ec3300010000636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 3f20
--> 2a 03 9eaf 007d 9c39
<-- 2a 03 fa 657673652d69643a2044452a42444f2a45383032353333343439322a3200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006373632d73772d76657273696f6e3a2076312e322e3334000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000473045022100c72ce46d0c5810427eeefdfb477a5444aaac8e403b83017eed840f8eb3bc31130220713662 15ee
--> 2a 03 9f2c 001b ec07
<-- 2a 03 36 9f96464773456895a330165154df038d91f61656c0a7f8607ee06c68b200000000000000000000000000000000000000000000000000 51cf
```

### OCMF JSON Payload

This is its derived OCMF representation. To get a better view on the JSON
payload of the OCMF data, it could be pretty-printed using some shell tooling
and [`jq`](https://stedolan.github.io/jq/) as shown below.
```json
{
  "FV": "1.0",
  "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
  "GS": "001BZR1521070006",
  "GV": "1.9:32CA:AFF4, f1d3d06",
  "PG": "T4278",
  "MV": "BAUER Electronic",
  "MM": "BSM-WS36A-H01-1311-0000",
  "MS": "001BZR1521070006",
  "IS": true,
  "IT": "UNDEFINED",
  "ID": "contract-id: rfid:12345678abcdef",
  "X2": "evse-id: DE*BDO*E8025334492*2",
  "X3": "csc-sw-version: v1.2.34",
  "RD": [
    {
      "TM": "2022-07-08T10:06:49,000+0200 S",
      "TX": "C",
      "RV": 0.15,
      "RI": "1-0:1.8.0*198",
      "RU": "kWh",
      "XV": 100,
      "XI": "1-0:1.8.0*255",
      "XU": "kWh",
      "XT": 0,
      "RT": "AC",
      "EF": "",
      "ST": "G"
    }
  ]
}
```
The current draft of the [Open Charge Metering Format
Specification](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format/blob/176d59b7e4cf6eecbbdcbb056a08fdb201ed8ff5/OCMF-de.md#sektionen)
explains the standard keys used here. Reading value is the reference cumulative register _RCR_:

- _RV_: its actual value [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L19)
- _RI_: _RCR_'s OBIS ID
- _RU_: _RCR_'s [unit](../../bauer_bsm/bsm/models/smdx_64901.xml#L19)

In addition, four vendor-specific keys are used in the reading data:

- _XV_: the additional total watt hours imported counter [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L20)
- _XI_: _TotWhImp_'s OBIS ID
- _XU_: _TotWhImp_'s [unit](../../bauer_bsm/bsm/models/smdx_64901.xml#L20)
- _XT_: the underlying snapshot's type [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L4)

The metadata is provided in the following fields:

- _ID_: the data from _Meta1_
- _X2_: the data from _Meta2_
- _X3_: the data from _Meta3_


## OCMF XML

In the context of electric vehicle charging, OCMF data gets usually validated
by a so-called Transparenzsoftware. There are several implementations at the
market and among them the [S.A.F.E. e.V.
Transparenzsoftware](https://www.safe-ev.de/de/transparenzsoftware.php) which
uses an XML envelope.

The XML envelope includes the OCMF data taken before starting and after
terminating the charging process along with the public key used for signing.
The format could be generated from a
[template](../../bauer_bsm/exporter/ocmf.py#L48) where the actual data gets
inserted.


### Generating OCMF XML

The [BSM Python support](../../bauer_bsm/exporter/ocmf.py#L12) and the [BSM
Tool](../../bauer_bsm/cli/bsmtool.py#L419) support the generation of OCMF XML
data for the OCMF representation of a pair of already created snapshots (the
switching snapshots _OCMF Signed Turn-On Snapshot_ and _OCMF Signed Turn-Off
Snapshot_ or the non-switching _OCMF Signed Start Snapshot_ and _OCMF Signed
End Snapshot_). To generate an OCMF XML envelope for the switching snapshots,
invoke the BSM Tool as follows:

- Create _Signed Turn-On Snapshot_
    ```
    $ bsmtool get-snapshot stons
    bsm_snapshot:
        fixed:
            Typ: 1
            St: 0
            RCR: None
            TotWhImp: 99840.0 Wh
            W: 0.0 W
            MA1: 001BZR1521070006
            RCnt: 4276
            OS: 519243 s
            Epoch: 1657267228 s
            TZO: 120 min
            EpochSetCnt: 3139
            EpochSetOS: 519219 s
            DI: 1
            DO: 0
            Meta1: contract-id: rfid:12345678abcdef
            Meta2: evse-id: DE*BDO*E8025334492*2
            Meta3: csc-sw-version: v1.2.34
            Evt: 0
            NSig: 48
            BSig: 70
        repeating blocks blob:
            Sig: 304402206abd76fb7c48676c8b020e5561ea7cb109025a10ad945fcb4bc712015b5cb59902202e3f0d6d5e02deaeff7fa7429619a5cdb0c637e73a343d45d60ce0829c93ca37
    ```

- Create _Signed Turn-Off Snapshot_
    ```
    $ bsmtool get-snapshot stoffs
    bsm_snapshot:
        fixed:
            Typ: 2
            St: 0
            RCR: 150.0 Wh
            TotWhImp: 100000.0 Wh
            W: 0.0 W
            MA1: 001BZR1521070006
            RCnt: 4277
            OS: 519567 s
            Epoch: 1657267552 s
            TZO: 120 min
            EpochSetCnt: 3139
            EpochSetOS: 519219 s
            DI: 1
            DO: 0
            Meta1: contract-id: rfid:12345678abcdef
            Meta2: evse-id: DE*BDO*E8025334492*2
            Meta3: csc-sw-version: v1.2.34
            Evt: 0
            NSig: 48
            BSig: 72
        repeating blocks blob:
            Sig: 3046022100ef2c86c28019f485dcb60424c8d29223f8a6c5b32c36bdc98c85677072c5a5d202210086e9512cedde2225d3e8a2094b10c5a0a7b9c1adb77eb9492c5c9f0dddcd77f3
    ```

- Generate OCMF XML envelope for both snapshots by reading both OCMF instances and wrapping them
    ```xml
    $ bsmtool ocmf-xml ostons ostoffs
    <?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>
    <values>
      <value transactionId="1" context="Transaction.Begin">
        <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070006","GV":"1.9:32CA:AFF4, f1d3d06","PG":"T4276","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070006","IS":true,"IT":"UNDEFINED","ID":"contract-id: rfid:12345678abcdef","X2":"evse-id: DE*BDO*E8025334492*2","X3":"csc-sw-version: v1.2.34","RD":[{"TM":"2022-07-08T10:00:28,000+0200 S","TX":"B","RV":0.00,"RI":"1-0:1.8.0*198","RU":"kWh","XV":99.84,"XI":"1-0:1.8.0*255","XU":"kWh","XT":1,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3046022100b63d4125929dc1ab354171570c37de579f961c4ddf1b301db1cfa035b3a96d16022100b6cb9fb98164a400181dc240ff7333e94cfd0742aa634e47e7a4c1fd62c695b5"}</signedData>
        <publicKey encoding="plain">3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254</publicKey>
      </value>
      <value transactionId="1" context="Transaction.End">
        <signedData format="OCMF" encoding="plain">OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070006","GV":"1.9:32CA:AFF4, f1d3d06","PG":"T4277","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070006","IS":true,"IT":"UNDEFINED","ID":"contract-id: rfid:12345678abcdef","X2":"evse-id: DE*BDO*E8025334492*2","X3":"csc-sw-version: v1.2.34","RD":[{"TM":"2022-07-08T10:05:52,000+0200 S","TX":"E","RV":0.15,"RI":"1-0:1.8.0*198","RU":"kWh","XV":100.00,"XI":"1-0:1.8.0*255","XU":"kWh","XT":2,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3044022014f0be0063d22f3b847218f42cd2a852f6d2a487c6668160613ce5542787c10302206f83d65044da4874da4e671742e4de5236202d52f4bd4d9fca4130bd16ef76dc"}</signedData>
        <publicKey encoding="plain">3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c7254</publicKey>
      </value>
    </values>
    ```
    ```
    --> 2a 03 9d07 0050 dd80
    <-- 2a 03 a0 30303030303030303231303730303036000000000000000030303062353730303030363063616131312e393a333243413a4146463400000066316433643036000000000000000000303031425a5231353231303730303036463046314433000000000000000000000000000f000100000ca9000010b50007edbb62c7e58c007800000c430007ec33000100000007ed8a62c7e55b00780007ed8a62c7e55b0078 e4e3
    --> 2a 03 9d57 0078 dd8f
    <-- 2a 03 f0 636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000657673652d69643a2044452a42444f2a45383032353333343439322a320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 4ec6
    --> 2a 03 9dcf 0064 5da9
    <-- 2a 03 c8 6373632d73772d76657273696f6e3a2076312e322e333400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030005b3059301306072a8648ce3d020106082a8648ce3d030107034200044bfd02c1d85272ceea9977db26d72cc401d9e5602faeee7ec7b6b62f9c0cce34ad8d345d5ac0e8f65deb5ff0bb402b1b87926bd1b7fc2dbc3a9774e8e70c72540000000000 95c8
    --> 2a 03 a535 0002 f0d2
    <-- 2a 03 04 00010000 30f1
    --> 2a 03 a537 007d 10f2
    <-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353231303730303036222c224756223a22312e393a333243413a414646342c2066316433643036222c225047223a225434323736222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353231303730303036222c224953223a747275652c224954223a22554e444546494e4544222c224944223a22636f6e747261 9670
    --> 2a 03 a5b4 007d e11a
    <-- 2a 03 fa 63742d69643a20726669643a3132333435363738616263646566222c225832223a22657673652d69643a2044452a42444f2a45383032353333343439322a32222c225833223a226373632d73772d76657273696f6e3a2076312e322e3334222c225244223a5b7b22544d223a22323032322d30372d30385431303a30303a32382c3030302b303230302053222c225458223a2242222c225256223a302e30302c225249223a22312d303a312e382e302a313938222c225255223a226b5768222c225856223a39392e38342c225849223a22312d303a312e382e302a323535222c225855223a226b5768222c225854223a312c225254223a224143 c48e
    --> 2a 03 a631 007d f0b7
    <-- 2a 03 fa 222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a22333034363032323130306236336434313235393239646331616233353431373135373063333764653537396639363163346464663162333031646231636661303335623361393664313630323231303062366362396662393831363461343030313831646332343066663733333365393463666430373432616136333465343765376134633166643632633639356235227d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 a33c
    --> 2a 03 a6ae 0079 c15a
    <-- 2a 03 f2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 443c
    --> 2a 03 a729 0002 30ac
    <-- 2a 03 04 00020000 c0f1
    --> 2a 03 a72b 007d d08c
    <-- 2a 03 fa 4f434d467c7b224656223a22312e30222c224749223a22424155455220456c656374726f6e69632042534d2d57533336412d4830312d313331312d30303030222c224753223a22303031425a5231353231303730303036222c224756223a22312e393a333243413a414646342c2066316433643036222c225047223a225434323737222c224d56223a22424155455220456c656374726f6e6963222c224d4d223a2242534d2d57533336412d4830312d313331312d30303030222c224d53223a22303031425a5231353231303730303036222c224953223a747275652c224954223a22554e444546494e4544222c224944223a22636f6e747261 5be0
    --> 2a 03 a7a8 007d 2164
    <-- 2a 03 fa 63742d69643a20726669643a3132333435363738616263646566222c225832223a22657673652d69643a2044452a42444f2a45383032353333343439322a32222c225833223a226373632d73772d76657273696f6e3a2076312e322e3334222c225244223a5b7b22544d223a22323032322d30372d30385431303a30353a35322c3030302b303230302053222c225458223a2245222c225256223a302e31352c225249223a22312d303a312e382e302a313938222c225255223a226b5768222c225856223a3130302e30302c225849223a22312d303a312e382e302a323535222c225855223a226b5768222c225854223a322c225254223a2241 b5c1
    --> 2a 03 a825 007d b25b
    <-- 2a 03 fa 43222c224546223a22222c225354223a2247227d5d7d7c7b225341223a2245434453412d7365637032353672312d534841323536222c225344223a223330343430323230313466306265303036336432326633623834373231386634326364326138353266366432613438376336363638313630363133636535353432373837633130333032323036663833643635303434646134383734646134653637313734326534646535323336323032643532663462643464396663613431333062643136656637366463227d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 cb1f
    --> 2a 03 a8a2 0079 03b1
    <-- 2a 03 f2 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 443c
    ```


### Example OCMF XML Payload

- Start
    ```json
    {
      "FV": "1.0",
      "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
      "GS": "001BZR1521070006",
      "GV": "1.9:32CA:AFF4, f1d3d06",
      "PG": "T4276",
      "MV": "BAUER Electronic",
      "MM": "BSM-WS36A-H01-1311-0000",
      "MS": "001BZR1521070006",
      "IS": true,
      "IT": "UNDEFINED",
      "ID": "contract-id: rfid:12345678abcdef",
      "X2": "evse-id: DE*BDO*E8025334492*2",
      "X3": "csc-sw-version: v1.2.34",
      "RD": [
        {
          "TM": "2022-07-08T10:00:28,000+0200 S",
          "TX": "B",
          "RV": 0,
          "RI": "1-0:1.8.0*198",
          "RU": "kWh",
          "XV": 99.84,
          "XI": "1-0:1.8.0*255",
          "XU": "kWh",
          "XT": 1,
          "RT": "AC",
          "EF": "",
          "ST": "G"
        }
      ]
    }
    ```

- End
    ```json
    {
      "FV": "1.0",
      "GI": "BAUER Electronic BSM-WS36A-H01-1311-0000",
      "GS": "001BZR1521070006",
      "GV": "1.9:32CA:AFF4, f1d3d06",
      "PG": "T4277",
      "MV": "BAUER Electronic",
      "MM": "BSM-WS36A-H01-1311-0000",
      "MS": "001BZR1521070006",
      "IS": true,
      "IT": "UNDEFINED",
      "ID": "contract-id: rfid:12345678abcdef",
      "X2": "evse-id: DE*BDO*E8025334492*2",
      "X3": "csc-sw-version: v1.2.34",
      "RD": [
        {
          "TM": "2022-07-08T10:05:52,000+0200 S",
          "TX": "E",
          "RV": 0.15,
          "RI": "1-0:1.8.0*198",
          "RU": "kWh",
          "XV": 100,
          "XI": "1-0:1.8.0*255",
          "XU": "kWh",
          "XT": 2,
          "RT": "AC",
          "EF": "",
          "ST": "G"
        }
      ]
    }
    ```


### OCMF XML Verification

The OCMF XML envelope [`ev-charging-ocmf.xml`](data/ev-charging-ocmf.xml) from
the example above can be verified with the [S.A.F.E. e.V.
Transparenzsoftware](https://www.safe-ev.de/de/transparenzsoftware.php) which
by loading the file and clicking on _Transaktion überprüfen_:

![S.A.F.E. e.V. Transparenzsoftware Main Window](img/ev-charging-ocmf-verification-overview.png)
![S.A.F.E. e.V. Transparenzsoftware Verification Details](img/ev-charging-ocmf-verification-detail.png)
