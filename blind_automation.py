import appdaemon.plugins.hass.hassapi as hass
from enum import Enum
import voluptuous as vol
import voluptuous_helper as vol_help
from datetime import datetime, time, timedelta

"""
Blind automation adjust all configured blinds (in the AppDaemon configuration file apps.yaml)
based on the sun elevation, sun azimuth, temperature instide and outside

Arguments:
- outside_temperature       - outside temperature sensor
- weather                   - weather entity (check state for clouds)
- winter_treshold           - outside temperature theshold to switch to the winter_mode
- winter_max_temperature    - in winter suny day, let sun in if internal temperature is below
- enable_automation         - input boolean to disable the automation
- blinds:                   - (required) list of blinds
  - entity_id:              - (required) blind entity ID
    inside_temperature      - room temperature sensor
    start_at                - do not run before this time (reflects sun azimuth)
    stop_at                 - do not run after this time (reflects sun azimuth)
    min_azimuth             - open if azimuth is smaller than
    max_azimuth             - open if azimuth is greater than

configuration example (in AppDaemon's apps.yaml):

blind_automation:
    module: adjust-covers
    class: Blind_Automation
    outside_temperature: sensor.outside_temperature
    enable_automation: input_boolean.enable_blind_automation
    blinds:
    - entity_id: sensor.blind_all
      inside_temperature: sensor.office_temperature
      stop_at: '15:00'
      start_at: '8:00'
      min_azimuth: 25
      max_azimuth: 210
"""

ENTITY_ID = "entity_id"
ENABLE_AUTOMATION = "enable_automation"
OUTSIDE_TEMPERATURE = "outside_temperature"


class BlindAutomation(hass.Hass):
  def initialize(self):
    BLIND_SCHEMA = vol.Schema(
      {
        vol.Required(ENTITY_ID): vol_help.existing_entity_id(self),
        vol.Optional(OUTSIDE_TEMPERATURE): vol_help.existing_entity_id(self),
        vol.Optional(OUTSIDE_TEMPERATURE): vol_help.existing_entity_id(self),
        
      }
    )
    APP_SCHEMA = vol.Schema(
      {
        vol.Required("module"): str,
        vol.Required("class"): str,
        vol.Optional(ENABLE_AUTOMATION): vol_help.existing_entity_id(self),
        
      },
      extra= vol.ALLOW_EXTRA,
    )
    __version__ = "0.0.1"
    try:
      config = APP_SCHEMA(self.args)
    except vol.Invalid as err:
      vol.error(f"Invalid format: {err}", level="ERROR")
      return
    self.__outside_temperature = config.get(OUTSIDE_TEMPERATURE)
    