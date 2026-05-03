export interface ILauncherCredentials {
  username: string;
  password?: string;
  method?: "oauth" | "credentials";
}

export interface ILauncherService {
  /** Unique identifier (e.g., 'riot', 'steam') */
  readonly id: string;

  /** Launches the launcher client (without necessarily launching the game) */
  launchClient(): Promise<void>;

  /** Launches a specific game managed by this launcher */
  launchGame(gameId: string): Promise<void>;

  /** Performs authentication (if supported) */
  login(credentials: ILauncherCredentials): Promise<void>;

  /** Kills all processes associated with this launcher */
  killAll(): Promise<void>;

  /** Detects if the launcher is installed on the machine */
  detectInstallation(): Promise<string | null>;

  /** Checks if the client is currently running */
  isRunning(): Promise<boolean>;
}

/**
 * Generic launcher adapter shape (TcNo-inspired capture/restore profile model).
 * Implemented by per-launcher adapters under `services/launchers/`.
 */
export interface LauncherAdapter {
  readonly id: string; // 'riot' | 'steam' | 'ubisoft' | 'battlenet'
  readonly displayName: string;
  isInstalled(): Promise<boolean>;
  killProcesses(): Promise<void>;
  launchClient(args?: string[]): Promise<void>;
  /** Snapshot the currently logged-in user's profile artifacts. */
  captureProfile(accountId: string): Promise<void>;
  /** Restore a previously captured profile snapshot. */
  restoreProfile(accountId: string): Promise<void>;
  /** Optional automated login (Riot legacy path). */
  login?(credentials: ILauncherCredentials): Promise<void>;
}
