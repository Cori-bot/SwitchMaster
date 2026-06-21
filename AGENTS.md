# SwitchMaster Agent Guide

This repository contains **SwitchMaster**, an Electron application for switching between multi-accounts (Riot Games, etc.), built with React, TypeScript, Vite, and Tailwind CSS.

## 1. Project Overview & Environment

- **Runtime:** Electron 42.4.1 (Node 20 — figé par la CI Windows)
- **Frontend:** React 19, TypeScript 5.9
- **Build Tool:** Vite 7.3 (Tailwind branché via `@tailwindcss/vite`)
- **Styling:** Tailwind CSS 4.1 (v4 — configurée via le plugin Vite + `@theme` dans le CSS, **pas** de `tailwind.config.js`)
- **State:** Custom Hooks uniquement (`useConfig`, `useAccountManager`, `useAccounts`, `useSecurity`, `useNotifications`, `useAppIpc`) — il n'y a **PAS** de React Context provider (`src/renderer/contexts/` est vide).
- **Package Manager:** `pnpm` (Strictly required - do NOT use npm/yarn)

### Setup & Commands

| Action            | Command                    | Description                                                             |
| :---------------- | :------------------------- | :---------------------------------------------------------------------- |
| **Install**       | `pnpm install`             | Install all dependencies.                                               |
| **Dev**           | `pnpm dev`                 | Start Electron + Vite dev server concurrently.                          |
| **Build**         | `pnpm build`               | Run full production build (Renderer -> Main -> Builder).                |
| **Release**       | `pnpm release`             | Build and publish to GitHub Releases.                                   |
| **Test**          | `pnpm test`                | Run all unit tests via Vitest.                                          |
| **Test (Single)** | `pnpm test <path/to/file>` | Run a specific test file (e.g., `pnpm test src/renderer/App.test.tsx`). |
| **Coverage**      | `pnpm test:coverage`       | Generate test coverage report.                                          |
| **Typecheck**     | `pnpm typecheck`           | TypeScript check (`tsc --noEmit`). Également lancé par la CI.           |
| **Format**        | `npx prettier --write .`   | Prettier (automatisé au commit via husky + lint-staged).                |
| **Update Deps**   | `pnpm up-dep`              | Update dependencies (Use with extreme caution).                         |

## 2. Directory Structure

- **`src/main/`**: Electron Main Process (Node.js environment).
  - **`services/`**: Core business logic classes — `AccountService`, `ConfigService`, `SecurityService`, `SessionService`, `StatsService`, `SystemService`, `RiotAutomationService`, `LauncherFactory`, `launchers/SteamAdapter`.
    - _Pattern:_ Services are instantiated in `main.ts` and injected into IPC handlers.
  - **`ipc/`**: IPC handlers split by domain — `accountHandlers`, `configHandlers`, `riotHandlers`, `securityHandlers`, `updateHandlers`, `miscHandlers` — plus `schemas.ts` (zod), `utils.ts` (`safeHandle` / `parsePayload`), `types.ts`.
  - **`interfaces/`**: `ILauncherService.ts` (contracts `ILauncherService` and `LauncherAdapter`).
  - **`valorant-api/`**: Riot OAuth (RSO) webview auth — `riotWebviewAuth.ts`, `riotAuthService.ts`.
  - `main.ts`: Application entry point, window creation, CSP, single-instance lock, and service orchestration.
  - `ipc.ts`: IPC handler registration (delegates to `ipc/*Handlers`).
  - `window.ts`: `BrowserWindow` creation + hardening (`sandbox`, `contextIsolation`, navigation guards).
  - `updater.ts`: electron-updater wiring.
  - `logger.ts`: Custom logging wrapper (`devLog`, `devError`).
  - `preload.js`: `contextBridge` exposing a minimal `ipc` API with strict channel allowlists.
- **`src/renderer/`**: React Renderer Process (Browser environment).
  - `components/`: Functional UI components (`PascalCase.tsx`), including `AddAccount/` and `Modals/`.
  - `designs/`: Swappable UI designs lazy-loaded via `registry.ts` — `classic/` (`ClassicLayout`), `modern/` (`ModernLayout` + `modern.css`), `pro/` (`ProLayout`, `AccountList` drag&drop, `pro.css`). Active design = `config.activeDesignModule`.
  - `hooks/`: Custom hooks (`useHook.ts`) — **this is where global state lives** (no Context).
  - `constants/`: `colors`, `typography`, `ui`.
  - `styles/`: `tokens.css` (design tokens `--sm-*`, single source of truth).
  - `utils/`: utilities (e.g. `logger.ts`).
- **`src/shared/`**: Types & zod validation shared between main and renderer (`types.ts`, `validation.ts`).
- **`src/assets/`**: Static assets (games, launchers, branding).
- **`src/scripts/`**: PowerShell scripts (`automate_login.ps1`, `detect_games.ps1`).

## 3. Code Style & Conventions

### TypeScript & General

- **Strict Mode:** Enabled in `tsconfig.json`. **NO** `any` types. Use proper interfaces/types.
- **Interfaces:** Use `interface` for object definitions, `type` for unions/primitives.
- **Path Aliases:**
  - `@/` -> `src/renderer/` (Renderer only)
  - `@assets/` -> `src/assets/`
- **Naming:**
  - **Variables/Functions:** `camelCase`
  - **Components/Classes:** `PascalCase`
  - **Constants:** `UPPER_SNAKE_CASE`
  - **Files:** `camelCase.ts` (logic/utils), `PascalCase.tsx` (components/classes).

### React (Renderer)

- **Components:** Functional components only. `const Component = () => {}`.
- **Styling:** **Tailwind CSS v4** only.
  - Thème et tokens via `@theme` (dans `src/renderer/index.css`) alimentés par `src/renderer/styles/tokens.css`.
  - **NO** inline `style={{}}` unless dynamic (e.g., user-defined background images).
- **Icons:** Use `lucide-react`.
- **State:**
  - Prefer `useState` for local component state.
  - Global state is encapsulated in custom hooks (`useConfig`, `useAccountManager`, `useAccounts`, `useSecurity`) — **no** `useContext` for global state.
- **Animation:** `framer-motion` en mode **LazyMotion** : `import { LazyMotion, domAnimation, m } from "framer-motion"`. Le wrapper `<LazyMotion features={domAnimation} strict>` est posé dans `index.tsx` ; les composants utilisent `m.div` / `AnimatePresence`. **Ne PAS** utiliser `motion.*` (interdit par le strict mode, casse le tree-shaking).

### Electron (Main)

- **Architecture:** Service-based pattern.
  - Logic belongs in `src/main/services/`, NOT in `main.ts` or `ipc.ts`.
  - Services should be singletons or instantiated once in `main.ts`.
- **IPC Communication:**
  - **Renderer:** `window.ipc.invoke('channel', data)` (exposé par le preload via `contextBridge`, canaux en allowlist).
  - **Main:** handlers enregistrés via `safeHandle` dans `src/main/ipc/*Handlers.ts`.
  - **Validation obligatoire :** valider chaque payload avec zod (`src/main/ipc/schemas.ts` via `parsePayload`, ou `src/shared/validation.ts` pour les comptes) AVANT tout traitement. Un payload invalide rejette la promesse `invoke()`.
  - Type the data payloads in `src/shared/types.ts` or `src/main/ipc/types.ts`.
- **File System:** Use `fs-extra` for all FS operations (provides Promise support).
- **Paths:** ALWAYS use `path.join()`. Never use string concatenation for file paths.
- **Logging:** Use `devLog`/`devError` from `./logger`. **NO** `console.log` in production code.

### Imports Ordering

1. **External:** `react`, `electron`, third-party libs.
2. **Internal Absolute:** `@/components/...`, `@assets/...`.
3. **Internal Relative:** `./utils`, `../hooks`.
4. **Styles:** `./index.css`.

## 4. Testing Guidelines

- **Framework:** Vitest + React Testing Library.
- **Location:** `src/__tests__` (main process) and `src/renderer/__tests__` (renderer).
- **Naming:** `Component.test.tsx` or `logic.test.ts`.
- **Mocking:**
  - Mock the preload `ipc` API in renderer tests.
  - Mock `fs-extra` / `child_process` in main process tests.

```typescript
// Example Renderer Test
import { render, screen } from "@testing-library/react";
import AccountCard from "./AccountCard";

describe("AccountCard", () => {
  it("should render account name", () => {
    const mockAccount = { id: "1", name: "PlayerOne" /* ... */ };
    render(<AccountCard account={mockAccount} />);
    expect(screen.getByText("PlayerOne")).toBeInTheDocument();
  });
});

// Example Main Process Test
import { describe, it, expect, vi } from "vitest";
import { ConfigService } from "../services/ConfigService";

vi.mock("fs-extra"); // Auto-mock fs-extra

describe("ConfigService", () => {
  it("should load default config if file missing", async () => {
    const service = new ConfigService();
    const config = await service.getConfig();
    expect(config.enableGPU).toBe(false);
  });
});
```

## 5. Critical Rules for Agents

1.  **Read First:** Always inspect `package.json`, `tsconfig.json`, and related source files before changing configuration or architecture.
2.  **No Blind Installs:** Do not run `npm install` or `pnpm install` for new packages without explicit user permission.
3.  **Absolute Paths:** ALWAYS use full absolute paths for file operations (e.g., `D:\Code\SwitchMaster-v2\src\main\main.ts`).
4.  **Preserve Style:** Match indentation (2 spaces), quoting (double quotes), and existing code patterns.
5.  **Type Safety:** Verify changes with `pnpm typecheck` after significant refactoring.
6.  **No Regressions:** Run `pnpm test` to verify changes don't break existing functionality.
7.  **Error Handling:**
    - Use `try/catch` for all async operations (IPC, FS, Network).
    - Log errors using `devError` in the Main process.
    - Handle UI errors gracefully (e.g., Error Boundaries or Toast notifications).
8.  **Atomic Changes:** Make small, focused changes. Don't rewrite entire files unless necessary.
9.  **Dependencies:** Use existing libraries (`zod`, `lucide-react`, `@dnd-kit`, `cmdk`, etc.) before suggesting new ones.

## 6. Common Patterns & Troubleshooting

- **"Module not found":** Check `tsconfig.json` path aliases. Renderer code cannot import Main process code directly (use `src/shared` for shared types).
- **IPC Errors:** Ensure the channel name matches exactly across `src/main/preload.js` (allowlist), `src/main/ipc/*Handlers.ts`, and `src/renderer/hooks/useAppIpc.ts`. A zod validation failure on the payload will reject the `invoke()` promise.
- **Tailwind (v4):** Pas de `tailwind.config.js`. La config passe par le plugin `@tailwindcss/vite` (dans `vite.config.ts`) et le thème via `@theme` dans `src/renderer/index.css` (tokens dans `src/renderer/styles/tokens.css`).
- **Designs:** Le design actif est résolu dans `App.tsx` via `config.activeDesignModule` et le `DesignRegistry` lazy (`src/renderer/designs/registry.ts`). Les composants des designs sont code-splittés (`design-classic` / `design-modern` / `design-pro`).
- **Window Management:** `BrowserWindow` instances are managed in `src/main/window.ts`. Use `mainWindow?.webContents.send` for push updates.
