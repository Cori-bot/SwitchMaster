import { Client } from "@xhayper/discord-rpc";
import { devLog } from "../logger";

export interface DiscordPresence {
  state?: string;
  details?: string;
  largeImageKey?: string;
  largeImageText?: string;
}

export class DiscordRpcService {
  private client: Client | null = null;
  private connected = false;
  private pending: DiscordPresence | null = null;

  public async start(clientId: string): Promise<void> {
    try {
      this.client = new Client({ clientId });
      this.client.on("ready", () => {
        this.connected = true;
        devLog("[DiscordRpc] Connected");
        if (this.pending) {
          this.setPresence(this.pending).catch(() => undefined);
          this.pending = null;
        }
      });
      await this.client.login();
    } catch (err) {
      // Discord likely not running — swallow.
      devLog("[DiscordRpc] Failed to start (Discord likely not running):", err);
      this.client = null;
      this.connected = false;
    }
  }

  public async setPresence(presence: DiscordPresence): Promise<void> {
    if (!this.client || !this.connected) {
      this.pending = presence;
      return;
    }
    try {
      await this.client.user?.setActivity({
        state: presence.state,
        details: presence.details,
        largeImageKey: presence.largeImageKey,
        largeImageText: presence.largeImageText,
        instance: false,
      });
    } catch (err) {
      devLog("[DiscordRpc] setPresence error:", err);
    }
  }

  public async stop(): Promise<void> {
    if (!this.client) return;
    try {
      await this.client.destroy();
    } catch (err) {
      devLog("[DiscordRpc] stop error:", err);
    }
    this.client = null;
    this.connected = false;
  }
}
