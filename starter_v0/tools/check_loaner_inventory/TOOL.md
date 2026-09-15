---
name: check_loaner_inventory
track: bonus
kind: local_inventory
provider: mock_loaner_inventory
requires_env: []
inputs: [device_type, location, os_family, max_results]
outputs: [available_count, matches, snapshot_at]
side_effect: false
---
# check_loaner_inventory

Reads deterministic synthetic loaner-device inventory for temporary replacement
devices. It is read-only and does not reserve, assign, or create tickets.

Use this for availability questions about loaner, spare, replacement, temporary,
or borrowable devices. It should not be used for diagnosing a specific broken
asset unless the user also asks for diagnostics.
