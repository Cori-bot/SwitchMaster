import { useEffect, useState, useCallback } from "react";
import { Command } from "cmdk";
import { Account } from "../../shared/types";

export interface CommandPaletteSystemActions {
  openSecurityModal?: (mode: "set" | "disable" | null) => void;
  checkUpdates?: () => void | Promise<unknown>;
  /** Verrouille immédiatement l'app si un PIN est configuré, sinon ouvre la définition de PIN. */
  onLock?: () => void | Promise<unknown>;
}

export interface CommandPaletteProps {
  accounts: Account[];
  onSwitchSession: (id: string) => void | Promise<void>;
  systemActions?: CommandPaletteSystemActions;
  onOpenSettings?: () => void;
  /** For testability — force initial open state. */
  initialOpen?: boolean;
}

export const CommandPalette = ({
  accounts,
  onSwitchSession,
  systemActions,
  onOpenSettings,
  initialOpen = false,
}: CommandPaletteProps) => {
  const [open, setOpen] = useState(initialOpen);
  const [search, setSearch] = useState("");

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && (e.key === "k" || e.key === "K")) {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const close = useCallback(() => {
    setOpen(false);
    setSearch("");
  }, []);

  const run = useCallback(
    (fn: () => void | Promise<unknown>) => {
      Promise.resolve(fn()).catch(() => undefined);
      close();
    },
    [close],
  );

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Command Menu"
      data-testid="command-palette"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.55)",
        display: open ? "flex" : "none",
        alignItems: "flex-start",
        justifyContent: "center",
        paddingTop: "12vh",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          width: "min(560px, 92vw)",
          background: "var(--sm-color-surface, #1e1e1e)",
          color: "var(--sm-color-text, #fff)",
          border: "1px solid var(--sm-color-border, #333)",
          borderRadius: "var(--sm-radius-md, 16px)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
          overflow: "hidden",
          fontFamily:
            'ui-monospace, SFMono-Regular, Menlo, Monaco, "Cascadia Mono", monospace',
        }}
      >
        <Command.Input
          autoFocus
          placeholder="Type a command or search…"
          value={search}
          onValueChange={setSearch}
          style={{
            width: "100%",
            padding: "14px 16px",
            background: "transparent",
            border: "none",
            outline: "none",
            color: "inherit",
            fontSize: 15,
            borderBottom: "1px solid var(--sm-color-border, #333)",
          }}
        />
        <Command.List
          style={{
            maxHeight: 400,
            overflowY: "auto",
            padding: 6,
          }}
        >
          <Command.Empty style={{ padding: 16, opacity: 0.6 }}>
            No results found.
          </Command.Empty>

          {accounts.length > 0 && (
            <Command.Group heading="Accounts" style={groupStyle}>
              {accounts.map((acc) => (
                <Command.Item
                  key={acc.id}
                  value={`switch ${acc.name} ${acc.riotId} ${(acc.tags ?? []).join(" ")}`}
                  onSelect={() => run(() => onSwitchSession(acc.id))}
                  style={itemStyle}
                  data-testid={`cmd-account-${acc.id}`}
                >
                  <span>Switch to {acc.name}</span>
                  <span style={{ opacity: 0.5, fontSize: 12 }}>
                    {acc.riotId}
                  </span>
                </Command.Item>
              ))}
            </Command.Group>
          )}

          <Command.Group heading="System" style={groupStyle}>
            <Command.Item
              value="settings"
              onSelect={() => run(() => onOpenSettings?.())}
              style={itemStyle}
              data-testid="cmd-settings"
            >
              Settings
            </Command.Item>
            <Command.Item
              value="lock"
              onSelect={() => run(() => systemActions?.onLock?.())}
              style={itemStyle}
              data-testid="cmd-lock"
            >
              Lock
            </Command.Item>
            <Command.Item
              value="check updates"
              onSelect={() => run(() => systemActions?.checkUpdates?.())}
              style={itemStyle}
              data-testid="cmd-check-updates"
            >
              Check for Updates
            </Command.Item>
            <Command.Item
              value="quit exit"
              onSelect={() => run(() => window.ipc.invoke("confirm-quit"))}
              style={itemStyle}
              data-testid="cmd-quit"
            >
              Quit
            </Command.Item>
          </Command.Group>
        </Command.List>
      </div>
    </Command.Dialog>
  );
};

const groupStyle: React.CSSProperties = {
  fontSize: 11,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  opacity: 0.6,
  padding: "6px 10px",
};

const itemStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  gap: 8,
  padding: "10px 12px",
  borderRadius: 8,
  cursor: "pointer",
  fontSize: 14,
};

export default CommandPalette;
