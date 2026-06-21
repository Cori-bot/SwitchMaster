import React from "react";
import { Settings, Search } from "lucide-react";
import { AppStatus } from "../../../shared/types";

interface ProTopBarProps {
  status: AppStatus;
  onOpenSettings: () => void;
  query: string;
  onQueryChange: (value: string) => void;
}

export const ProTopBar: React.FC<ProTopBarProps> = ({
  status,
  onOpenSettings,
  query,
  onQueryChange,
}) => {
  return (
    <header className="pro-topbar">
      <div className="pro-topbar__brand">SwitchMaster</div>
      <div className="pro-topbar__status" data-testid="pro-status">
        {status.status}
        {status.accountName ? `  ·  ${status.accountName}` : ""}
      </div>
      <div className="pro-topbar__search">
        <Search size={12} />
        <input
          type="text"
          placeholder="Rechercher un compte..."
          value={query}
          onChange={(e) => onQueryChange(e.target.value)}
          aria-label="Rechercher un compte"
        />
      </div>
      <button
        className="pro-iconbtn"
        onClick={onOpenSettings}
        title="Settings"
        aria-label="Settings"
      >
        <Settings size={14} />
      </button>
    </header>
  );
};

export default ProTopBar;
