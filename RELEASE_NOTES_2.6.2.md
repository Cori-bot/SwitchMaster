# SwitchMaster 2.6.2

Améliorations de l'interface et micro-interactions (philosophie Emil Kowalski & Impeccable).

## ✨ Nouveautés & Améliorations UI

- **Transitions optimisées :** Remplacement des `transition-all` par des transitions ciblées (`transform`, `opacity`, `border-color`, `background-color`) évitant les recalculs de paint complets pour un rendu fluide à 60 FPS.
- **Micro-interactions tactiles :** Ajout de feedback physique `:active` précis (`active:scale-[0.98]`) sur l'ensemble des boutons d'action et des cartes de compte.
- **Animations d'entrée affinées :** Courbes spring calibrées (`stiffness: 350`, `damping: 28`) avec une échelle initiale de `0.98` évitant les effets d'apparition brusque.
- **Toasts & Notifications :** Timing et lissage revus avec une courbe `cubic-bezier(0.16, 1, 0.3, 1)` plus vive et naturelle.

## ⬇️ Installation

Téléchargez **`SwitchMaster Setup 2.6.2.exe`** ci-dessous et lancez-le.
