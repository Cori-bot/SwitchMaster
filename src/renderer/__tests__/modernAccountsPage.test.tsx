import { describe, it, expect, vi, beforeAll } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import AccountsPage from "../designs/modern/pages/AccountsPage";
import { Account } from "../../shared/types";

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
  {
    id: "a1",
    name: "Alice",
    gameType: "valorant",
    riotId: "Alice#EUW",
    isFavorite: true,
  },
  { id: "a2", name: "Bob", gameType: "league", riotId: "Bob#EUW" },
];

const baseProps = {
  accounts,
  favorites: ["a1"],
  onToggleFavorite: vi.fn().mockResolvedValue(undefined),
  onAddAccount: vi.fn(),
  onWallpaperClick: vi.fn(),
  onReorder: vi.fn(),
};

describe("Modern AccountsPage", () => {
  it("affiche toutes les cartes", () => {
    render(<AccountsPage {...baseProps} />);
    expect(screen.getByTestId("modern-account-a1")).toBeInTheDocument();
    expect(screen.getByTestId("modern-account-a2")).toBeInTheDocument();
  });

  it("filtre par jeu (League)", () => {
    render(<AccountsPage {...baseProps} />);
    fireEvent.click(screen.getByText("League"));
    expect(screen.queryByTestId("modern-account-a1")).toBeNull();
    expect(screen.getByTestId("modern-account-a2")).toBeInTheDocument();
  });

  it("filtre par favoris", () => {
    render(<AccountsPage {...baseProps} />);
    const favFilter = document.querySelector(".filter-favorite") as HTMLElement;
    fireEvent.click(favFilter);
    expect(screen.getByTestId("modern-account-a1")).toBeInTheDocument();
    expect(screen.queryByTestId("modern-account-a2")).toBeNull();
  });
});
