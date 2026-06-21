import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import Settings from "../components/Settings";
import { Config } from "../../shared/types";

const config: Config = {
  riotPath: "",
  autoStart: false,
  startMinimized: false,
  minimizeToTray: false,
  showQuitModal: true,
  hasSeenOnboarding: true,
  activeDesignModule: "classic",
};

describe("Settings — sélecteur de design", () => {
  it("propose Classic, Modern et Pro et émet le bon module au clic", () => {
    const onUpdate = vi.fn();
    render(
      <Settings
        config={config}
        onUpdate={onUpdate}
        onSelectRiotPath={vi.fn()}
        onOpenPinModal={vi.fn()}
        onDisablePin={vi.fn()}
        onCheckUpdates={vi.fn()}
        onOpenGPUModal={vi.fn()}
      />,
    );

    expect(screen.getByText("Classic")).toBeInTheDocument();
    expect(screen.getByText("Modern")).toBeInTheDocument();
    expect(screen.getByText("Pro")).toBeInTheDocument();

    fireEvent.click(screen.getByText("Pro"));
    expect(onUpdate).toHaveBeenCalledWith({ activeDesignModule: "pro" });
  });
});
