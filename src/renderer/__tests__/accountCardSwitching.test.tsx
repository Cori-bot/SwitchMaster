import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import AccountCard from "../components/AccountCard";
import { Account } from "../../shared/types";

const acc: Account = {
  id: "a1",
  name: "Alice",
  gameType: "valorant",
  riotId: "Alice#EU",
};

const noop = vi.fn();
const dragProps = {
  onDragStart: noop,
  onDragOver: noop,
  onDragEnd: noop,
  onDragEnter: noop,
  onDrop: noop,
};
const baseProps = {
  account: acc,
  onSwitch: noop,
  onDelete: noop,
  onEdit: noop,
  onToggleFavorite: noop,
  ...dragProps,
};

describe("AccountCard — feedback de switch", () => {
  it("affiche « Connexion… » et désactive le bouton pendant le switch", () => {
    render(<AccountCard {...baseProps} isSwitching />);
    expect(screen.getByText("Connexion…")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Connexion/i })).toBeDisabled();
  });

  it("affiche « Se connecter » au repos", () => {
    render(<AccountCard {...baseProps} />);
    expect(screen.getByText("Se connecter")).toBeInTheDocument();
  });
});
