import { useState } from 'react'
import { Risk } from '../../types/risk'
import { RiskSeverityBadge } from './RiskSeverityBadge'
import { ChevronDown, ChevronUp } from 'lucide-react'

interface RiskCardProps {
  risk: Risk
}

export function RiskCard({ risk }: RiskCardProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow bg-white">
      <div
        className="cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {risk.title}
            </h3>
            <RiskSeverityBadge
              level={risk.severity_level}
              score={risk.severity_score}
            />
          </div>
          {isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
        <p className="text-sm text-gray-600">{risk.description}</p>
      </div>

      {isExpanded && (
        <div className="mt-6 pt-6 border-t border-gray-200 space-y-4 fade-in">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">
              Why This Matters
            </h4>
            <p className="text-sm text-gray-700">{risk.explanation}</p>
          </div>

          {risk.evidence && risk.evidence.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Evidence</h4>
              <ul className="space-y-2">
                {risk.evidence.map((evidence, index) => (
                  <li
                    key={index}
                    className="text-sm bg-gray-50 p-3 rounded border border-gray-200"
                  >
                    <blockquote className="italic text-gray-700">
                      "{evidence}"
                    </blockquote>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div>
            <h4 className="font-semibold text-gray-900 mb-2">
              Remediation Suggestion
            </h4>
            <div className="bg-blue-50 border border-blue-200 rounded p-4">
              <p className="text-sm text-blue-900 mb-3">
                {risk.remediation.suggestion}
              </p>
              <div className="flex gap-4 text-xs">
                <span className="inline-flex items-center px-2 py-1 rounded bg-blue-100 text-blue-800">
                  Priority: {risk.remediation.priority}
                </span>
                <span className="inline-flex items-center px-2 py-1 rounded bg-blue-100 text-blue-800">
                  Effort: {risk.remediation.effort}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
