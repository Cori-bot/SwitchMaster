import React from "react";
import { render, screen } from "@testing-library/react";
import App from "../App";
import { vi, describe, it, expect, beforeEach } from "vitest";

// Mock des images
vi.mock("@assets/logo.png", () => ({ default: "mock-logo" }));
vi.mock("@assets/valorant.png", () => ({ default: "mock-val" }));
vi.mock("@assets/league.png", () => ({ default: "mock-lol" }));

// Mock global window.ipc
beforeEach(() => {
  vi.clearAllMocks();
  (window as any).ipc = {
    invoke: vi.fn().mockResolvedValue({}),
    on: vi.fn(() => vi.fn()),
    send: vi.fn(),
  };
});

// Mock des hooks globaux
vi.mock("../hooks/useAccounts", () => ({
  useAccounts: () => ({
    accounts: [],
    refreshAccounts: vi.fn(),
    deleteAccount: vi.fn(),
    updateAccount: vi.fn(),
    reorderAccounts: vi.fn(),
    addAccount: vi.fn(),
    loading: false,
  }),
}));
vi.mock("../hooks/useConfig", () => ({
  useConfig: () => ({
    config: { hasSeenOnboarding: true },
    refreshConfig: vi.fn(),
    updateConfig: vi.fn(),
    selectRiotPath: vi.fn(),
  }),
}));
vi.mock("../hooks/useSecurity", () => ({
  useSecurity: () => ({
    checkSecurityStatus: vi.fn().mockResolvedValue(false),
    isLocked: false,
    verifyPin: vi.fn(),
    setPin: vi.fn(),
    disablePin: vi.fn(),
  }),
}));
vi.mock("../hooks/useNotifications", () => ({
  useNotifications: () => ({ notifications: [], removeNotification: vi.fn() }),
}));
vi.mock("../hooks/useAppIpc", () => ({
  useAppIpc: () => ({
    status: { status: "Prêt" },
    updateInfo: { isOpen: false },
    isQuitModalOpen: false,
    setIsQuitModalOpen: vi.fn(),
  }),
}));

// Mock des composants critiques
vi.mock("../components/LoadingScreen", () => ({
  default: () => <div data-testid="ready">READY</div>,
}));
vi.mock("framer-motion", () => {
  // Proxy : n'importe quel tag (m.div, motion.button, ...) devient un
  // composant passe-plat qui ignore les props d'animation.
  const makeProxy = () =>
    new Proxy(
      {},
      {
        get: (_t, tag: string) => {
          const Comp = ({ children, ...props }: any) => {
            const {
              whileHover,
              whileTap,
              initial,
              animate,
              exit,
              variants,
              transition,
              layout,
              ...rest
            } = props;
            return React.createElement(tag, rest, children);
          };
          return Comp;
        },
      },
    );
  return {
    motion: makeProxy(),
    m: makeProxy(),
    AnimatePresence: ({ children }: any) => <>{children}</>,
    LazyMotion: ({ children }: any) => <>{children}</>,
    domAnimation: {},
  };
});

describe("App Root", () => {
  it("doit monter l'application", async () => {
    render(<App />);
    // Le design actif (classic) est chargé via React.lazy : on attend qu'il
    // se résolve avant d'asserter la présence de la sidebar.
    expect(await screen.findByText("Comptes")).toBeInTheDocument();
  });
});
