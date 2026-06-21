import { apiClient } from './client';

export const vendorsApi = {
  getVendors: (params) => apiClient.get('/vendors', { params }),
  getVendor: (id) => apiClient.get(`/vendors/${id}`),
  createVendor: (data) => apiClient.post('/vendors', data),
  updateVendor: (id, data) => apiClient.put(`/vendors/${id}`, data),
};

export const riskApi = {
  calculateRisk: (vendorId) => apiClient.post('/risk/calculate', { vendor_id: vendorId }),
  getVendorRisk: (vendorId) => apiClient.get(`/risk/vendors/${vendorId}`),
  getRiskHistory: (vendorId) => apiClient.get(`/risk/vendors/${vendorId}/history`),
};

export const contractsApi = {
  uploadContract: (formData) => apiClient.post('/contracts/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getContractAnalysis: (id) => apiClient.get(`/contracts/${id}/analysis`),
  getContractClauses: (id) => apiClient.get(`/contracts/${id}/clauses`),
};

export const complianceApi = {
  getCertifications: () => apiClient.get('/certifications'),
  getExpiringCertifications: (days = 60) => apiClient.get(`/certifications/expiring?days=${days}`),
  createCertification: (data) => apiClient.post('/certifications', data),
};

export const copilotApi = {
  query: (question) => apiClient.post('/copilot/query', { question }),
  generateReport: (reportType) => apiClient.post('/copilot/report', { report_type: reportType }),
};
