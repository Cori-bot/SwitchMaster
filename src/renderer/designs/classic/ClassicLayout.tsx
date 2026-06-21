import React, { useState, useEffect } from "react";
import Dashboard from "../../components/Dashboard";
import Sidebar from "../../components/Sidebar";
import TopBar from "../../components/TopBar";
import Settings from "../../components/Settings";
import AddAccountModal from "../../components/AddAccountModal";
import { DesignProps } from "../types";
import { AnimatePresence, m } from "motion/react";
import { useAccountModal } from "../../hooks/useAccountModal";
import NotificationItem from "../../components/NotificationItem";
import { useNotifications } from "../../hooks/useNotifications";

export const ClassicLayout: React.FC<DesignProps> = ({
  accounts,
  activeAccountId,
  config,
  status,
  actions,
  systemActions,
  onSwitchSession,
  openSettingsSignal,
}) => {
  const [view, setView] = useState("dashboard");

  useEffect(() => {
    if (openSettingsSignal) setView("settings");
  }, [openSettingsSignal]);
  const [filter, setFilter] = useState<
    "all" | "favorite" | "valorant" | "league"
  >("all");
  const modal = useAccountModal(actions);

  const { notifications, removeNotification } = useNotifications();

  return (
    <div className="flex h-screen bg-gray-900 text-white overflow-hidden font-sans select-none relative">
      <Sidebar activeView={view} onViewChange={setView} />

      <div className="flex-1 flex flex-col min-w-0 bg-[#0a0a0a]">
        <TopBar
          status={status}
          currentFilter={filter}
          onFilterChange={setFilter}
          showFilters={view === "dashboard"}
        />

        <main className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-transparent">
          {view === "dashboard" && (
            <Dashboard
              accounts={accounts}
              filter={filter}
              activeAccountId={activeAccountId || undefined}
              onSwitch={onSwitchSession}
              onDelete={actions.deleteAccount}
              onEdit={modal.openEdit}
              onToggleFavorite={actions.toggleFavorite}
              onReorder={actions.reorderAccounts}
              onAddAccount={modal.openAdd}
            />
          )}

          {view === "settings" && (
            <Settings
              config={config}
              onUpdate={systemActions.updateConfig}
              onSelectRiotPath={systemActions.selectRiotPath}
              onOpenPinModal={() => systemActions.openSecurityModal("set")}
              onDisablePin={() => systemActions.openSecurityModal("disable")}
              onCheckUpdates={systemActions.checkUpdates}
              onOpenGPUModal={systemActions.openGpuModal}
            />
          )}
        </main>
      </div>

      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        <AnimatePresence mode="popLayout">
          {notifications.map((notification) => (
            <m.div
              key={notification.id}
              layout
              initial={{ opacity: 0, y: 20, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.9 }}
            >
              <NotificationItem
                notification={notification}
                onRemove={removeNotification}
              />
            </m.div>
          ))}
        </AnimatePresence>
      </div>

      <AddAccountModal
        isOpen={modal.isOpen}
        onClose={modal.close}
        onAdd={modal.submit}
        editingAccount={modal.editing}
      />
    </div>
  );
};
