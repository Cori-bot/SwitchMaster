import { Config } from "../../shared/types";
import { safeHandle } from "./utils";
import { ConfigService } from "../services/ConfigService";
import { parsePayload, configSchema } from "./schemas";

export function registerConfigHandlers(configService: ConfigService) {
  safeHandle("get-config", () => configService.getConfig());
  safeHandle("save-config", async (_e, config) => {
    const validated = parsePayload(configSchema, config, "save-config");
    const cleanConfig = { ...(validated as Partial<Config>) };
    await configService.saveConfig(cleanConfig);
    return true;
  });
}
