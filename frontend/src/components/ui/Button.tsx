import { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";
type Size = "sm" | "md" | "lg";

const variantClasses: Record<Variant, string> = {
  primary:
    "bg-hydropi-700 text-white hover:bg-hydropi-600 active:bg-hydropi-800 " +
    "shadow-btn-primary focus-visible:ring-hydropi-500",
  secondary:
    "bg-white text-hydropi-800 border border-hydropi-300 " +
    "hover:bg-hydropi-50 hover:border-hydropi-400 hover:text-hydropi-900 active:bg-hydropi-100 " +
    "shadow-[0_1px_3px_rgba(3,60,115,0.10)] focus-visible:ring-hydropi-400",
  danger:
    "bg-red-600 text-white hover:bg-red-500 active:bg-red-700 " +
    "shadow-[0_1px_3px_rgba(220,38,38,0.30)] focus-visible:ring-red-400",
  ghost:
    "text-hydropi-700 hover:text-hydropi-900 hover:bg-hydropi-100/80 active:bg-hydropi-200/60 " +
    "focus-visible:ring-hydropi-400",
};

const sizeClasses: Record<Size, string> = {
  sm: "px-2.5 py-1 text-xs rounded",
  md: "px-4 py-2 text-sm rounded-lg",
  lg: "px-5 py-2.5 text-base rounded-xl",
};

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  children,
  className = "",
  ...rest
}: Props) {
  return (
    <button
      disabled={disabled || loading}
      className={[
        "font-semibold select-none",
        "transition-[background-color,opacity,transform,border-color] duration-150",
        "focus-visible:outline-none focus-visible:ring-2",
        "disabled:opacity-40 disabled:cursor-not-allowed",
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].join(" ")}
      {...rest}
    >
      {loading ? <span className="opacity-60">…</span> : children}
    </button>
  );
}
