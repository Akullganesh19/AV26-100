## 2024-05-15 — Direct axios calls in frontend

**Complexity found:** Components `DiagnosticsCenter.tsx`, `SimulationLab.tsx`, `StrategicMap.tsx`, `TacticalAlerts.tsx`, and `Dashboard.tsx` imported and used raw `axios` directly, bypassing the customized `apiClient` instance.

**Why it existed:** Likely developed quickly without realizing a centralized API client with JWT injection (`apiClient`) was already implemented in `api/client.ts`.

**Eliminated:** Direct `axios` imports, redundant token injections, and manual `import.meta.env.VITE_API_URL` string interpolations across 5 components.

**Net change:** 5 abstractions removed (manual auth/URL logic), simplified API calls across 5 major components.

**Next target:** Any other duplicated API clients or manually handled auth logic.
