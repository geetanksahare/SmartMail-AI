import {
  Inbox,
} from "lucide-react";

import type {
  ReactNode,
} from "react";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Inbox size={21} />
      </div>

      <h3>{title}</h3>

      {description && (
        <p>{description}</p>
      )}

      {action && (
        <div className="empty-action">
          {action}
        </div>
      )}
    </div>
  );
}