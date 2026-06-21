import React, { useEffect, useState } from "react";
import { Settings } from "lucide-react";
import { DesignProps } from "../types";
import { PageName, Wallpaper } from "./types";
import AccountsPage from "./pages/AccountsPage";
import GamesPage from "./pages/GamesPage";
import SettingsPage from "./pages/SettingsPage";
import AccountView from "./components/AccountView";
import GameView from "./components/GameView";
import AddAccountModal from "../../components/AddAccountModal";
import "./modern.css";
import { useAccountModal } from "../../hooks/useAccountModal";

// Assets for logo
import LogoIcon from "@assets/switchmaster/switchmaster-icon.svg"; // Use V2 logo as fallback

export const ModernLayout: React.FC<DesignProps> = ({
  accounts,
  config,
  actions,
  systemActions,
  openSettingsSignal,
}) => {
  const [activePage, setActivePage] = useState<PageName>("Accounts");
  const [displayPage, setDisplayPage] = useState<PageName>("Accounts");
  const [isTransitioning, setIsTransitioning] = useState<boolean>(false);
  const [selectedWallpaper, setSelectedWallpaper] = useState<Wallpaper | null>(
    null,
  );
  const [isWallpaperClosing, setIsWallpaperClosing] = useState<boolean>(false);

  // Ouverture des réglages déclenchée de l'extérieur (command palette, etc.)
  useEffect(() => {
    if (!openSettingsSignal) return;
    setSelectedWallpaper(null);
    setActivePage("Settings");
    setDisplayPage("Settings");
  }, [openSettingsSignal]);

  const handlePageChange = (newPage: PageName) => {
    if (newPage !== activePage) {
      setIsTransitioning(true);
      setTimeout(() => {
        setActivePage(newPage);
        setDisplayPage(newPage);
        setTimeout(() => {
          setIsTransitioning(false);
        }, 30);
      }, 200);
    }
  };

  const handleWallpaperClick = (wallpaper: Wallpaper) => {
    setSelectedWallpaper(wallpaper);
    setIsWallpaperClosing(false);
  };

  const handleCloseWallpaper = () => {
    setIsWallpaperClosing(true);
    setTimeout(() => {
      setSelectedWallpaper(null);
      setIsWallpaperClosing(false);
    }, 250);
  };

  const modal = useAccountModal(actions);

  const handleEdit = (id: string) => {
    const acc = accounts.find((a) => a.id === id);
    if (acc) {
      modal.openEdit(acc);
      // Close wallpaper view if open
      handleCloseWallpaper();
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Are you sure you want to delete this account?")) {
      await actions.deleteAccount(id);
      handleCloseWallpaper();
    }
  };

  const handleLogin = async (id: string) => {
    const acc = accounts.find((a) => a.id === id);
    if (acc) {
      await actions.login(acc, true);
    }
  };

  const favIds = accounts.filter((a) => a.isFavorite).map((a) => a.id);

  return (
    <div className="modern-layout">
      {/* NAVBAR */}
      {!selectedWallpaper && (
        <>
          <header className="top-nav">
            <nav className="nav-pill">
              <div className="nav-logo" style={{ cursor: "pointer" }}>
                <img src={LogoIcon} alt="Logo" />
              </div>
              <button
                className={activePage === "Accounts" ? "active" : ""}
                onClick={() => handlePageChange("Accounts")}
              >
                Accounts
              </button>
              <button
                className={activePage === "Games" ? "active" : ""}
                onClick={() => handlePageChange("Games")}
              >
                Games
              </button>
            </nav>
            <button
              className={`settings-nav-btn ${activePage === "Settings" ? "active" : ""}`}
              onClick={() => handlePageChange("Settings")}
              title="Settings"
            >
              <Settings size={18} />
            </button>
          </header>
        </>
      )}

      {/* MAIN */}
      {!selectedWallpaper && (
        <div
          className={`page-wrapper ${isTransitioning ? "transitioning" : ""}`}
        >
          {displayPage === "Accounts" && (
            <AccountsPage
              accounts={accounts}
              favorites={favIds}
              onToggleFavorite={actions.toggleFavorite}
              onWallpaperClick={handleWallpaperClick}
              onReorder={actions.reorderAccounts}
              onAddAccount={modal.openAdd}
            />
          )}
          {displayPage === "Games" && (
            <GamesPage onWallpaperClick={handleWallpaperClick} />
          )}
          {displayPage === "Settings" && (
            <SettingsPage
              config={config}
              onUpdateConfig={systemActions.updateConfig}
              onCheckUpdates={systemActions.checkUpdates}
              onOpenSecurity={() => systemActions.openSecurityModal("set")}
              onSelectRiotPath={systemActions.selectRiotPath}
              onOpenGPU={() => systemActions.openGpuModal(true)}
            />
          )}
        </div>
      )}

      {/* VIEW */}
      {selectedWallpaper &&
        (activePage === "Games" ? (
          <GameView
            wallpaper={selectedWallpaper}
            onClose={handleCloseWallpaper}
            isClosing={isWallpaperClosing}
            onChangePath={systemActions.selectRiotPath}
            riotPath={config.riotPath}
          />
        ) : (
          <AccountView
            wallpaper={selectedWallpaper}
            onClose={handleCloseWallpaper}
            onLogin={handleLogin}
            isClosing={isWallpaperClosing}
            onToggleFavorite={(id) => {
              const acc = accounts.find((a) => a.id === id);
              if (acc) actions.toggleFavorite(acc);
            }}
            isFavorite={favIds.includes(selectedWallpaper.id)}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        ))}

      <AddAccountModal
        isOpen={modal.isOpen}
        onClose={modal.close}
        onAdd={modal.submit}
        editingAccount={modal.editing}
      />
    </div>
  );
};
