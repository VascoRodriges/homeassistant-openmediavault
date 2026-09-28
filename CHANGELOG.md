# Changelog

## 1.6.0

* Register entity actions during integration setup using Home Assistant's current
  platform entity service API.
* Replace deprecated `via_device` device links with registry-backed
  `via_device_id` links.
* Prevent a deadlock when an OpenMediaVault session expires during an API query.
* Reject malformed API responses cleanly and avoid mutable query defaults.
* Normalize current OMV Compose background-job responses in a separately tested
  parser.
* Serialize Compose commands per entity and report validation/API failures to
  Home Assistant instead of silently accepting them.
* Add unit, formatting, security, hassfest, and HACS validation workflows.
* Modernize the release workflow and add translated action metadata.

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
