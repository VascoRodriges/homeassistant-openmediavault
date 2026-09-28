# OpenMediaVault integration for Home Assistant — maintained fork

![GitHub release (latest by date)](https://img.shields.io/github/v/release/VascoRodriges/homeassistant-openmediavault?style=plastic)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=plastic)](https://www.hacs.xyz/docs/faq/custom_repositories/)
![Project Stage](https://img.shields.io/badge/project%20stage-development-yellow.svg?style=plastic)
![GitHub all releases](https://img.shields.io/github/downloads/VascoRodriges/homeassistant-openmediavault/total?style=plastic)

![GitHub commits since latest release](https://img.shields.io/github/commits-since/VascoRodriges/homeassistant-openmediavault/latest?style=plastic)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/VascoRodriges/homeassistant-openmediavault?style=plastic)

[![Help localize](https://img.shields.io/badge/lokalise-join-green?style=plastic&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyhpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ1IDc5LjE2MzQ5OSwgMjAxOC8wOC8xMy0xNjo0MDoyMiAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wTU09Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9tbS8iIHhtbG5zOnN0UmVmPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VSZWYjIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6REVCNzgzOEY4NDYxMTFFQUIyMEY4Njc0NzVDOUZFMkMiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6REVCNzgzOEU4NDYxMTFFQUIyMEY4Njc0NzVDOUZFMkMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENDIDIwMTcgKE1hY2ludG9zaCkiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDozN0ZDRUY4Rjc0M0UxMUU3QUQ2MDg4M0Q0MkE0NjNCNSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDozN0ZDRUY5MDc0M0UxMUU3QUQ2MDg4M0Q0MkE0NjNCNSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pjs1zyIAAABVSURBVHjaYvz//z8DOYCJgUxAtkYW9+mXyXIrI7l+ZGHc0k5nGxkupdHZxve1yQR1CjbPZURXh9dGoGJZIPUI2QC4JEgjIfyuJuk/uhgj3dMqQIABAPEGTZ/+h0kEAAAAAElFTkSuQmCC)](https://app.lokalise.com/public/106503135ea170ab5e1f70.96389313/)

![English](https://raw.githubusercontent.com/tomaae/homeassistant-mikrotik_router/master/docs/assets/images/flags/us.png)

![OpenMediaVault Logo](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/header.png)

This repository is a public fork of
[`tomaae/homeassistant-openmediavault`](https://github.com/tomaae/homeassistant-openmediavault).
It retains the original Apache-2.0 license and upstream attribution. The fork exists
to keep the integration compatible with current Home Assistant and OpenMediaVault
releases and to maintain additional functionality used by this installation.

## What this fork adds and fixes

Release `v1.5.x` is based on the current upstream `master` branch and includes:

* authentication compatibility with the response schema introduced in OMV 8.5;
* support for the current OMV Compose background-job API;
* Compose project UUID discovery without UUIDs hard-coded in Lovelace YAML;
* entity-targeted `compose_start`, `compose_stop`, and `compose_restart` actions;
* removal of the unsafe generic RPC action that could invoke arbitrary OMV API methods;
* correct reconciliation of refreshed Compose data while existing HA entities remain loaded;
* guaranteed release of controller update locks after an exception;
* safer config-entry unloading and explicit fork documentation/issue links.

The original monitoring features remain available:

Features:
* Filesystem usage sensors
* System sensors (CPU, Memory, Uptime)
* System status sensors (Available updates, Required reboot and Dirty config)
* Disk and smart sensors
* Service sensors
* OMV Compose project status and entity-targeted start, stop, and restart actions

## Roadmap

Planned work is tracked here so the repository description does not need to be
rewritten for every small release:

* migrate polling to Home Assistant's `DataUpdateCoordinator` model;
* register entity actions from integration setup using the current HA service API;
* replace deprecated `DeviceInfo` fields before their Home Assistant removal date;
* add automated unit tests for API parsing, Compose commands, and error recovery;
* enable current HACS and Home Assistant validation in CI;
* improve removal/unavailability handling for disks, filesystems, VMs, and Compose projects;
* expand OMV 7/8 compatibility testing, translations, diagnostics, and repair messages;
* keep the fork rebased on relevant upstream fixes where they remain compatible.

# Features
## Filesystem usage
Monitor your filesystem usage.

![Filesystem usage](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/filesystem_sensor.png)

## System
Monitor your OpenMediaVault system.

![System](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/system_sensors.png)

## Disk smart
Monitor your disks.

![Disk info](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/disk_sensor.png)

# Install this fork

The fork is distributed as a release archive compatible with
[HACS](https://www.hacs.xyz/):

1. In HACS, open **Custom repositories**.
2. Add `https://github.com/VascoRodriges/homeassistant-openmediavault` as an
   **Integration** repository.
3. Install the latest release and restart Home Assistant.

When migrating from the upstream repository, add this custom repository and
reinstall the integration in place. Existing Home Assistant config entries and
entity IDs are retained because the integration domain remains `openmediavault`.

## Setup integration
Setup this integration for your OpenMediaVault NAS in Home Assistant via `Configuration -> Integrations -> Add -> OpenMediaVault`.
You can add this integration several times for different devices.

![Add Integration](https://raw.githubusercontent.com/tomaae/homeassistant-openmediavault/master/docs/assets/images/ui/setup_integration.png)
* "Name of the integration" - Friendly name for this NAS
* "Host" - Use hostname or IP
* "Use SSL" - Connect to OMV using SSL
* "Verify SSL certificate" - Validate SSL certificate (must be trusted certificate)

# Development
## Translation
To help out with the translation you need an account on Lokalise, the easiest way to get one is to [click here](https://lokalise.com/login/) then select "Log in with GitHub".
After you have created your account [click here to join OpenMediaVault project on Lokalise](https://app.lokalise.com/public/106503135ea170ab5e1f70.96389313/).

If you want to add translations for a language that is not listed please [open a Feature request](https://github.com/tomaae/homeassistant-openmediavault/issues/new?labels=enhancement&title=%5BLokalise%5D%20Add%20new%20translations%20language).

## Enabling debug
To enable debug for OpenMediaVault integration, add following to your configuration.yaml:
```
logger:
  default: info
  logs:
    custom_components.openmediavault: debug
```
