import React, { useMemo, useState } from "react";
import { Play, Star, Pencil, Trash2 } from "lucide-react";
import { DesignProps } from "../types";
import { Account } from "../../../shared/types";
import AddAccountModal from "../../components/AddAccountModal";
import ProTopBar from "./TopBar";
import AccountList from "./AccountList";
import "./pro.css";

export const ProLayout: React.FC<DesignProps> = ({
  accounts,
  activeAccountId,
  status,
  actions,
  onSwitchSession,
  onOpenSettings,
}) => {
  const [selectedId, setSelectedId] = useState<string | null>(activeAccountId);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editing, setEditing] = useState<Account | null>(null);

  const selected = useMemo(
    () =>
      accounts.find((a) => a.id === (selectedId ?? activeAccountId)) ??
      accounts[0] ??
      null,
    [accounts, selectedId, activeAccountId],
  );

  const handleAdd = async (data: Partial<Account>) => {
    if (editing) {
      await actions.updateAccount({ ...editing, ...data } as Account);
    } else {
      await actions.addAccount(data);
    }
    setIsAddOpen(false);
    setEditing(null);
  };

  const handleDelete = async (id: string) => {
    if (confirm("Delete this account?")) {
      await actions.deleteAccount(id);
    }
  };

  return (
    <div className="pro-layout" data-design="pro">
      <ProTopBar status={status} onOpenSettings={onOpenSettings} />

      <AccountList
        accounts={accounts}
        activeAccountId={activeAccountId}
        selectedId={selected?.id ?? null}
        onSelect={setSelectedId}
        onToggleFavorite={actions.toggleFavorite}
        onReorder={actions.reorderAccounts}
      />

      <section className="pro-detail" aria-label="Account detail">
        {!selected ? (
          <div className="pro-detail__empty">
            <p>No accounts yet.</p>
            <button className="pro-btn" onClick={() => setIsAddOpen(true)}>
              Add account
            </button>
          </div>
        ) : (
          <>
            <h1 className="pro-detail__title">{selected.name}</h1>
            <p className="pro-detail__subtitle">
              {selected.riotId || "No Riot ID"}
            </p>

            <div className="pro-card">
              <div className="pro-row">
                <span className="pro-row__label">Game</span>
                <span>
                  {selected.gameType === "league"
                    ? "League of Legends"
                    : "Valorant"}
                </span>
              </div>
              <div className="pro-row">
                <span className="pro-row__label">Launcher</span>
                <span>{selected.launcherType ?? "riot"}</span>
              </div>
              <div className="pro-row">
                <span className="pro-row__label">Rank</span>
                <span>{selected.stats?.rank ?? "Unranked"}</span>
              </div>
              <div className="pro-row">
                <span className="pro-row__label">Status</span>
                <span>
                  {selected.id === activeAccountId ? "Active" : "Inactive"}
                </span>
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
              <button
                className="pro-btn"
                onClick={() => onSwitchSession(selected.id)}
              >
                <Play size={12} /> Launch
              </button>
              <button
                className="pro-btn pro-btn--ghost"
                onClick={() => actions.toggleFavorite(selected)}
              >
                <Star
                  size={12}
                  fill={selected.isFavorite ? "currentColor" : "none"}
                />
                {selected.isFavorite ? "Unfavorite" : "Favorite"}
              </button>
              <button
                className="pro-btn pro-btn--ghost"
                onClick={() => {
                  setEditing(selected);
                  setIsAddOpen(true);
                }}
              >
                <Pencil size={12} /> Edit
              </button>
              <button
                className="pro-btn pro-btn--ghost"
                onClick={() => handleDelete(selected.id)}
              >
                <Trash2 size={12} /> Delete
              </button>
              <button
                className="pro-btn pro-btn--ghost"
                style={{ marginLeft: "auto" }}
                onClick={() => {
                  setEditing(null);
                  setIsAddOpen(true);
                }}
              >
                + New
              </button>
            </div>
          </>
        )}
      </section>

      <AddAccountModal
        isOpen={isAddOpen}
        onClose={() => {
          setIsAddOpen(false);
          setEditing(null);
        }}
        onAdd={handleAdd}
        editingAccount={editing}
      />
    </div>
  );
};

export default ProLayout;
