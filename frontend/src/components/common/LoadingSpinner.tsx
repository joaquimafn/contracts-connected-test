interface LoadingSpinnerProps {
  message?: string
  progress?: number
}

export function LoadingSpinner({ message, progress }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative w-16 h-16 mb-4">
        <div className="absolute inset-0 rounded-full border-4 border-gray-200"></div>
        <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
      </div>
      {message && (
        <p className="text-lg text-gray-700 font-medium">{message}</p>
      )}
      {progress !== undefined && (
        <div className="mt-4 w-48">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-500 mt-2 text-center">{progress}%</p>
        </div>
      )}
    </div>
  )
}
