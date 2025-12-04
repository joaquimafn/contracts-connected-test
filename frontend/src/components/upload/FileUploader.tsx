import { useDropzone } from 'react-dropzone'
import { Upload } from 'lucide-react'

interface FileUploaderProps {
  onFileSelect: (file: File) => void
  isLoading: boolean
}

export function FileUploader({ onFileSelect, isLoading }: FileUploaderProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0]
        if (file.type === 'application/pdf' || file.type === 'text/plain') {
          onFileSelect(file)
        }
      }
    },
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
    },
    disabled: isLoading,
    multiple: false,
  })

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`relative border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-blue-400'
        } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center">
          <Upload className="w-12 h-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700 mb-2">
            {isDragActive ? 'Drop your contract here' : 'Drag and drop your contract here'}
          </p>
          <p className="text-sm text-gray-500 mb-4">
            or click to select a file
          </p>
          <p className="text-xs text-gray-400">
            Accepted formats: PDF, TXT (Max 10MB)
          </p>
        </div>
      </div>
    </div>
  )
}
