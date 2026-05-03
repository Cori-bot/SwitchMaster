import {
  ILauncherService,
  LauncherAdapter,
} from "../interfaces/ILauncherService";
import { SteamAdapter } from "./launchers/SteamAdapter";

export class LauncherFactory {
  private services: Map<string, ILauncherService> = new Map();
  private adapters: Map<string, LauncherAdapter> = new Map();

  constructor(services: ILauncherService[] = []) {
    services.forEach((s) => this.registerService(s));
    // Register built-in adapters (TcNo-style capture/restore).
    this.registerAdapter(new SteamAdapter());
    // TODO: register UbisoftAdapter and BattleNetAdapter once implemented.
  }

  public registerService(service: ILauncherService) {
    this.services.set(service.id, service);
  }

  public getService(launcherId: string): ILauncherService {
    const service = this.services.get(launcherId);
    if (!service) {
      throw new Error(`Launcher service not supported: ${launcherId}`);
    }
    return service;
  }

  public registerAdapter(adapter: LauncherAdapter) {
    this.adapters.set(adapter.id, adapter);
  }

  public getAdapter(launcherId: string): LauncherAdapter {
    const adapter = this.adapters.get(launcherId);
    if (!adapter) {
      throw new Error(`Launcher adapter not supported: ${launcherId}`);
    }
    return adapter;
  }

  public listAdapters(): LauncherAdapter[] {
    return Array.from(this.adapters.values());
  }
}
