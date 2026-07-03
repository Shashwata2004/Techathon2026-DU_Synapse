# Assumptions

- The corrected v1.2 fixed office setup is authoritative: 3 rooms, 2 fans per room, 3 lights per room, 15 devices total.
- Later PDF references to 18 devices are treated as leftover text from an earlier version.
- The backend in-memory store is the only source of truth during the local demo.
- Demo control endpoints are local-only utilities, not production features.
- The Discord bot must work without `OPENAI_API_KEY`.
- One representative Wokwi room schematic is enough for the hardware deliverable.
