import { useEffect, useRef, useState } from "react";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "../utils/cn";

export interface DropdownOption<T extends string> {
  value: T;
  label: string;
}

interface DropdownProps<T extends string> {
  value: T;
  options: DropdownOption<T>[];
  onChange: (value: T) => void;
  className?: string;
  title?: string;
  align?: "left" | "right";
}

/**
 * Sélecteur déroulant aux couleurs de l'app (remplace `<select>` natif, dont la
 * liste déroulante est rendue par l'OS et ne suit pas le thème). Clic-extérieur
 * et Échap ferment le menu.
 */
export function Dropdown<T extends string>({
  value,
  options,
  onChange,
  className,
  title,
  align = "right",
}: DropdownProps<T>) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const current = options.find((o) => o.value === value);

  useEffect(() => {
    if (!open) return;
    const onPointerDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("mousedown", onPointerDown);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onPointerDown);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        title={title}
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "flex items-center justify-between gap-2 bg-[#1a1a1a] border border-white/10 rounded-xl px-3 py-2.5 text-sm text-gray-200 hover:border-white/20 focus:outline-none focus:border-blue-500/50 transition-colors",
          className,
        )}
      >
        <span className="truncate">{current?.label ?? ""}</span>
        <ChevronDown
          size={16}
          className={cn(
            "text-gray-400 transition-transform duration-200 shrink-0",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <div
          role="listbox"
          className={cn(
            "absolute top-full mt-2 min-w-[12rem] bg-[#242424] border border-white/10 rounded-xl shadow-2xl overflow-hidden z-30 py-1",
            align === "right" ? "right-0" : "left-0",
          )}
        >
          {options.map((o) => (
            <button
              key={o.value}
              type="button"
              role="option"
              aria-selected={o.value === value}
              onClick={() => {
                onChange(o.value);
                setOpen(false);
              }}
              className={cn(
                "w-full flex items-center justify-between gap-3 px-4 py-2.5 text-sm text-left transition-colors",
                o.value === value
                  ? "text-white bg-white/5"
                  : "text-gray-300 hover:bg-white/5",
              )}
            >
              {o.label}
              {o.value === value && (
                <Check size={15} className="text-blue-400 shrink-0" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dropdown;
