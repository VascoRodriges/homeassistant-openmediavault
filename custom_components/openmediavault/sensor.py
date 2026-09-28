"""OpenMediaVault sensor platform."""

import asyncio
from logging import getLogger
from typing import Any
from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from homeassistant.components.sensor import SensorEntity
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.typing import StateType
from .helper import format_attribute
from .model import model_async_setup_entry, OMVEntity
from .sensor_types import (
    SENSOR_TYPES,
    DEVICE_ATTRIBUTES_DISK_SMART,
)

_LOGGER = getLogger(__name__)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up device tracker for OpenMediaVault component."""
    dispatcher = {
        "OMVSensor": OMVSensor,
        "OMVDiskSensor": OMVDiskSensor,
        "OMVUptimeSensor": OMVUptimeSensor,
        "OMVKVMSensor": OMVKVMSensor,
        "OMVComposeSensor": OMVComposeSensor,
    }
    await model_async_setup_entry(
        hass,
        config_entry,
        async_add_entities,
        SENSOR_TYPES,
        dispatcher,
    )


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVSensor(OMVEntity, SensorEntity):
    """Define an OpenMediaVault sensor."""

    def __init__(
        self,
        inst,
        uid: str,
        omv_controller,
        entity_description,
    ):
        super().__init__(inst, uid, omv_controller, entity_description)
        self._attr_suggested_unit_of_measurement = (
            self.entity_description.suggested_unit_of_measurement
        )

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        return self._data[self.entity_description.data_attribute]

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        if self.entity_description.native_unit_of_measurement:
            if self.entity_description.native_unit_of_measurement.startswith("data__"):
                uom = self.entity_description.native_unit_of_measurement[6:]
                if uom in self._data:
                    return self._data[uom]

            return self.entity_description.native_unit_of_measurement

        return None


# ---------------------------
#   OMVSensor
# ---------------------------
class OMVDiskSensor(OMVSensor):
    """Define an OpenMediaVault sensor."""

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        attributes = super().extra_state_attributes

        if not self._ctrl.option_smart_disable:
            for variable in DEVICE_ATTRIBUTES_DISK_SMART:
                if variable in self._data:
                    attributes[format_attribute(variable)] = self._data[variable]

        return attributes


# ---------------------------
#   OMVUptimeSensor
# ---------------------------
class OMVUptimeSensor(OMVSensor):
    """Define an OpenMediaVault Uptime sensor."""

    async def restart(self) -> None:
        """Restart OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "System",
            "reboot",
            {"delay": 0},
        )

    async def stop(self) -> None:
        """Shutdown OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "System",
            "shutdown",
            {"delay": 0},
        )


# ---------------------------
#   OMVKVMSensor
# ---------------------------
class OMVKVMSensor(OMVSensor):
    """Define an OpenMediaVault VM sensor."""

    async def start(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "shutoff":
            _LOGGER.warning("VM %s is not powered off", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "poweron",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def stop(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "running":
            _LOGGER.warning("VM %s is not running", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "poweroff",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def restart(self) -> None:
        """Shutdown OpenMediaVault systen."""
        tmp = await self.hass.async_add_executor_job(
            self._ctrl.api.query, "Kvm", "getVmList", {"start": 0, "limit": 999}
        )

        state = ""
        if "data" in tmp:
            for tmp_i in tmp["data"]:
                if tmp_i["vmname"] == self._data["vmname"]:
                    state = tmp_i["state"]
                    break

        if state != "running":
            _LOGGER.warning("VM %s is not running", self._data["vmname"])
            return

        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "doCommand",
            {
                "command": "reboot",
                "virttype": f"{self._data['type']}",
                "name": f"{self._data['vmname']}",
            },
        )

    async def snapshot(self) -> None:
        """Shutdown OpenMediaVault systen."""
        await self.hass.async_add_executor_job(
            self._ctrl.api.query,
            "Kvm",
            "addSnapshot",
            {
                "virttype": f"{self._data['type']}",
                "vmname": f"{self._data['vmname']}",
            },
        )


class OMVComposeSensor(OMVSensor):
    """Represent and control an OMV Compose project."""

    def __init__(self, *args, **kwargs):
        """Initialize a Compose project sensor."""
        super().__init__(*args, **kwargs)
        self._command_lock = asyncio.Lock()

    async def _command(self, command: str) -> None:
        uuid = self._data.get("uuid")
        if not uuid or uuid == "unknown":
            raise ServiceValidationError("OMV Compose project UUID is unavailable")

        async with self._command_lock:
            await self.hass.async_add_executor_job(
                self._ctrl.api.query,
                "Compose",
                "doCommand",
                {"command": command, "uuid": uuid},
            )
            if self._ctrl.api.error is not None:
                raise HomeAssistantError(
                    f"OpenMediaVault rejected Compose command: {self._ctrl.api.error}"
                )

            await asyncio.sleep(3)
            await self.hass.async_add_executor_job(self._ctrl.get_compose)
            self.async_write_ha_state()

    async def start(self) -> None:
        """Start this Compose project."""
        await self._command("up")

    async def stop(self) -> None:
        """Stop this Compose project."""
        await self._command("down")

    async def restart(self) -> None:
        """Restart this Compose project."""
        await self._command("restart")
