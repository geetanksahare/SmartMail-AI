import type {
  LucideIcon,
} from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  helper?: string;
  icon: LucideIcon;
}

export function StatCard({
  label,
  value,
  helper,
  icon: Icon,
}: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-card-top">
        <div className="stat-icon">
          <Icon size={18} />
        </div>

        <span>{label}</span>
      </div>

      <strong>{value}</strong>

      {helper && (
        <small>{helper}</small>
      )}
    </div>
  );
}