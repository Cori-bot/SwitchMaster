import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ProLayout from "../designs/pro/ProLayout";
import { Account, Config } from "../../shared/types";
import { DesignProps } from "../designs/types";

beforeAll(() => {
  if (!(globalThis as any).ResizeObserver) {
    (globalThis as any).ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  }
});

const accounts: Account[] = [
  { id: "a1", name: "Alice", gameType: "valorant", riotId: "Alice#EUW" },
  { id: "a2", name: "Bob", gameType: "league", riotId: "Bob#EUW" },
];

const config: Config = {
  riotPath: "",
  autoStart: false,
  startMinimized: false,
  minimizeToTray: false,
  showQuitModal: true,
  hasSeenOnboarding: true,
  activeDesignModule: "pro",
};

const makeProps = (overrides: Partial<DesignProps> = {}): DesignProps => ({
  accounts,
  activeAccountId: "a1",
  config,
  status: { status: "Prêt" },
  actions: {
    login: vi.fn().mockResolvedValue(undefined),
    deleteAccount: vi.fn().mockResolvedValue(undefined),
    updateAccount: vi.fn().mockResolvedValue(undefined),
    reorderAccounts: vi.fn().mockResolvedValue(undefined),
    toggleFavorite: vi.fn().mockResolvedValue(undefined),
    addAccount: vi.fn().mockResolvedValue(undefined),
  },
  onSwitchSession: vi.fn().mockResolvedValue(undefined),
  onOpenSettings: vi.fn(),
  systemActions: {
    openSecurityModal: vi.fn(),
    openGpuModal: vi.fn(),
    checkUpdates: vi.fn(),
    selectRiotPath: vi.fn(),
    updateConfig: vi.fn().mockResolvedValue(undefined),
  },
  ...overrides,
});

describe("ProLayout", () => {
  it("affiche la liste des comptes", () => {
    render(<ProLayout {...makeProps()} />);
    expect(screen.getByTestId("pro-account-a1")).toBeInTheDocument();
    expect(screen.getByTestId("pro-account-a2")).toBeInTheDocument();
  });

  it("ouvre les réglages quand openSettingsSignal change", () => {
    const { rerender } = render(
      <ProLayout {...makeProps({ openSettingsSignal: 0 })} />,
    );
    expect(screen.queryByText("Paramètres")).toBeNull();
    rerender(<ProLayout {...makeProps({ openSettingsSignal: 1 })} />);
    expect(screen.getByText("Paramètres")).toBeInTheDocument();
  });

  it("filtre les comptes via la recherche", () => {
    render(<ProLayout {...makeProps()} />);
    const input = screen.getByLabelText("Rechercher un compte");
    fireEvent.change(input, { target: { value: "bob" } });
    expect(screen.queryByTestId("pro-account-a1")).toBeNull();
    expect(screen.getByTestId("pro-account-a2")).toBeInTheDocument();
  });
});
