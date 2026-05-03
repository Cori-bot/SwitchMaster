import React from "react";
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
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Account } from "../../../shared/types";

interface AccountListProps {
  accounts: Account[];
  activeAccountId: string | null;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onToggleFavorite: (account: Account) => void;
  onReorder: (ids: string[]) => void;
}

interface RowProps {
  account: Account;
  isActive: boolean;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onToggleFavorite: (account: Account) => void;
}

const Row: React.FC<RowProps> = ({
  account,
  isActive,
  isSelected,
  onSelect,
  onToggleFavorite,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: account.id,
  });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const initials = account.name?.slice(0, 2).toUpperCase() || "??";

  return (
    <div
      ref={setNodeRef}
      style={style}
      data-testid={`pro-account-${account.id}`}
      className={`pro-list__item${isActive || isSelected ? " is-active" : ""}${isDragging ? " is-dragging" : ""}`}
      onClick={() => onSelect(account.id)}
      {...attributes}
      {...listeners}
    >
      <div className="pro-avatar">
        {account.cardImage ? (
          <img
            src={
              account.cardImage.startsWith("http")
                ? account.cardImage
                : `sm-img://${account.cardImage.replace(/\\/g, "/")}`
            }
            alt=""
          />
        ) : (
          <span>{initials}</span>
        )}
      </div>
      <div style={{ minWidth: 0 }}>
        <div className="pro-list__name">{account.name}</div>
        <div className="pro-list__sub">{account.riotId || "—"}</div>
      </div>
      <div className="pro-list__meta">
        <span className="pro-tag">
          {account.gameType === "league" ? "LoL" : "VAL"}
        </span>
        <button
          className={`pro-fav${account.isFavorite ? " is-on" : ""}`}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(account);
          }}
          aria-label={account.isFavorite ? "Unfavorite" : "Favorite"}
        >
          <Star size={12} fill={account.isFavorite ? "currentColor" : "none"} />
        </button>
      </div>
    </div>
  );
};

export const AccountList: React.FC<AccountListProps> = ({
  accounts,
  activeAccountId,
  selectedId,
  onSelect,
  onToggleFavorite,
  onReorder,
}) => {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = accounts.findIndex((a) => a.id === active.id);
    const newIndex = accounts.findIndex((a) => a.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;
    const next = arrayMove(accounts, oldIndex, newIndex);
    onReorder(next.map((a) => a.id));
  };

  return (
    <aside className="pro-list" aria-label="Accounts">
      <div className="pro-list__header">
        <span>Accounts</span>
        <span>{accounts.length}</span>
      </div>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext
          items={accounts.map((a) => a.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="pro-list__items" role="list">
            {accounts.map((account) => (
              <Row
                key={account.id}
                account={account}
                isActive={account.id === activeAccountId}
                isSelected={account.id === selectedId}
                onSelect={onSelect}
                onToggleFavorite={onToggleFavorite}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </aside>
  );
};

export default AccountList;
