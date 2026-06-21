import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import CommandPalette from "../renderer/components/CommandPalette";
import { Account } from "../shared/types";

beforeAll(() => {
  if (!(globalThis as any).ResizeObserver) {
    (globalThis as any).ResizeObserver = class {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  }
  if (!(Element.prototype as any).scrollIntoView) {
    (Element.prototype as any).scrollIntoView = function () {};
  }
});

const accounts: Account[] = [
  {
    id: "a1",
    name: "Alice",
    gameType: "valorant",
    riotId: "Alice#EUW",
  },
  {
    id: "a2",
    name: "Bob",
    gameType: "league",
    riotId: "Bob#EUW",
  },
];

describe("CommandPalette", () => {
  it("opens on Ctrl+K and shows account commands", () => {
    const onSwitch = vi.fn();
    render(<CommandPalette accounts={accounts} onSwitchSession={onSwitch} />);

    // Initially closed → palette element not visible
    expect(screen.queryByPlaceholderText(/Type a command/i)).toBeNull();

    act(() => {
      fireEvent.keyDown(window, { key: "k", ctrlKey: true });
    });

    expect(screen.getByPlaceholderText(/Type a command/i)).toBeInTheDocument();
    expect(screen.getByText(/Switch to Alice/)).toBeInTheDocument();
  });

  it("executes a command on selection", () => {
    const onSwitch = vi.fn();
    render(
      <CommandPalette
        accounts={accounts}
        onSwitchSession={onSwitch}
        initialOpen
      />,
    );

    const item = screen.getByTestId("cmd-account-a1");
    fireEvent.click(item);

    expect(onSwitch).toHaveBeenCalledWith("a1");
  });

  it("la commande Settings appelle onOpenSettings", () => {
    const onOpenSettings = vi.fn();
    render(
      <CommandPalette
        accounts={accounts}
        onSwitchSession={vi.fn()}
        onOpenSettings={onOpenSettings}
        initialOpen
      />,
    );

    fireEvent.click(screen.getByTestId("cmd-settings"));
    expect(onOpenSettings).toHaveBeenCalled();
  });

  it("la commande Lock appelle systemActions.onLock", () => {
    const onLock = vi.fn();
    render(
      <CommandPalette
        accounts={accounts}
        onSwitchSession={vi.fn()}
        systemActions={{ onLock }}
        initialOpen
      />,
    );

    fireEvent.click(screen.getByTestId("cmd-lock"));
    expect(onLock).toHaveBeenCalled();
  });
});
