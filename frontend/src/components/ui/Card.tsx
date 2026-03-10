interface Props {
  children: React.ReactNode;
  className?: string;
}

export default function Card({ children, className = "" }: Props) {
  return (
    <div
      className={[
        "rounded-xl border border-hydropi-200/80",
        "bg-white/90 backdrop-blur-sm",
        "shadow-card",
        className,
      ].join(" ")}
    >
      {children}
    </div>
  );
}
