import { safeHandle } from "./utils";
import { SecurityService } from "../services/SecurityService";
import { parsePayload, pinSchema } from "./schemas";

export function registerSecurityHandlers(securityService: SecurityService) {
  safeHandle("verify-pin", async (_e, pin) => {
    const validPin = parsePayload(pinSchema, pin, "verify-pin");
    return await securityService.verifyPin(validPin);
  });

  safeHandle("set-pin", async (_e, pin) => {
    const validPin = parsePayload(pinSchema, pin, "set-pin");
    return await securityService.setPin(validPin);
  });

  safeHandle("disable-pin", async (_e, pin) => {
    const validPin = parsePayload(pinSchema, pin, "disable-pin");
    return await securityService.disablePin(validPin);
  });

  safeHandle("get-security-status", () => {
    return securityService.isEnabled();
  });
}
