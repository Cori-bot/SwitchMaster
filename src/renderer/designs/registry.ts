import { lazy } from "react";

export const DesignRegistry = {
  classic: lazy(() =>
    import("./classic/ClassicLayout").then((m) => ({
      default: m.ClassicLayout,
    })),
  ),
  modern: lazy(() =>
    import("./modern/ModernLayout").then((m) => ({ default: m.ModernLayout })),
  ),
  pro: lazy(() =>
    import("./pro/ProLayout").then((m) => ({ default: m.ProLayout })),
  ),
};

export type DesignKey = keyof typeof DesignRegistry;
