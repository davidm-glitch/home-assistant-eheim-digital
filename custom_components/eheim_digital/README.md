# EHEIM Digital for Home Assistant

## Installation


## Websocket Data

Tha Data sent by EHEIM Digital devices comes via websocket. Here are 2 examples of device data that I have available:

<b>EHEIM thermocontrol+ e 300</b>
```
{
"title": "HEATER_DATA",
"from": "<MAC_ADDRESS>",
"mUnit": 0,
"sollTemp": 260,
"isTemp": 270,
"hystLow": 5,
"hystHigh": 5,
"offset": 0,
"active": 1,
"isHeating": 0,
"mode": 0,
"sync": "",
"partnerName": "",
"dayStartT": 390,
"nightStartT": 1080,
"nReduce": -2,
"alertState": 0,
"to": "USER"
}
```


<b>EHEIM professionel 5e 700</b>
```
[
    {
        "title": "FILTER_DATA",
        "from": "<MAC_AdDRESS>",
        "minFreq": 3500,
        "maxFreq": 7500,
        "maxFreqRglOff": 8000,
        "freq": 7200,
        "freqSoll": 7200,
        "dfs": 1377,
        "dfsFaktor": 1914,
        "sollStep": 8,
        "rotSpeed": 43,
        "pumpMode": 1,
        "filterActive": 1,
        "runTime": 2178,
        "actualTime": 2178,
        "serviceHour": 4320,
        "pm_dfs_soll_high": 10,
        "pm_dfs_soll_low": 1,
        "pm_time_high": 10,
        "pm_time_low": 10,
        "nm_dfs_soll_day": 10,
        "nm_dfs_soll_night": 3,
        "end_time_night_mode": 480,
        "start_time_night_mode": 1080,
        "version": 78,
        "isEheim": 0,
        "turnOffTime": 0,
        "turnTimeFeeding": 0
    },
    {
        "title": "MESH_NETWORK",
        "from": "<MAC_AdDRESS>",
        "clientList": [
            "<MAC_AdDRESS>",
            "<MAC_AdDRESS>"
        ]
    }
]
```