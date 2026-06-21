export interface GameStats {
  rank?: string;
  rankIcon?: string;
  lastUpdate: number;
}

export interface Config {
  riotPath: string;
  theme?: string;
  autoStart: boolean;
  startMinimized: boolean;
  minimizeToTray: boolean;
  showQuitModal: boolean;
  lastAccountId?: string | null;
  security?: {
    enabled: boolean;
    pinHash?: string | null;
    failedAttempts?: number;
    lockedUntil?: number;
  };
  hasSeenOnboarding: boolean;
  valorantAutoLockAgent?: string | null;
  enableGPU?: boolean;

  riotLaunchDelay?: number;
  showLaunchGamePopup?: boolean;
  activeDesignModule?: "classic" | "modern" | "pro";
  autoUpdate?: boolean;
}

export interface Account {
  id: string;
  name: string;
  gameType: "league" | "valorant";
  launcherType?: "riot" | "steam" | "epic";
  riotId: string;
  username?: string;
  password?: string;
  cardImage?: string;
  isFavorite?: boolean;
  lastUsed?: string;
  stats?: GameStats | null;
  timestamp?: number;
  tags?: string[];
  notes?: string;
  accentColor?: string;
}

export interface AppStatus {
  status: string;
  accountId?: string;
  accountName?: string;
}

/**
 * Verdict de connexion Riot extrait des logs du Riot Client (poussé du main
 * vers le renderer via IPC `riot-login-status`).
 */
export type RiotLoginPhase = "success" | "error" | "captcha" | "info";

export interface RiotLoginEvent {
  phase: RiotLoginPhase;
  /** Code d'erreur RSO brut le cas échéant (ex: "40005803"). */
  code?: string;
  /** Message clair en français, prêt à afficher. */
  message: string;
  /** Extrait de la ligne de log d'origine (diagnostic). */
  raw?: string;
}
