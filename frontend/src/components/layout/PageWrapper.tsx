interface Props {
  title: string;
  children: React.ReactNode;
}

export default function PageWrapper({ title, children }: Props) {
  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <h1 className="text-2xl text-hydropi-900 mb-6">{title}</h1>
      {children}
    </div>
  );
}
