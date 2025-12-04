export interface UploadResponse {
  analysis_id: string
  status: string
  created_at: string
  message: string
}

export interface AnalysisStatus {
  analysis_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress_percentage: number
  created_at?: string
  completed_at?: string
  error_message?: string
}
