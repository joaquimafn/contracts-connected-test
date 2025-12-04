import { useState } from 'react'
import { Header } from './components/layout/Header'
import { FileUploader } from './components/upload/FileUploader'
import { LoadingSpinner } from './components/common/LoadingSpinner'
import { ErrorMessage } from './components/common/ErrorMessage'
import { AnalysisResults } from './components/analysis/AnalysisResults'
import { contractService } from './services/contractService'
import { AnalysisResult } from './types/analysis'

type AppState = 'idle' | 'uploading' | 'analyzing' | 'completed' | 'error'

function App() {
  const [appState, setAppState] = useState<AppState>('idle')
  const [_, setAnalysisId] = useState<string | null>(null)
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  const handleFileSelect = async (file: File) => {
    setAppState('uploading')
    setError(null)
    setProgress(5)

    try {
      const uploadResponse = await contractService.uploadContract(file)
      setAnalysisId(uploadResponse.analysis_id)
      setAppState('analyzing')
      setProgress(10)

      // Poll for results
      await pollForResults(uploadResponse.analysis_id)
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Failed to upload contract'
      )
      setAppState('error')
    }
  }

  const pollForResults = async (id: string) => {
    let isComplete = false
    let attempts = 0
    const maxAttempts = 120 // 2 minutes with 1 second polling

    while (!isComplete && attempts < maxAttempts) {
      try {
        const status = await contractService.getAnalysisStatus(id)

        if (status.status === 'completed') {
          // Get full results
          const analysisResult = await contractService.getAnalysisResults(id)
          setResult(analysisResult)
          setAppState('completed')
          setProgress(100)
          isComplete = true
        } else if (status.status === 'failed') {
          setError(status.error_message || 'Analysis failed')
          setAppState('error')
          isComplete = true
        } else {
          // Update progress
          setProgress(10 + (status.progress_percentage || 0) * 0.9)
          // Wait before next poll
          await new Promise(resolve => setTimeout(resolve, 1000))
          attempts++
        }
      } catch (err: any) {
        if (err.response?.status === 202) {
          // Still processing
          setProgress(10 + 40)
          await new Promise(resolve => setTimeout(resolve, 1000))
          attempts++
        } else {
          setError(err.message || 'Failed to get analysis results')
          setAppState('error')
          isComplete = true
        }
      }
    }

    if (!isComplete) {
      setError('Analysis timeout - please try again')
      setAppState('error')
    }
  }

  const handleReset = () => {
    setAppState('idle')
    setAnalysisId(null)
    setResult(null)
    setError(null)
    setProgress(0)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {appState === 'idle' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Upload Your Contract
              </h2>
              <p className="text-gray-600 mb-8">
                Upload a PDF or TXT file containing the contract you want to analyze.
                Our AI-powered system will identify potential risks and provide recommendations.
              </p>
              <FileUploader
                onFileSelect={handleFileSelect}
                isLoading={appState !== 'idle'}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl mb-2">🔍</div>
                <h3 className="font-bold text-gray-900 mb-2">
                  Risk Detection
                </h3>
                <p className="text-sm text-gray-600">
                  Identifies 6 key risk categories using advanced AI analysis
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl mb-2">📊</div>
                <h3 className="font-bold text-gray-900 mb-2">
                  Severity Scoring
                </h3>
                <p className="text-sm text-gray-600">
                  Calculates risk severity on a 0-100 scale with detailed breakdown
                </p>
              </div>
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl mb-2">💡</div>
                <h3 className="font-bold text-gray-900 mb-2">
                  Remediation
                </h3>
                <p className="text-sm text-gray-600">
                  Provides actionable suggestions to address each identified risk
                </p>
              </div>
            </div>
          </div>
        )}

        {appState === 'uploading' && (
          <div className="bg-white rounded-lg shadow p-8">
            <LoadingSpinner
              message="Uploading your contract..."
              progress={Math.min(progress, 10)}
            />
          </div>
        )}

        {appState === 'analyzing' && (
          <div className="bg-white rounded-lg shadow p-8">
            <LoadingSpinner
              message="Analyzing contract for risks..."
              progress={Math.min(progress, 99)}
            />
          </div>
        )}

        {appState === 'completed' && result && (
          <div className="bg-white rounded-lg shadow p-8">
            <button
              onClick={handleReset}
              className="mb-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              ← Upload Another Contract
            </button>
            <AnalysisResults result={result} />
          </div>
        )}

        {appState === 'error' && (
          <div className="bg-white rounded-lg shadow p-8">
            <ErrorMessage
              message={error || 'An error occurred'}
              onDismiss={handleReset}
            />
            <button
              onClick={handleReset}
              className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}
      </main>

      <footer className="bg-gray-100 border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-600 text-sm">
            Contract Risk Analysis Agent v1.0 | Powered by AI
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
