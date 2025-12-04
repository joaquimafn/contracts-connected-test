import { Risk, ContractMetadata } from './risk'

export interface AnalysisResult {
  analysis_id: string
  status: string
  contract_metadata: ContractMetadata
  risks: Risk[]
  overall_risk_score: number
  summary: string
  analyzed_at: string
}
