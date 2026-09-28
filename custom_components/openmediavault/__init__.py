"""The OpenMediaVault integration."""

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, service
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .omv_controller import OMVControllerData
from .sensor_types import SENSOR_SERVICES


# ---------------------------
#   async_setup
# ---------------------------
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up configured OMV Controller."""
    hass.data.setdefault(DOMAIN, {})
    for action, schema, method in SENSOR_SERVICES:
        service.async_register_platform_entity_service(
            hass,
            DOMAIN,
            action,
            entity_domain=SENSOR_DOMAIN,
            schema=schema,
            func=method,
        )
    return True


# ---------------------------
#   update_listener
# ---------------------------
async def _async_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


# ---------------------------
#   async_setup_entry
# ---------------------------
async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up OMV config entry."""
    hass.data.setdefault(DOMAIN, {})
    controller = OMVControllerData(hass, config_entry)
    await controller.async_hwinfo_update()
    await controller.async_update()

    if not controller.connected():
        raise ConfigEntryNotReady()

    hostname = controller.data["hwinfo"]["hostname"]
    protocol = "https" if config_entry.data[CONF_SSL] else "http"
    hub_device = dr.async_get(hass).async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, hostname)},
        connections={(DOMAIN, hostname)},
        name=f"{config_entry.data[CONF_NAME]} System",
        manufacturer="OpenMediaVault",
        sw_version=controller.data["hwinfo"]["version"],
        configuration_url=f"{protocol}://{config_entry.data[CONF_HOST]}",
    )
    controller.hub_device_id = hub_device.id

    await controller.async_init()
    hass.data[DOMAIN][config_entry.entry_id] = controller

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)
    config_entry.async_on_unload(
        config_entry.add_update_listener(_async_update_listener)
    )

    return True


# ---------------------------
#   async_unload_entry
# ---------------------------
async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload TrueNAS config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        controller = hass.data[DOMAIN][config_entry.entry_id]
        await controller.async_reset()
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
