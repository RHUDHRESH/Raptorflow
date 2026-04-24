interface PageErrorProps {
  message?: string;
  onRetry?: () => void;
}

export function PageError({ message = "Something went wrong.", onRetry }: PageErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <p className="text-slate-400 text-sm mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs text-violet-400 hover:text-violet-300 underline underline-offset-2"
        >
          Try again
        </button>
      )}
    </div>
  );
}
