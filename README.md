# EHEIM Digital for Home Assistant

## Installation

### Step 1
Install MQTT Broker

### Step 2
tba

### Step 3
Adjust config.yaml of the eheim_digital folder.

### Step 4
Add this to your Home Assistant configuration.yaml

Remove or change the entities to suit your setup.

```yaml
mqtt:
  switch:
    # HEATER
    - command_topic: "eheim_digital/heater/active/set"
      name: EHEIM heater active
      icon: mdi:heat-wave
      device_class: switch
      state_topic: "eheim_digital/heater/is_active"
      <<: &eheim_heater_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/heater/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all

    # FILTER
    - command_topic: "eheim_digital/filter_running/set"
      name: EHEIM filter running
      icon: mdi:air-filter
      device_class: switch
      state_topic: "eheim_digital/filter/filter_running"
      <<: &eheim_filter_availability
        availability:
          - topic: "eheim_digital/status"
            payload_available: "online"
            payload_not_available: "offline"
          - topic: "eheim_digital/filter/status"
            payload_available: "online"
            payload_not_available: "offline"
        availability_mode: all

  binary_sensor:
    # HEATER
    - name: EHEIM Heater alert
      state_topic: "eheim_digital/heater/alert"
      device_class: problem
      icon: mdi:thermometer-alert
      <<: *eheim_heater_availability
    - name: EHEIM Heater is heating
      state_topic: "eheim_digital/heater/is_heating"
      device_class: running
      icon: mdi:heat-wave
      <<: *eheim_heater_availability

  sensor:
    # HEATER
    - name: EHEIM Heater current temperature
      state_topic: "eheim_digital/heater/current_temperature"
      device_class: temperature
      unit_of_measurement: °C
      <<: *eheim_heater_availability

    # FILTER
    - name: EHEIM Filter operating time
      state_topic: "eheim_digital/filter/operating_time"
      unit_of_measurement: "h"
      icon: mdi:timer
      <<: *eheim_filter_availability
    - name: EHEIM Filter end time night mode
      state_topic: "eheim_digital/filter/end_time_night_mode"
      icon: mdi:clock-time-eight
      <<: *eheim_filter_availability
    - name: EHEIM Filter start time night mode
      state_topic: "eheim_digital/filter/start_time_night_mode"
      icon: mdi:clock-time-six
      <<: *eheim_filter_availability
    - name: EHEIM Filter current speed
      state_topic: "eheim_digital/filter/current_speed"
      unit_of_measurement: "%"
      icon: mdi:speedometer
      <<: *eheim_filter_availability
    - name: EHEIM Filter next service
      state_topic: "eheim_digital/filter/next_service"
      unit_of_measurement: "h"
      icon: mdi:wrench-clock
      <<: *eheim_filter_availability
    - name: EHEIM Filter turn off time
      state_topic: "eheim_digital/filter/turn_off_time"
      unit_of_measurement: "s"
      icon: mdi:timer
      <<: *eheim_filter_availability

  select:
    # HEATER

    # FILTER
    - command_topic: "eheim_digital/filter/pump_mode/set"
      state_topic: "eheim_digital/filter/pump_mode"
      icon: mdi:pump
      <<: *eheim_filter_availability
      name: "EHEIM filter pump mode"
      options:
        - "constant"
        - "bio"
        - "pulse"
        - "manual"

  number:
    # HEATER
    - command_topic: "eheim_digital/heater/target_temperature/set"
      state_topic: "eheim_digital/heater/target_temperature"
      name: EHEIM Heater target temperature
      unit_of_measurement: °C
      icon: mdi:thermometer
      min: 18
      max: 32
      step: 0.5
      <<: *eheim_heater_availability

    # FILTER
    - command_topic: "eheim_digital/filter/target_speed/set"
      state_topic: "eheim_digital/filter/target_speed"
      name: EHEIM Filter target speed
      unit_of_measurement: "%"
      icon: mdi:speedometer
      <<: *eheim_filter_availability
      min: 0
      max: 100
      step: 1
```

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

