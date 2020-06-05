import logging
import asyncio
from datetime import timedelta
from homeassistant.components.lock import LockEntity
from homeassistant.const import (ATTR_CODE, STATE_LOCKED, STATE_UNKNOWN,
                                 STATE_UNLOCKED)

import custom_components.sector as sector

DEPENDENCIES = ['sector']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=10)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):

    sector_hub = hass.data[sector.DATA_SA]
    code = discovery_info[sector.CONF_CODE]
    code_format = discovery_info[sector.CONF_CODE_FORMAT]

    locks = await sector_hub.get_locks()

    if locks is not None:
        async_add_entities(
            SectorAlarmLock(sector_hub, code, code_format, lock)
            for lock in locks)

class SectorAlarmLock(LockEntity):
    """Representation of a Sector Alarm lock."""

    def __init__(self, hub, code, code_format, serial):
        self._hub = hub
        self._serial = serial
        self._code = code
        self._code_format = code_format
        self._state = STATE_UNKNOWN

    @property
    def name(self):
        """Return the serial of the lock."""
        return self._serial

    @property
    def changed_by(self):
        """Return the serial of the lock."""
        return None

    @property
    def state(self):
        """Return the state of the lock."""
        return self._state

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    @property
    def code_format(self):
        """Return the required six digit code."""
        return self._code_format

    async def async_update(self):
        update = await self._hub.async_update()
        state = self._hub.lock_state[self._serial]
        if state == 'lock':
            self._state = STATE_LOCKED
        elif state == 'unlock':
            self._state = STATE_UNLOCKED
        else:
            self._state = STATE_UNKNOWN
        return True

    def _validate_code(self, code):
        """Validate given code."""
        check = self._code is None or code == self._code
        if not check:
            _LOGGER.warning("Invalid code given")
        return check

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        return self._state == STATE_LOCKED

    async def unlock(self, **kwargs):
        """Send unlock command."""
        COMMAND = "unlock"
        if not self._validate_code(code):
            return
        state = await self._hub.triggerlock(self._serial, self._code, COMMAND)
        if state:
            self._state = STATE_UNLOCKED
            return True
        return False

    async def lock(self, **kwargs):
        """Send lock command."""
        COMMAND = "unlock"
        if not self._validate_code(code):
            return
        state = await self._hub.triggerlock(self._serial, self._code, COMMAND)
        if state:
            self._state = STATE_LOCKED
            return True
        return False