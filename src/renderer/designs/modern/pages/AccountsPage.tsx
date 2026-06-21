import React, { useState, useMemo } from "react";
import { Star } from "lucide-react";
import {
  DndContext,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  closestCenter,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  rectSortingStrategy,
  sortableKeyboardCoordinates,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Wallpaper } from "../types";
import { Account } from "../../../../shared/types";

interface AccountsPageProps {
  accounts: Account[];
  onWallpaperClick?: (wallpaper: Wallpaper) => void;
  favorites: string[]; // IDs
  onToggleFavorite: (account: Account) => Promise<void>;
  onAddAccount: () => void;
  onReorder?: (ids: string[]) => void;
}

const getGameIcon = (game?: string): string | null => {
  if (!game) return null;
  try {
    if (game === "valorant") {
      return new URL(
        "../../../../assets/games/valorant-icon.svg",
        import.meta.url,
      ).href;
    } else if (game === "league-of-legends" || game === "league") {
      return new URL(
        "../../../../assets/games/league-of-legends-icon.svg",
        import.meta.url,
      ).href;
    }
  } catch (e) {
    console.error("Icon not found", e);
  }
  return null;
};

const formatRankForAsset = (game: string, rank: string): string | null => {
  if (!rank) return null;
  const lowerRank = rank.toLowerCase();
  if (game === "league-of-legends" || game === "league") {
    return lowerRank.split(" ")[0];
  } else if (game === "valorant") {
    return lowerRank.replace(" ", "_");
  }
  return lowerRank;
};

const getRankIcon = (game?: string, rank?: string): string | null => {
  if (!game || !rank) return null;
  const gameFolder = game === "league" ? "league-of-legends" : game;
  const rankFile = formatRankForAsset(gameFolder, rank);
  if (!rankFile) return null;
  try {
    return new URL(
      `../../../../assets/games/${gameFolder}/${rankFile}.svg`,
      import.meta.url,
    ).href;
  } catch (e) {
    return null;
  }
};

// Filtres : favoris, par jeu (gameType) et par launcher (valeurs réelles riot|steam|epic).
const GAME_FILTERS: Record<string, string> = {
  Valorant: "valorant",
  League: "league",
};
const LAUNCHER_FILTERS: Record<string, string> = {
  Riot: "riot",
  Steam: "steam",
  Epic: "epic",
};
const FILTER_BUTTONS = [
  "favorites",
  "Valorant",
  "League",
  "Riot",
  "Steam",
  "Epic",
];

interface CardProps {
  wallpaper: Wallpaper;
  isFavorite: boolean;
  draggable: boolean;
  onClick: () => void;
  onToggleFavorite: (e: React.MouseEvent) => void;
}

const Card: React.FC<CardProps> = ({
  wallpaper,
  isFavorite,
  draggable,
  onClick,
  onToggleFavorite,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: wallpaper.id, disabled: !draggable });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.6 : undefined,
  };

  const gameIcon = getGameIcon(wallpaper.game);
  const rankIcon = getRankIcon(wallpaper.game, wallpaper.rank);

  return (
    <article
      ref={setNodeRef}
      style={style}
      className="card"
      onClick={onClick}
      data-testid={`modern-account-${wallpaper.id}`}
      {...attributes}
      {...listeners}
    >
      <img src={wallpaper.image} alt={wallpaper.title} />
      <div className="card-icons-container">
        {gameIcon && (
          <div className="card-game-icon">
            <img src={gameIcon} alt={wallpaper.game} />
          </div>
        )}
        {rankIcon && (
          <div className="card-rank-icon">
            <img src={rankIcon} alt={wallpaper.rank} />
          </div>
        )}
      </div>
      <button
        className={`favorite-icon ${isFavorite ? "active" : ""}`}
        onClick={onToggleFavorite}
        title={isFavorite ? "Retirer des favoris" : "Ajouter aux favoris"}
      >
        <Star size={18} fill={isFavorite ? "currentColor" : "none"} />
      </button>
      <div className="card-info">
        <h3>{wallpaper.title}</h3>
        <span>{wallpaper.category}</span>
        <span style={{ display: "block", opacity: 0.7, fontSize: "10px" }}>
          {wallpaper.details}
        </span>
      </div>
    </article>
  );
};

function AccountsPage({
  accounts,
  onWallpaperClick,
  favorites,
  onToggleFavorite,
  onAddAccount,
  onReorder,
}: AccountsPageProps) {
  // Adapter : Account[] -> Wallpaper[]
  const wallpapers: Wallpaper[] = useMemo(() => {
    return accounts.map((acc) => {
      const isLeague = acc.gameType === "league";
      return {
        id: acc.id,
        image:
          acc.cardImage ||
          (isLeague
            ? getGameIcon("league") || ""
            : getGameIcon("valorant") || ""),
        title: acc.name || "Unknown",
        category:
          acc.riotId ||
          (acc.username && acc.username.length < 30
            ? acc.username
            : "No Riot ID"),
        details: acc.stats?.rank || "Unranked",
        game: acc.gameType,
        rank: acc.stats?.rank,
        account: acc,
      };
    });
  }, [accounts]);

  const [activeFilter, setActiveFilter] = useState<string | null>(null);

  const handleToggleFavorite = (e: React.MouseEvent, account: Account) => {
    e.stopPropagation();
    onToggleFavorite(account);
  };

  const handleFilterClick = (filterName: string) => {
    setActiveFilter((prev) => (prev === filterName ? null : filterName));
  };

  const filteredWallpapers = useMemo(() => {
    if (!activeFilter) return wallpapers;
    if (activeFilter === "favorites")
      return wallpapers.filter((w) => favorites.includes(w.id));
    if (GAME_FILTERS[activeFilter])
      return wallpapers.filter((w) => w.game === GAME_FILTERS[activeFilter]);
    if (LAUNCHER_FILTERS[activeFilter])
      return wallpapers.filter(
        (w) =>
          (w.account?.launcherType ?? "riot") ===
          LAUNCHER_FILTERS[activeFilter],
      );
    return wallpapers;
  }, [wallpapers, activeFilter, favorites]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  // Le réordonnancement n'est persisté que sur la liste complète (sans filtre).
  const canReorder = !!onReorder && activeFilter === null;

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id || !canReorder) return;
    const oldIndex = filteredWallpapers.findIndex((w) => w.id === active.id);
    const newIndex = filteredWallpapers.findIndex((w) => w.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    const next = arrayMove(filteredWallpapers, oldIndex, newIndex);
    onReorder?.(next.map((w) => w.id));
  };

  return (
    <main>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "6px",
        }}
      >
        <h1>Accounts</h1>
        <button
          className="icon-btn"
          onClick={onAddAccount}
          style={{
            width: "32px",
            height: "32px",
            fontSize: "20px",
            background: "rgba(255,255,255,0.1)",
          }}
          title="Add Account"
        >
          +
        </button>
      </div>
      <p className="subtitle">Add, remove and manage your accounts.</p>

      {/* FILTERS */}
      <div className="filters">
        {FILTER_BUTTONS.map((f) =>
          f === "favorites" ? (
            <div
              key={f}
              className={`filter filter-favorite ${activeFilter === "favorites" ? "active" : ""}`}
              onClick={() => handleFilterClick("favorites")}
              title="Favoris"
            >
              <Star
                size={14}
                fill={activeFilter === "favorites" ? "currentColor" : "none"}
              />
            </div>
          ) : (
            <div
              key={f}
              className={`filter ${activeFilter === f ? "active" : ""}`}
              onClick={() => handleFilterClick(f)}
            >
              {f}
            </div>
          ),
        )}
      </div>

      {/* GRID */}
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={filteredWallpapers.map((w) => w.id)}
          strategy={rectSortingStrategy}
        >
          <section className="grid">
            {filteredWallpapers.map((wallpaper) => (
              <Card
                key={wallpaper.id}
                wallpaper={wallpaper}
                isFavorite={favorites.includes(wallpaper.id)}
                draggable={canReorder}
                onClick={() => onWallpaperClick?.(wallpaper)}
                onToggleFavorite={(e) =>
                  handleToggleFavorite(e, wallpaper.account!)
                }
              />
            ))}
          </section>
        </SortableContext>
      </DndContext>
    </main>
  );
}

export default AccountsPage;
