import axios from 'axios'
import apiClient from './api'
import { UploadResponse, AnalysisStatus } from '../types/contract'
import { AnalysisResult } from '../types/analysis'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const contractService = {
  async uploadContract(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(
      `${API_URL}/api/v1/contracts/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async getAnalysisStatus(analysisId: string): Promise<AnalysisStatus> {
    const response = await apiClient.get(
      `/api/v1/contracts/${analysisId}/status`
    )
    return response.data
  },

  async getAnalysisResults(analysisId: string): Promise<AnalysisResult> {
    const response = await apiClient.get(
      `/api/v1/contracts/${analysisId}/results`
    )
    return response.data
  },

  async checkHealth() {
    const response = await apiClient.get('/api/v1/health')
    return response.data
  },
}
