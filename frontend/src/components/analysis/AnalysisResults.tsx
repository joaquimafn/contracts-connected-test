import { AnalysisResult } from '../../types/analysis'
import { RiskCard } from './RiskCard'

interface AnalysisResultsProps {
  result: AnalysisResult
}

export function AnalysisResults({ result }: AnalysisResultsProps) {
  const risksBySeverity = {
    CRITICAL: result.risks.filter(r => r.severity_level === 'CRITICAL'),
    HIGH: result.risks.filter(r => r.severity_level === 'HIGH'),
    MEDIUM: result.risks.filter(r => r.severity_level === 'MEDIUM'),
    LOW: result.risks.filter(r => r.severity_level === 'LOW'),
  }

  const getScoreColor = (score: number) => {
    if (score <= 25) return 'text-green-600'
    if (score <= 50) return 'text-yellow-600'
    if (score <= 75) return 'text-orange-600'
    return 'text-red-600'
  }

  const getScoreBgColor = (score: number) => {
    if (score <= 25) return 'bg-green-50'
    if (score <= 50) return 'bg-yellow-50'
    if (score <= 75) return 'bg-orange-50'
    return 'bg-red-50'
  }

  return (
    <div className="space-y-8 fade-in">
      {/* Header with file info */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">
          Analysis Report
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-500">File</p>
            <p className="font-semibold text-gray-900">
              {result.contract_metadata.filename}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Type</p>
            <p className="font-semibold text-gray-900">
              {result.contract_metadata.file_type.toUpperCase()}
            </p>
          </div>
          {result.contract_metadata.page_count > 0 && (
            <div>
              <p className="text-sm text-gray-500">Pages</p>
              <p className="font-semibold text-gray-900">
                {result.contract_metadata.page_count}
              </p>
            </div>
          )}
          <div>
            <p className="text-sm text-gray-500">Words</p>
            <p className="font-semibold text-gray-900">
              {result.contract_metadata.word_count.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Overall Risk Score */}
      <div
        className={`rounded-lg p-8 ${getScoreBgColor(result.overall_risk_score)}`}
      >
        <h3 className="text-sm font-semibold text-gray-600 mb-2">
          Overall Risk Score
        </h3>
        <div className="flex items-end gap-4">
          <div className={`text-5xl font-bold ${getScoreColor(result.overall_risk_score)}`}>
            {result.overall_risk_score}
          </div>
          <div className="text-lg font-semibold text-gray-700">/ 100</div>
        </div>
        <div className="mt-4 w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              result.overall_risk_score <= 25
                ? 'bg-green-600'
                : result.overall_risk_score <= 50
                ? 'bg-yellow-600'
                : result.overall_risk_score <= 75
                ? 'bg-orange-600'
                : 'bg-red-600'
            }`}
            style={{ width: `${result.overall_risk_score}%` }}
          ></div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="font-semibold text-blue-900 mb-2">Summary</h3>
        <p className="text-blue-800">{result.summary}</p>
      </div>

      {/* Risk Breakdown */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600 font-semibold text-2xl">
            {risksBySeverity.CRITICAL.length}
          </p>
          <p className="text-red-700 text-sm">Critical</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <p className="text-orange-600 font-semibold text-2xl">
            {risksBySeverity.HIGH.length}
          </p>
          <p className="text-orange-700 text-sm">High</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-600 font-semibold text-2xl">
            {risksBySeverity.MEDIUM.length}
          </p>
          <p className="text-yellow-700 text-sm">Medium</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-green-600 font-semibold text-2xl">
            {risksBySeverity.LOW.length}
          </p>
          <p className="text-green-700 text-sm">Low</p>
        </div>
      </div>

      {/* Risks List */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Identified Risks
        </h2>

        {result.risks.length === 0 ? (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
            <p className="text-green-800 font-medium">
              ✓ No significant risks detected in this contract
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {result.risks.map((risk) => (
              <RiskCard key={risk.risk_id} risk={risk} />
            ))}
          </div>
        )}
      </div>

      {/* Analyzed At */}
      <div className="text-center text-sm text-gray-500">
        Analyzed on {new Date(result.analyzed_at).toLocaleString()}
      </div>
    </div>
  )
}
