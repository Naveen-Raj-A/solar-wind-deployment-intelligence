export default function Sidebar({ children, className }) {
  return (
    <aside className={`w-64 bg-white border-r border-gray-200 p-6 ${className}`}>
      {children}
    </aside>
  );
}