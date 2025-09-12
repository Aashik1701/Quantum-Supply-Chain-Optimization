import axios, { AxiosInstance, AxiosError } from 'axios'

const baseURL = import.meta?.env?.VITE_API_BASE_URL || '/api/v1'

const api: AxiosInstance = axios.create({
	baseURL,
	withCredentials: true,
})

// Simple interceptor placeholders (extend with auth token handling later)
api.interceptors.response.use(
	(resp) => {
		const data = resp.data
		if (data && typeof data === 'object' && 'success' in data) {
			if (data.success) {
				// Unwrap standardized envelope
				return data.data !== undefined ? data.data : data
			}
			return Promise.reject({
				code: data.error?.code || 'UNKNOWN_ERROR',
				message: data.error?.message || 'Request failed',
				details: data.error?.details,
				meta: data.meta,
				status: resp.status,
			})
		}
		return data
	},
	(error: AxiosError) => {
		const status = error.response?.status
		const payload: any = error.response?.data
		if (payload && typeof payload === 'object') {
			return Promise.reject({
				code: payload.error?.code || 'HTTP_ERROR',
				message: payload.error?.message || error.message,
				details: payload.error?.details,
				meta: payload.meta,
				status,
			})
		}
		return Promise.reject({
			code: 'NETWORK_ERROR',
			message: error.message,
			status,
		})
	}
)

// Wrapper methods expected by slices/pages
const apiService = {
	// Health check
	async healthCheck() {
		const { data } = await api.get('/health')
		return data
	},

	// Dashboard aggregated data
	async getDashboardData() {
		return api.get('/dashboard')
	},

	// Entity lists
	async getWarehouses() { return api.get('/data/warehouses') },
	async getCustomers() { return api.get('/data/customers') },
	async getRoutes() { return api.get('/data/routes') },

	// Upload (expects FormData)
	async uploadData(file: File, dataType: string) {
		const form = new FormData()
		form.append('file', file)
		form.append('type', dataType)
		return api.post(`/data/upload`, form, { headers: { 'Content-Type': 'multipart/form-data' } })
	},

	// Validate dataset(s)
	async validateData(payload: { warehouses?: any[]; customers?: any[]; routes?: any[] }) {
		return api.post('/data/validate', payload)
	},

	// Delete dataset type
	async deleteData(dataType: string) {
		return api.delete(`/data/${dataType}`)
	},

	// Optimization endpoints
	async runOptimization(payload: { method: string; parameters?: any; data?: any }) {
		return api.post('/optimize', payload)
	},

	async runVRPOptimization(payload: any) {
		return api.post('/optimize/vrp', payload)
	},

	async runHybridVRPOptimization(payload: any) {
		return api.post('/optimize/hybrid-vrp', payload)
	},

	async getOptimizationStatus(jobId: string) {
		return api.get(`/optimize/status/${jobId}`)
	},
}

export default apiService
