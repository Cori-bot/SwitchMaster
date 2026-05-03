import "@testing-library/jest-dom/vitest";
import { vi } from "vitest";
import React from "react";

// Mock global de framer-motion pour tous les tests renderer sans JSX
const motionProxy = {
  div: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("div", { ...props, ref }, children),
  ),
  button: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("button", { ...props, ref }, children),
  ),
  span: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("span", { ...props, ref }, children),
  ),
  h1: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("h1", { ...props, ref }, children),
  ),
  h2: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("h2", { ...props, ref }, children),
  ),
  h3: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("h3", { ...props, ref }, children),
  ),
  p: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("p", { ...props, ref }, children),
  ),
  nav: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("nav", { ...props, ref }, children),
  ),
  header: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("header", { ...props, ref }, children),
  ),
  section: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("section", { ...props, ref }, children),
  ),
  main: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("main", { ...props, ref }, children),
  ),
  aside: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("aside", { ...props, ref }, children),
  ),
  img: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("img", { ...props, ref }, children),
  ),
  ul: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("ul", { ...props, ref }, children),
  ),
  li: React.forwardRef(({ children, ...props }: any, ref) =>
    React.createElement("li", { ...props, ref }, children),
  ),
};
vi.mock("framer-motion", () => ({
  motion: motionProxy,
  m: motionProxy,
  AnimatePresence: ({ children }: any) => children,
  LayoutGroup: ({ children }: any) => children,
  LazyMotion: ({ children }: any) => children,
  domAnimation: {},
  domMax: {},
}));

// Mock global window.ipc
(window as any).ipc = {
  invoke: vi.fn().mockResolvedValue({}),
  on: vi.fn(() => vi.fn()),
  send: vi.fn(),
};
