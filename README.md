# EHEIM Digital for Home Assistant

## Installation

## Compatible devices
### External filters
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| professionel 5e 350 | No | No | | |
| professionel 5e 450 | No | No | | |
| professionel 5e 600T | No | No | | |
| professionel 5e 700 | No | No | 1.01.3 | 1.00.8 |

### Heaters
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| thermocontrol+ e 150 | No | No | | |
| thermocontrol+ e 200 | No | No | | |
| thermocontrol+ e 250 | No | No | | |
| thermocontrol+ e 300 | No | No | 1.01.3 | 1.00.8 |

### Lighting control
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| LEDcontrol+e | No | No | | |

### CO2
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| pHcontrol+e | No | No | | |

### Feeding
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| autofeeder+ | No | No | | |

### Climate control 
| Name | Integrated | Tested | Version Website | Version Server |
| --- | --- | --- | --- | --- |
| climacontrol+ S | No | No | | |
| climacontrol+ M | No | No | | |
| climacontrol+ L | No | No | | |

## Receiving Websocket Data

Tha Data sent by EHEIM Digital devices comes via websocket. Here are 2 examples of device data that I have available:

<details>
<summary>
<b>EHEIM thermocontrol+ e 300</b>
</summary>

```json
{
  "active": 1,
  "alertState": 0,
  "dayStartT": 390,
  "from": "<MAC_ADDRESS>",
  "hystHigh": 5,
  "hystLow": 5,
  "isHeating": 0,
  "isTemp": 268,
  "mUnit": 0,
  "mode": 0,
  "nReduce": -2,
  "nightStartT": 1080,
  "offset": 0,
  "partnerName": "",
  "sollTemp": 260,
  "sync": "",
  "title": "HEATER_DATA",
  "to": "USER"
}
```

<b>Explanation of values</b>

| Key | Type | Mode | Meaning |
| --- | --- | --- | --- |
| `active` | `int` | all | 0 = turned off, 1 = turned on |
| `alertState` | `int` | all | 0 = no alert,  ? |
| `dayStartT` | `int` | all | unknown |
| `from` | `string` | all | MAC address of device |
| `hystHigh` | `int` | all | unknown |
| `hystLow` | `int` | all | unknown |
| `isHeating` | `int` | all | 0 = not heating, 1 = heating |
| `isTemp` | `int` | all | currently measured temperature, `value` / 10 = temperature |
| `mUnit` | `int` | all | unknown |
| `mode` | `int` | all | unknown |
| `nReduce` | `int` | `smart` | reduction of temperature at night |
| `nightStartT` | `int` | all | unknown |
| `offset` | `int` | all | unknown |
| `partnerName` | `string` | `smart` | Devicename when synced |
| `sollTemp` | `int` | all | target temperature, `value` / 10 = temperature |
| `sync` | `string` | `smart` | partner MAC address |
| `title` | `int` | all | = `HEATER_DATA` |
| `to` | `string` | all | = `USER` |

</details>

<details>
<summary>
<b>EHEIM professionel 5e 700</b>
</summary>
  
```json
{
  "actualTime": 2784,
  "dfs": 1375,
  "dfsFaktor": 2927,
  "end_time_night_mode": 480,
  "filterActive": 1,
  "freq": 4700,
  "freqSoll": 4700,
  "from": "<MAC_ADDRESS>",
  "isEheim": 0,
  "maxFreq": 7500,
  "maxFreqRglOff": 8000,
  "minFreq": 3500,
  "nm_dfs_soll_day": 9,
  "nm_dfs_soll_night": 0,
  "pm_dfs_soll_high": 7,
  "pm_dfs_soll_low": 4,
  "pm_time_high": 45,
  "pm_time_low": 40,
  "pumpMode": 1,
  "rotSpeed": 28,
  "runTime": 2784,
  "serviceHour": 4320,
  "sollStep": 8,
  "start_time_night_mode": 1200,
  "title": "FILTER_DATA",
  "to": "USER",
  "turnOffTime": 0,
  "turnTimeFeeding": 0,
  "version": 78
}
```
    
<b>Explanation of values</b>
    
| Key | Type | Mode | Meaning |
| --- | --- | --- | --- |
| `actualTime` | `int` | all | operating time in minutes |
| `dfs` | `int` | all | unknown |
| `dfsFaktor` | `int` | all | unknown |
| `end_time_night_mode` | `int` | `bio` | endtime of night, `value` / 60 = time |
| `filterActive` | `int` | all | 1 = running, 0 = stopped |
| `freq` | `int` | all | current speed, `freq` / `maxFreq` * 100 = value in % |
| `freqSoll` | `int` | all | target speed, `freqSoll` / `maxFreq` * 100 = value in % |
| `from` | `string` | all | MAC address of device |
| `isEheim` | `int` | all | unknown |
| `maxFreq` | `int` | `constant`, `bio`, `pulse` | maximum possible freq in these modes (unsure) |
| `maxFreqRglOff` | `int` | `manual` | maximum possible freq in this mode (100% power) (unsure) |
| `minFreq` | `int` | `constant`, `bio`, `pulse` | minimum possible freq in these modes (unsure) |
| `nm_dfs_soll_day` | `int` | `bio` | 0 - 10 power setting for day (0 = `minFreq`, 10 = ?) |
| `nm_dfs_soll_night` | `int` | `bio` | 0 - 10 power setting for night (0 = `minFreq`, 10 = ?) |
| `pm_dfs_soll_high` | `int` | `pulse` | 0 - 10 power setting for high phase (0 = `minFreq`, 10 = ?) |
| `pm_dfs_soll_low` | `int` | `pulse` | 0 - 10 power setting for low phase (0 = `minFreq`, 10 = ?) |
| `pm_time_high` | `int` | `pulse` | duration of high phase in s |
| `pm_time_low` | `int` | `pulse` | duration of low phase in s |
| `pumpMode` | `int` | all | manual = 16, pulse = 8, bio = 4, constant = 1, calibrating = 24577 or 8193 (other values have been seen as well) |
| `rotSpeed` | `int` | all | unknown |
| `serviceHour` | `int` | all | hours until next cleaning |
| `sollStep` | `int` | all | unknown |
| `start_time_night_mode` | `int` | `bio` | starttime of night, `value` / 60 = time |
| `title` | `string` | all | = `FILTER_DATA` |
| `to` | `string` | all | = `USER` |
| `turnOffTime` | `int` | all | time in s until automatic turn on after turning off via webinterface |
| `turnTimeFeeding` | `int` | all | unknown, maybe something for connection to autofeeder+ ? |
| `version` | `int` | all | unknown |

</details>




# Sending Websocket Commands

<details>
<summary>
<b>External filters</b>
</summary>
  
<b>Turn off</b>

`{"title":"SET_FILTER_PUMP","to":"<MAC_ADDRESS>","active":0,"from":"USER"}`

<b>Turn on</b>

`{"title":"SET_FILTER_PUMP","to":"<MAC_ADDRESS>","active":1,"from":"USER"}`

<b>Change mode to `constant` or change flow rate</b>

`{"title":"START_FILTER_NORMAL_MODE_WITH_COMP","to":"<MAC_ADDRESS>","flow_rate":<NEW_VALUE>,"from":"USER"}`

<sub>flow_rate means steps from 0 to 8</sub>

<b>Change mode to `bio` or change values</b>

`{"title":"START_NOCTURNAL_MODE","to":"<MAC_ADDRESS>","dfs_soll_day":<NEW_VALUE>,"dfs_soll_night":<NEW_VALUE>,"end_time_night_mode":<NEW_VALUE>,"start_time_night_mode":<NEW_VALUE>,"from":"USER"}`

<b>Change mode to `pulse` or change values</b>

`{"title":"START_FILTER_PULSE_MODE","to":"<MAC_ADDRESS>","time_high":<NEW_VALUE>,"time_low":<NEW_VALUE>,"dfs_soll_high":<NEW_VALUE>,"dfs_soll_low":<NEW_VALUE>,"from":"USER"}`

<b>Change mode to `manual` or change manual speed</b>

`{"title":"START_FILTER_NORMAL_MODE_WITHOUT_COMP","to":"<MAC_ADDRESS>","frequency":<NEW_VALUE>,"from":"USER"}`

</details>
  
<details>
<summary>
<b>Heaters</b>
</summary>

<b>Change any value</b>

There will always be sent the same message

`{"title":"SET_EHEATER_PARAM","to":"<MAC_ADDRESS>","mUnit":<NEW_VALUE>,"sollTemp":<NEW_VALUE>,"active":<NEW_VALUE>,"hystLow":<NEW_VALUE>,"hystHigh":<NEW_VALUE>,"offset":<NEW_VALUE>,"mode":<NEW_VALUE>,"sync":"<MAC_ADDRESS>","partnerName":"<NAME>","dayStartT":<NEW_VALUE>,"nightStartT":<NEW_VALUE>,"nReduce":<NEW_VALUE>,"from":"USER"}`

</details>
