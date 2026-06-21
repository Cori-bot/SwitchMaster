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
  /** Détection (lecture seule, opt-in) du compte Riot connecté via le client local. */
  enableLcuDetection?: boolean;
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
