import { SeverityLevel } from '../../types/risk'

interface RiskSeverityBadgeProps {
  level: SeverityLevel
  score: number
}

const severityColors = {
  LOW: 'bg-green-100 text-green-800 border-green-300',
  MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  HIGH: 'bg-orange-100 text-orange-800 border-orange-300',
  CRITICAL: 'bg-red-100 text-red-800 border-red-300',
}

const severityIcons = {
  LOW: '✓',
  MEDIUM: '⚠',
  HIGH: '⚠',
  CRITICAL: '🔴',
}

export function RiskSeverityBadge({ level, score }: RiskSeverityBadgeProps) {
  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full border ${severityColors[level]}`}>
      <span className="mr-2">{severityIcons[level]}</span>
      <span className="font-semibold">{level}</span>
      <span className="ml-2 text-sm">({score}/100)</span>
    </div>
  )
}
