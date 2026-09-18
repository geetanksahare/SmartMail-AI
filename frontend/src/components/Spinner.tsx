interface SpinnerProps {
  size?: "small" | "medium" | "large";
}

export function Spinner({
  size = "medium",
}: SpinnerProps) {
  return (
    <span
      className={`spinner spinner-${size}`}
      role="status"
      aria-label="Loading"
    />
  );
}