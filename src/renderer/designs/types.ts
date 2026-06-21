import { Account, Config, AppStatus } from "../../shared/types";

export interface AccountActions {
  login: (account: Account, autoLaunch?: boolean) => Promise<void>;
  deleteAccount: (id: string) => Promise<void>;
  updateAccount: (account: Account) => Promise<void>;
  reorderAccounts: (ids: string[]) => Promise<void>;
  toggleFavorite: (account: Account) => Promise<void>;
  addAccount: (data: Partial<Account>) => Promise<void>;
}

export interface DesignProps {
  accounts: Account[];
  activeAccountId: string | null;
  config: Config;
  status: AppStatus;
  actions: AccountActions;

  // Core Navigation/Action
  onSwitchSession: (id: string, autoLaunch?: boolean) => Promise<void>;
  onOpenSettings: () => void;
  /**
   * Compteur incrémenté à chaque demande d'ouverture des réglages (ex:
   * depuis la command palette). Les designs doivent réagir à son changement
   * pour naviguer vers leur page Settings.
   */
  openSettingsSignal?: number;

  // System Metadata
  updateInfo?: any;

  // System Modals
  systemActions: {
    openSecurityModal: (mode: "set" | "disable") => void;
    openGpuModal: (target: boolean) => void;
    checkUpdates: () => void;
    selectRiotPath: () => void;
    updateConfig: (config: Partial<Config>) => Promise<void>;
  };
}
