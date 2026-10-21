## 2024-10-24 — Centralize API Client Migration
**Risk identified:** Raw `axios` usage is scattered across React components instead of using the centralized `apiClient`. This risks inconsistent error handling, duplicated base URL configs, and broken authentication since raw axios requests bypass interceptors.
**Migration target:** Consistent use of `apiClient` from `src/api/client.ts` for all network requests.
**Migrated this session:** Replaced raw `axios` imports and URL strings with `apiClient` in `Dashboard.tsx`, `TacticalAlerts.tsx`, `StrategicMap.tsx`, `DiagnosticsCenter.tsx`, and `SimulationLab.tsx`.
**Remaining:** Verify if there are other frontend files or utility functions that still use raw `axios` instead of `apiClient`.
**Next session:** Complete migration of any remaining raw `axios` usages and consider extracting inline API calls into a dedicated API layer or custom hooks.
