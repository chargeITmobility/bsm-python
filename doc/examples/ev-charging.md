# Electric Vehicle Charging

The BSM-WS36A facilitates setting up electric vehicle charging applications in
three ways:

1. Taking and signing snapshots of data relevant for billing
2. Its ability to directly control an external contactor for controlling energy
   delivery and its controlled operation for recording snapshot data with the
   contactor turned off
3. Direct output of
   [OCMF](https://github.com/SAFE-eV/OCMF-Open-Charge-Metering-Format) data
   allowing end-user validation of billing data with commonly used and
   available software without the need for separate signing

The following sections demonstrate how to make use of them.


## Typical Setup

Core components of an electric vehicle charging application are the meter
itself and a contactor with appropriate auxiliary contacts for providing
feedback. [Hardware Setup](prerequisites.md#hardware-setup) shows the
single-phase setup we in the example below:

![Demo and Development Setup](img/bsm-demo-box-schematic-20210204.png)

For charging electric cars, a three-phase installation is more common though.

If epoch time information is important for billing, an external controller is
required for providing it to the meter on a regular basis as described in
[Setting and Updating Time](time.md).


## Charging Scenario

### Overview

This example shows aspects of a typical charging scenario as sketched below:

![EV Charging](img/overview-charging.png)

The backend in this example generates OCMF-XML envelopes for billing data. But
every data format which implicitly or explicitly supports passing the actual
signed data could be generated from the snapshot data.


### Updating Time Information

The time information is assumed to be up to date. It could be set and updated
as described in [Setting and Updating Time](time.md). This needs to be done on
a regular basis.

shown below:
```
$ bsmtool set bsm/epoch=1657267200 bsm/tzo=120
```
```
--> 2a 10 9d44 0003 06 62c7e4000078 8d85
<-- 2a 10 9d44 0003 e9aa
```


### Setting Identification Data

The BSM-WS36A provides three string [metadata points](snapshots.md#metadata)
_Meta1_, _Meta2_ and _Meta3_ which get recorded and signed when creating a
snapshot.

These three data points could be used according to the application's needs when
generating billing data from the regular snapshots. When using the meter's OCMF
representation, only _Meta1_ will be included as customer identification data
_ID_.

This example sets and uses the following demo data

- Customer identification data _contract-id: rfid:12345678abcdef_ set as _Meta1_
- The EVSE ID _evse-id: DE*BDO*E8025334492*2_ set as _Meta2_
- The charging station software version _csc-sw-version: v1.2.34_ as _Meta3_

where _12345678abcdef_ is meant to be the identification from a RFID
identification tag. This data could be set with the BSM Tool:
```
$ bsmtool set 'bsm/meta1=contract-id: rfid:12345678abcdef' 'bsm/meta2=evse-id: DE*BDO*E8025334492*2' 'bsm/meta3=csc-sw-version: v1.2.34'
```
```
--> 2a 10 9d57 0078 f0 636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000657673652d69643a2044452a42444f2a45383032353333343439322a320000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 195c
<-- 2a 10 9d57 0078 584c
--> 2a 10 9dcf 0032 64 6373632d73772d76657273696f6e3a2076312e322e33340000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 f0c8
<-- 2a 10 9dcf 0032 5854
```


### Start of Charging

Creating a _Signed Turn-On Snapshot_ starts the charging process by recording
the baseline data and turning on the contactor. [Snapshot
Creation](snapshots.md#snapshot-creation) gives the details about this
procedure.

This example uses the snapshot pair  _Signed Turn-On Snapshot_ and _Signed
Turn-Off Snapshot_ which switches an external contactor. Use the pair _Signed
Start Snapshot_ and _Signed End Snapshot_ in analog in case the meter does not
control an external contactor. See [Signed Snapshots](snapshots.md) for more
details.


#### Creating the _Signed Turn-On Snapshot_

Create and read the _Signed Turn-On Snapshot_ as follows:
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
```
--> 2a 03 9f49 0064 bdf8
<-- 2a 03 c8 000100000000000000002700000100000001303031425a5231353231303730303036000010b40007ec4b62c7e41c007800000c430007ec3300010000636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 eddd
--> 2a 03 9fad 007d 3c05
<-- 2a 03 fa 657673652d69643a2044452a42444f2a45383032353333343439322a3200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006373632d73772d76657273696f6e3a2076312e322e333400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000300046304402206abd76fb7c48676c8b020e5561ea7cb109025a10ad945fcb4bc712015b5cb59902202e3f0d6d 5880
--> 2a 03 a02a 001b 0012
<-- 2a 03 36 5e02deaeff7fa7429619a5cdb0c637e73a343d45d60ce0829c93ca370000000000000000000000000000000000000000000000000000 ead0
```

#### Key Start Snapshot Data Points

Let's have a quick look at its key data points:

- Type and status
    - This is a [_Signed Turn-On
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L6) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L80)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L131)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) which will show
      the energy consumption at the end has been reset to zero
    - [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L193) gives the
      total energy consumption tracked by this meter and could be used for
      computing the energy consumption of the actual charging process as the
      delta between start and end
    - It was taken with no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L201) = 0 Wh) as it
      should be the case with the contactor turned off
- Time and counters
    - Let's remember the response counter
      [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L214) 4,276 for later
    - It has valid time information in _Epoch_ and _TZO_
- Metadata points _Meta1_ and _Meta2_ contain the previously set metadata


#### Start Snapshot Register Dump

The register dump (protocol addresses) of the start snapshot looks as follows:
```
$ bsmtool dump 40775 254
   40775: fd85 00fc 0001 0000 0000 0000 0000 2700  ..............'.
   40783: 0001 0000 0001 3030 3142 5a52 3135 3231  ......001BZR1521
   40791: 3037 3030 3036 0000 10b4 0007 ec4b 62c7  070006.......Kb.
   40799: e41c 0078 0000 0c43 0007 ec33 0001 0000  ...x...C...3....
   40807: 636f 6e74 7261 6374 2d69 643a 2072 6669  contract-id: rfi
   40815: 643a 3132 3334 3536 3738 6162 6364 6566  d:12345678abcdef
   40823: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40831: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40839: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40847: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40855: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40863: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40871: 0000 0000 0000 0000 0000 0000 6576 7365  ............evse
   40879: 2d69 643a 2044 452a 4244 4f2a 4538 3032  -id: DE*BDO*E802
   40887: 3533 3334 3439 322a 3200 0000 0000 0000  5334492*2.......
   40895: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40903: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40911: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40919: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40927: 6373 632d 7377 2d76 6572 7369 6f6e 3a20  csc-sw-version: 
   40935: 7631 2e32 2e33 3400 0000 0000 0000 0000  v1.2.34.........
   40943: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40951: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40959: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40967: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   40975: 0000 0000 0000 0000 0030 0046 3044 0220  .........0.F0D. 
   40983: 6abd 76fb 7c48 676c 8b02 0e55 61ea 7cb1  j.v.|Hgl...Ua.|.
   40991: 0902 5a10 ad94 5fcb 4bc7 1201 5b5c b599  ..Z..._.K...[\..
   40999: 0220 2e3f 0d6d 5e02 deae ff7f a742 9619  . .?.m^......B..
   41007: a5cd b0c6 37e7 3a34 3d45 d60c e082 9c93  ....7.:4=E......
   41015: ca37 0000 0000 0000 0000 0000 0000 0000  .7..............
   41023: 0000 0000 0000 0000 0000 0000            ............
```


#### Start OCMF Representation

The snapshot is valid and so its OCMF representation could be read from _OCMF
Signed Turn-On Snapshot_ with the BSM Tool:
```
$ bsmtool get ostons
bsm_ocmf:
    Typ: 1
    St: 0
    O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070006","GV":"1.9:32CA:AFF4, f1d3d06","PG":"T4276","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070006","IS":true,"IT":"UNDEFINED","ID":"contract-id: rfid:12345678abcdef","X2":"evse-id: DE*BDO*E8025334492*2","X3":"csc-sw-version: v1.2.34","RD":[{"TM":"2022-07-08T10:00:28,000+0200 S","TX":"B","RV":0.00,"RI":"1-0:1.8.0*198","RU":"kWh","XV":99.84,"XI":"1-0:1.8.0*255","XU":"kWh","XT":1,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3046022100b63d4125929dc1ab354171570c37de579f961c4ddf1b301db1cfa035b3a96d16022100b6cb9fb98164a400181dc240ff7333e94cfd0742aa634e47e7a4c1fd62c695b5"}
```
```
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
```


#### Key Start OCMF Values

[Pretty-printed](ocmf.md#ocmf-json-payload), the _OCMF Signed Turn-On
Snapshot_'s payload looks like:
```json
$ bsmtool get ostons/o | cut -d \| -f 2 | jq .
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

Let's have a quick look at its key data points too:

- Type and status
    - Its type is indicated by the transaction _TX_ = _B_ (for beginning)
    - Its status _ST_ indicates that it is _good_ = _G_
- Power and energy
    - The reference cumulative register is used as the primary reading value
      _RV_
    - The total energy consumption is given as the additional value _XV_
    - The OCMF data does not contain the active power
- Time and counters
    - It provides the response counter as the snapshot in _PG_ (for pagination)
      prefixed with _T_ for a reading in a transactional context
    - Epoch time information is given in ISO 8601 format instead of epoch
      seconds and timezone offset
- _Meta1_ is used as identification data _ID_ and the identification type
  always _IT_ always returns _UNDEFINED_
- _Meta2_ and _Meta3_ are provided as _X2_ and _X3_


#### Start OCMF Register Dump

The register dump of the start snapshot's OCMF representation looks as follows:
```
$ bsmtool dump 42291 500
   42291: fd87 01f2 0001 0000 4f43 4d46 7c7b 2246  ........OCMF|{"F
   42299: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   42307: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic 
   42315: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   42323: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   42331: 3031 425a 5231 3532 3130 3730 3030 3622  01BZR1521070006"
   42339: 2c22 4756 223a 2231 2e39 3a33 3243 413a  ,"GV":"1.9:32CA:
   42347: 4146 4634 2c20 6631 6433 6430 3622 2c22  AFF4, f1d3d06","
   42355: 5047 223a 2254 3432 3736 222c 224d 5622  PG":"T4276","MV"
   42363: 3a22 4241 5545 5220 456c 6563 7472 6f6e  :"BAUER Electron
   42371: 6963 222c 224d 4d22 3a22 4253 4d2d 5753  ic","MM":"BSM-WS
   42379: 3336 412d 4830 312d 3133 3131 2d30 3030  36A-H01-1311-000
   42387: 3022 2c22 4d53 223a 2230 3031 425a 5231  0","MS":"001BZR1
   42395: 3532 3130 3730 3030 3622 2c22 4953 223a  521070006","IS":
   42403: 7472 7565 2c22 4954 223a 2255 4e44 4546  true,"IT":"UNDEF
   42411: 494e 4544 222c 2249 4422 3a22 636f 6e74  INED","ID":"cont
   42419: 7261 6374 2d69 643a 2072 6669 643a 3132  ract-id: rfid:12
   42427: 3334 3536 3738 6162 6364 6566 222c 2258  345678abcdef","X
   42435: 3222 3a22 6576 7365 2d69 643a 2044 452a  2":"evse-id: DE*
   42443: 4244 4f2a 4538 3032 3533 3334 3439 322a  BDO*E8025334492*
   42451: 3222 2c22 5833 223a 2263 7363 2d73 772d  2","X3":"csc-sw-
   42459: 7665 7273 696f 6e3a 2076 312e 322e 3334  version: v1.2.34
   42467: 222c 2252 4422 3a5b 7b22 544d 223a 2232  ","RD":[{"TM":"2
   42475: 3032 322d 3037 2d30 3854 3130 3a30 303a  022-07-08T10:00:
   42483: 3238 2c30 3030 2b30 3230 3020 5322 2c22  28,000+0200 S","
   42491: 5458 223a 2242 222c 2252 5622 3a30 2e30  TX":"B","RV":0.0
   42499: 302c 2252 4922 3a22 312d 303a 312e 382e  0,"RI":"1-0:1.8.
   42507: 302a 3139 3822 2c22 5255 223a 226b 5768  0*198","RU":"kWh
   42515: 222c 2258 5622 3a39 392e 3834 2c22 5849  ","XV":99.84,"XI
   42523: 223a 2231 2d30 3a31 2e38 2e30 2a32 3535  ":"1-0:1.8.0*255
   42531: 222c 2258 5522 3a22 6b57 6822 2c22 5854  ","XU":"kWh","XT
   42539: 223a 312c 2252 5422 3a22 4143 222c 2245  ":1,"RT":"AC","E
   42547: 4622 3a22 222c 2253 5422 3a22 4722 7d5d  F":"","ST":"G"}]
   42555: 7d7c 7b22 5341 223a 2245 4344 5341 2d73  }|{"SA":"ECDSA-s
   42563: 6563 7032 3536 7231 2d53 4841 3235 3622  ecp256r1-SHA256"
   42571: 2c22 5344 223a 2233 3034 3630 3232 3130  ,"SD":"304602210
   42579: 3062 3633 6434 3132 3539 3239 6463 3161  0b63d4125929dc1a
   42587: 6233 3534 3137 3135 3730 6333 3764 6535  b354171570c37de5
   42595: 3739 6639 3631 6334 6464 6631 6233 3031  79f961c4ddf1b301
   42603: 6462 3163 6661 3033 3562 3361 3936 6431  db1cfa035b3a96d1
   42611: 3630 3232 3130 3062 3663 6239 6662 3938  6022100b6cb9fb98
   42619: 3136 3461 3430 3031 3831 6463 3234 3066  164a400181dc240f
   42627: 6637 3333 3365 3934 6366 6430 3734 3261  f7333e94cfd0742a
   42635: 6136 3334 6534 3765 3761 3463 3166 6436  a634e47e7a4c1fd6
   42643: 3263 3639 3562 3522 7d00 0000 0000 0000  2c695b5"}.......
   42651: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42659: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42667: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42675: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42683: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42691: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42699: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42707: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42715: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42723: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42731: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42739: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42747: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42755: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42763: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42771: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42779: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   42787: 0000 0000 0000 0000                      ........
```


### Intermediate Values

Intermediate values for the current charging process might be required for
example for displaying status information. There are two ways to get them:

- Just reading out the desired data points from the [AC
  Meter](modbus-interface.md#model-instances) and [_Signing
  Meter_](modbus-interface.md#model-instances) model instances

- Creating [_Signed Current Snapshot_](modbus-interface.md#model-instances)s

Both of them provide data suitable for status updates. The latter associates
energy consumption with a timestamp but increases the response counter so that
this one will reflect the number of intermediate snapshots taken at the end of
the charging process.


### End of Charging

Creating a _Signed Turn-Off Snapshot_ ends the charging process by turning of
the contactor and recoding the snapshot data. Again, [Snapshot Creation](snapshots.md#snapshot-creation) gives
the details about this procedure.


#### Creating the Signed Turn-Off Snapshot

Creating and reading the _Signed Turn-Off Snapshot_ works in analog to
[creating the _Signed Turn-On Snapshot_](#creating-the-signed-turn-on-snapshot)
and as follows:
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
```
--> 2a 03 a047 0064 d02f
<-- 2a 03 c8 000200000000000f00002710000100000001303031425a5231353231303730303036000010b50007ed8f62c7e560007800000c430007ec3300010000636f6e74726163742d69643a20726669643a3132333435363738616263646566000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 cbc8
--> 2a 03 a0ab 007d d010
<-- 2a 03 fa 657673652d69643a2044452a42444f2a45383032353333343439322a3200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006373632d73772d76657273696f6e3a2076312e322e3334000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003000483046022100ef2c86c28019f485dcb60424c8d29223f8a6c5b32c36bdc98c85677072c5a5d202210086e9 8a27
--> 2a 03 a128 001b a02e
<-- 2a 03 36 512cedde2225d3e8a2094b10c5a0a7b9c1adb77eb9492c5c9f0dddcd77f3000000000000000000000000000000000000000000000000 ace1
```


#### Key End Snapshot Data Points

Let's look one more time at the snapshot's key data points and compare them to
the _Signed Turn-On Snapshot_ taken at the start of charging:

- Type and status
    - This is a [_Signed Turn-Off
      Snapshot_](../../bauer_bsm/bsm/models/smdx_64901.xml#L7) as indicated by
      [_Typ_](../../bauer_bsm/bsm/models/smdx_64901.xml#L80)
    - It has been [created
      successfully](../../bauer_bsm/bsm/models/smdx_64901.xml#L12) according to
      its status [_St_](../../bauer_bsm/bsm/models/smdx_64901.xml#L131)
- Power and energy
    - The reference cumulative register
      [_RCR_](../../bauer_bsm/bsm/models/smdx_64901.xml#L185) started at zero
      and now shows the energy delivered during this charging process: 150 Wh
    - The total energy delivered,
      [_TotWhImp_](../../bauer_bsm/bsm/models/smdx_64901.xml#L193), increased
      from 99.84 kWh Wh to 100.00 kWh which is slightly (10 Wh) more than the
      consumption registerd by the reference cumulative registers. Due to the
      [internal state of _TotWhImp_](snapshots.md#energy-and-power) this
      difference can be one least significant digit larger than the value for
      _RCR_ (shown in the display).
    - Again, there is no active power
      ([_W_](../../bauer_bsm/bsm/models/smdx_64901.xml#L201) = 0 Wh) since
      power delivery got cut before recording the snapshot data
- Time and counters
    - The response counter
      [_RCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L214) 4,277 - one more
      than at the start
    - It has valid time information in _Epoch_ and _TZO_
    - [_EpochSetCnt_](../../bauer_bsm/bsm/models/smdx_64901.xml#L241) (with a
      value of 2,814) and
      [_EpochSetOS_](../../bauer_bsm/bsm/models/smdx_64901.xml#L246) (with a
      value of 3,139) are the same as in the start snapshot. So they are using
      the same time base originating from this same setting of time.
- Metadata is still the same as in _Signed Turn-On Snapshot_


#### End Snapshot Register Dump

The register dump of the end snapshot looks as follows
```
$ bsmtool dump 41029 254
   41029: fd85 00fc 0002 0000 0000 000f 0000 2710  ..............'.
   41037: 0001 0000 0001 3030 3142 5a52 3135 3231  ......001BZR1521
   41045: 3037 3030 3036 0000 10b5 0007 ed8f 62c7  070006........b.
   41053: e560 0078 0000 0c43 0007 ec33 0001 0000  .`.x...C...3....
   41061: 636f 6e74 7261 6374 2d69 643a 2072 6669  contract-id: rfi
   41069: 643a 3132 3334 3536 3738 6162 6364 6566  d:12345678abcdef
   41077: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41085: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41093: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41101: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41109: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41117: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41125: 0000 0000 0000 0000 0000 0000 6576 7365  ............evse
   41133: 2d69 643a 2044 452a 4244 4f2a 4538 3032  -id: DE*BDO*E802
   41141: 3533 3334 3439 322a 3200 0000 0000 0000  5334492*2.......
   41149: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41157: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41165: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41173: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41181: 6373 632d 7377 2d76 6572 7369 6f6e 3a20  csc-sw-version: 
   41189: 7631 2e32 2e33 3400 0000 0000 0000 0000  v1.2.34.........
   41197: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41205: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41213: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41221: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   41229: 0000 0000 0000 0000 0030 0048 3046 0221  .........0.H0F.!
   41237: 00ef 2c86 c280 19f4 85dc b604 24c8 d292  ..,.........$...
   41245: 23f8 a6c5 b32c 36bd c98c 8567 7072 c5a5  #....,6....gpr..
   41253: d202 2100 86e9 512c edde 2225 d3e8 a209  ..!...Q,.."%....
   41261: 4b10 c5a0 a7b9 c1ad b77e b949 2c5c 9f0d  K........~.I,\..
   41269: ddcd 77f3 0000 0000 0000 0000 0000 0000  ..w.............
   41277: 0000 0000 0000 0000 0000 0000            ............
```


#### OCMF End Representation

After successfully creating the _Signed Turn-Off Snapshot_, its OCMF
representation can be read from _OCMF Signed Turn-Off Snapshot_:
```
$ bsmtool get ostoffs
bsm_ocmf:
    Typ: 2
    St: 0
    O: OCMF|{"FV":"1.0","GI":"BAUER Electronic BSM-WS36A-H01-1311-0000","GS":"001BZR1521070006","GV":"1.9:32CA:AFF4, f1d3d06","PG":"T4277","MV":"BAUER Electronic","MM":"BSM-WS36A-H01-1311-0000","MS":"001BZR1521070006","IS":true,"IT":"UNDEFINED","ID":"contract-id: rfid:12345678abcdef","X2":"evse-id: DE*BDO*E8025334492*2","X3":"csc-sw-version: v1.2.34","RD":[{"TM":"2022-07-08T10:05:52,000+0200 S","TX":"E","RV":0.15,"RI":"1-0:1.8.0*198","RU":"kWh","XV":100.00,"XI":"1-0:1.8.0*255","XU":"kWh","XT":2,"RT":"AC","EF":"","ST":"G"}]}|{"SA":"ECDSA-secp256r1-SHA256","SD":"3044022014f0be0063d22f3b847218f42cd2a852f6d2a487c6668160613ce5542787c10302206f83d65044da4874da4e671742e4de5236202d52f4bd4d9fca4130bd16ef76dc"}
```
```
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


#### Key End OCMF Values

[Pretty-printed](ocmf.md#ocmf-json-payload), the _OCMF Signed Turn-Off
Snapshot_ looks as follows:
```json
$ bsmtool get ostons/o | cut -d \| -f 2 | jq .
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

Let's have a quick look at its key data points:

- Type and status
    - Its type is indicated by the transaction _TX_ = _E_ (for end)
    - Its status _ST_ = _G_ stands for good
- Power and energy
    - The primary reading value _RV_ now shows the energy consumption from the
      refernce cumulative register: 160 Wh
    - The total energy consumption is given by _XV_
    - The OCMF data does not contain the active power
- Time and counters
    - The response counter _PG_ (prefixed with _T_) gives the value 4,277 and
      is the successor of the start response counter
    - Epoch time information is given in ISO 8601 format
- The identification data _ID_ taken from _Meta1_ has the same value as in the
  start OCMF data
- _Meta2_ and _Meta3_ are provided as _X2_ and _X3_


#### End OCMF Register Dump

The register dump of the end snapshot's OCMF representation looks as follows:
```
$ bsmtool dump 42791 500
   42791: fd87 01f2 0002 0000 4f43 4d46 7c7b 2246  ........OCMF|{"F
   42799: 5622 3a22 312e 3022 2c22 4749 223a 2242  V":"1.0","GI":"B
   42807: 4155 4552 2045 6c65 6374 726f 6e69 6320  AUER Electronic 
   42815: 4253 4d2d 5753 3336 412d 4830 312d 3133  BSM-WS36A-H01-13
   42823: 3131 2d30 3030 3022 2c22 4753 223a 2230  11-0000","GS":"0
   42831: 3031 425a 5231 3532 3130 3730 3030 3622  01BZR1521070006"
   42839: 2c22 4756 223a 2231 2e39 3a33 3243 413a  ,"GV":"1.9:32CA:
   42847: 4146 4634 2c20 6631 6433 6430 3622 2c22  AFF4, f1d3d06","
   42855: 5047 223a 2254 3432 3737 222c 224d 5622  PG":"T4277","MV"
   42863: 3a22 4241 5545 5220 456c 6563 7472 6f6e  :"BAUER Electron
   42871: 6963 222c 224d 4d22 3a22 4253 4d2d 5753  ic","MM":"BSM-WS
   42879: 3336 412d 4830 312d 3133 3131 2d30 3030  36A-H01-1311-000
   42887: 3022 2c22 4d53 223a 2230 3031 425a 5231  0","MS":"001BZR1
   42895: 3532 3130 3730 3030 3622 2c22 4953 223a  521070006","IS":
   42903: 7472 7565 2c22 4954 223a 2255 4e44 4546  true,"IT":"UNDEF
   42911: 494e 4544 222c 2249 4422 3a22 636f 6e74  INED","ID":"cont
   42919: 7261 6374 2d69 643a 2072 6669 643a 3132  ract-id: rfid:12
   42927: 3334 3536 3738 6162 6364 6566 222c 2258  345678abcdef","X
   42935: 3222 3a22 6576 7365 2d69 643a 2044 452a  2":"evse-id: DE*
   42943: 4244 4f2a 4538 3032 3533 3334 3439 322a  BDO*E8025334492*
   42951: 3222 2c22 5833 223a 2263 7363 2d73 772d  2","X3":"csc-sw-
   42959: 7665 7273 696f 6e3a 2076 312e 322e 3334  version: v1.2.34
   42967: 222c 2252 4422 3a5b 7b22 544d 223a 2232  ","RD":[{"TM":"2
   42975: 3032 322d 3037 2d30 3854 3130 3a30 353a  022-07-08T10:05:
   42983: 3532 2c30 3030 2b30 3230 3020 5322 2c22  52,000+0200 S","
   42991: 5458 223a 2245 222c 2252 5622 3a30 2e31  TX":"E","RV":0.1
   42999: 352c 2252 4922 3a22 312d 303a 312e 382e  5,"RI":"1-0:1.8.
   43007: 302a 3139 3822 2c22 5255 223a 226b 5768  0*198","RU":"kWh
   43015: 222c 2258 5622 3a31 3030 2e30 302c 2258  ","XV":100.00,"X
   43023: 4922 3a22 312d 303a 312e 382e 302a 3235  I":"1-0:1.8.0*25
   43031: 3522 2c22 5855 223a 226b 5768 222c 2258  5","XU":"kWh","X
   43039: 5422 3a32 2c22 5254 223a 2241 4322 2c22  T":2,"RT":"AC","
   43047: 4546 223a 2222 2c22 5354 223a 2247 227d  EF":"","ST":"G"}
   43055: 5d7d 7c7b 2253 4122 3a22 4543 4453 412d  ]}|{"SA":"ECDSA-
   43063: 7365 6370 3235 3672 312d 5348 4132 3536  secp256r1-SHA256
   43071: 222c 2253 4422 3a22 3330 3434 3032 3230  ","SD":"30440220
   43079: 3134 6630 6265 3030 3633 6432 3266 3362  14f0be0063d22f3b
   43087: 3834 3732 3138 6634 3263 6432 6138 3532  847218f42cd2a852
   43095: 6636 6432 6134 3837 6336 3636 3831 3630  f6d2a487c6668160
   43103: 3631 3363 6535 3534 3237 3837 6331 3033  613ce5542787c103
   43111: 3032 3230 3666 3833 6436 3530 3434 6461  02206f83d65044da
   43119: 3438 3734 6461 3465 3637 3137 3432 6534  4874da4e671742e4
   43127: 6465 3532 3336 3230 3264 3532 6634 6264  de5236202d52f4bd
   43135: 3464 3966 6361 3431 3330 6264 3136 6566  4d9fca4130bd16ef
   43143: 3736 6463 227d 0000 0000 0000 0000 0000  76dc"}..........
   43151: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43159: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43167: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43175: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43183: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43191: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43199: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43207: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43215: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43223: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43231: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43239: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43247: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43255: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43263: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43271: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43279: 0000 0000 0000 0000 0000 0000 0000 0000  ................
   43287: 0000 0000 0000 0000                      ........
```


### Billing Data and Verification

Having _Signed Turn-On Snapshot_ and _Signed Turn-Off Snapshot_ successfully
created and read, billing data could be generated. Depending on the application
it might be either derived from the snapshot data or its OCMF representation.
In the latter case this data is typically wrapped in an OCMF XML envelope as
described in [OCMF XML](ocmf.md#ocmf-xml).

[Snapshot Verification](snapshots.md#snapshot-verification) describes how to
verify snapshot data and [OCMF XML](ocmf.md#ocmf-xml) the generation and
verification of OCMF XML envelopes.


#### Chargy

Chargy verifies JSON data generated by chargeIT mobility's backend. [chargeIT
mobility Chargy and Custom Formats](chargy.md) describes this format. It could
be generated from the snapshots above with:
```
$ bsmtool chargy stons stoffs > ev-charging-chargy.json
```

After downloading or just copying the data from the portal, it can be opened in
or pasted into Chargy for verification. For example, the data set
[`ev-charging-chargy.json`](data/ev-charging-chargy.json):

![Chargy Main Window](img/ev-charging-chargy-verification-overview.png)


#### OCMF with S.A.F.E. Transparenzsoftware

For this example, the OCMF XML envelope could be generated from the OCMF
representation of start and end snapshot created above with:
```xml
$ bsmtool ocmf-xml ostons ostoffs | tee ev-charging-ocmf.xml
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

This data (saved as [`ev-charging-ocmf.xml`](data/ev-charging-ocmf.xml)) can be
successfully verified with [S.A.F.E. e.V.
Transparenzsoftware](https://www.safe-ev.de/de/transparenzsoftware.php) by
loading it into the application and cliking on _Transaktion überprüfen_:

![S.A.F.E. e.V. Transparenzsoftware Main Window](img/ev-charging-ocmf-verification-overview.png)
![S.A.F.E. e.V. Transparenzsoftware Verification Details](img/ev-charging-ocmf-verification-detail.png)
