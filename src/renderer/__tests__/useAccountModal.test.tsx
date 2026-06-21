import { describe, it, expect, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useAccountModal } from "../hooks/useAccountModal";
import { Account } from "../../shared/types";

const makeActions = () => ({
  addAccount: vi.fn().mockResolvedValue(undefined),
  updateAccount: vi.fn().mockResolvedValue(undefined),
});

const acc: Account = {
  id: "a1",
  name: "X",
  gameType: "valorant",
  riotId: "X#EU",
};

describe("useAccountModal", () => {
  it("openAdd ouvre en mode création", () => {
    const { result } = renderHook(() => useAccountModal(makeActions()));
    act(() => result.current.openAdd());
    expect(result.current.isOpen).toBe(true);
    expect(result.current.editing).toBeNull();
  });

  it("openEdit ouvre avec le compte à éditer", () => {
    const { result } = renderHook(() => useAccountModal(makeActions()));
    act(() => result.current.openEdit(acc));
    expect(result.current.isOpen).toBe(true);
    expect(result.current.editing).toEqual(acc);
  });

  it("submit appelle addAccount en création puis ferme", async () => {
    const actions = makeActions();
    const { result } = renderHook(() => useAccountModal(actions));
    act(() => result.current.openAdd());
    await act(async () => {
      await result.current.submit({ name: "New" });
    });
    expect(actions.addAccount).toHaveBeenCalledWith({ name: "New" });
    expect(actions.updateAccount).not.toHaveBeenCalled();
    expect(result.current.isOpen).toBe(false);
  });

  it("submit appelle updateAccount en édition (merge)", async () => {
    const actions = makeActions();
    const { result } = renderHook(() => useAccountModal(actions));
    act(() => result.current.openEdit(acc));
    await act(async () => {
      await result.current.submit({ name: "Y" });
    });
    expect(actions.updateAccount).toHaveBeenCalledWith({ ...acc, name: "Y" });
    expect(result.current.isOpen).toBe(false);
  });

  it("close réinitialise l'état", () => {
    const { result } = renderHook(() => useAccountModal(makeActions()));
    act(() => result.current.openEdit(acc));
    act(() => result.current.close());
    expect(result.current.isOpen).toBe(false);
    expect(result.current.editing).toBeNull();
  });
});
