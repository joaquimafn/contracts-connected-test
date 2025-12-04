export type RiskCategory =
  | 'missing_insurance'
  | 'uncapped_liability'
  | 'vague_payment_terms'
  | 'broad_indemnification'
  | 'missing_termination'
  | 'ambiguous_scope'

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export interface Remediation {
  suggestion: string
  priority: string
  effort: string
}

export interface Risk {
  risk_id: string
  category: RiskCategory
  title: string
  description: string
  severity_score: number
  severity_level: SeverityLevel
  affected_clause: string
  explanation: string
  evidence: string[]
  remediation: Remediation
}

export interface ContractMetadata {
  filename: string
  file_type: string
  page_count: number
  word_count: number
}
