# Changelog

## 1.5.1

* Document the fork, upstream attribution, HACS installation, maintained changes,
  and planned work.
* Replace deprecated Home Assistant `DeviceInfo` default fields.

## 1.5.0

* Add OMV 8.5 authentication compatibility inherited from upstream.
* Support the current OMV Compose background-job API and project UUID discovery.
* Add entity-targeted Compose start, stop, and restart actions.
* Remove the local arbitrary OMV RPC action.
* Preserve controller liveness by releasing update locks after failures.
