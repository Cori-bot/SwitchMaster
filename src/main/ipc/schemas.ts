import { z } from "zod";

// Generic schemas reused across handlers
export const idSchema = z.string().min(1);
export const idArraySchema = z.array(z.string().min(1));
export const pinSchema = z.string().min(1).max(64);
export const booleanSchema = z.boolean();
export const steamProfileIdSchema = z
  .string()
  .regex(/^[a-zA-Z0-9 _-]{1,64}$/, "Identifiant de profil Steam invalide");

// Misc handler payloads
export const logToMainSchema = z.object({
  level: z.string(),
  args: z.array(z.unknown()).optional().default([]),
});

export const quitChoiceSchema = z.object({
  action: z.enum(["quit", "minimize"]),
  dontShowAgain: z.boolean(),
});

// Riot launch
export const launchGameDataSchema = z.union([
  z.string(),
  z.object({
    launcherType: z.string().optional(),
    gameId: z.string(),
    accountId: z.string().optional(),
    autoLaunch: z.boolean().optional(),
    credentials: z
      .object({
        username: z.string().optional(),
        password: z.string().optional(),
      })
      .passthrough()
      .optional(),
  }),
]);

// Config: keep loose because Config has many optional fields. Validate as object.
export const configSchema = z.record(z.string(), z.unknown());

/**
 * Helper that parses a payload with a zod schema and throws a descriptive error
 * if validation fails. Throwing here causes ipcMain.handle to reject the
 * renderer's invoke() promise, which is the desired safe behavior.
 */
export function parsePayload<T>(
  schema: z.ZodType<T>,
  payload: unknown,
  channel: string,
): T {
  const result = schema.safeParse(payload);
  if (!result.success) {
    throw new Error(
      `Invalid IPC payload for "${channel}": ${result.error.message}`,
    );
  }
  return result.data;
}
