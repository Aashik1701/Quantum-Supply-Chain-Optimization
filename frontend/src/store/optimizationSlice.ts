import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import apiService from '../services/api'

interface OptimizationState {
  isRunning: boolean
  progress: number
  results: any | null
  parameters: Record<string, any>
  selectedMethod: string
  error: string | null
  jobId: string | null
}

const initialState: OptimizationState = {
  isRunning: false,
  progress: 0,
  results: null,
  parameters: {},
  selectedMethod: 'hybrid',
  error: null,
  jobId: null,
}

// Async thunk for running optimization
export const runOptimization = createAsyncThunk(
  'optimization/runOptimization',
  async (payload: { method: string; parameters?: any; warehouses?: any[]; customers?: any[]; routes?: any[] }, { rejectWithValue }) => {
    try {
      const result = await apiService.runOptimization({
        method: payload.method,
        parameters: payload.parameters,
        data: {
          warehouses: payload.warehouses,
          customers: payload.customers,
          routes: payload.routes,
        }
      })
      return result
    } catch (error: any) {
      return rejectWithValue(error.message || 'Optimization failed')
    }
  }
)

const optimizationSlice = createSlice({
  name: 'optimization',
  initialState,
  reducers: {
    stopOptimization: (state) => {
      state.isRunning = false
    },
    setProgress: (state, action: PayloadAction<number>) => {
      state.progress = action.payload
    },
    setResults: (state, action: PayloadAction<any>) => {
      state.results = action.payload
      state.isRunning = false
      state.progress = 100
    },
    updateParameters: (state, action: PayloadAction<Record<string, any>>) => {
      state.parameters = { ...state.parameters, ...action.payload }
    },
    setMethod: (state, action: PayloadAction<string>) => {
      state.selectedMethod = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
    clearResults: (state) => {
      state.results = null
      state.jobId = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(runOptimization.pending, (state) => {
        state.isRunning = true
        state.progress = 0
        state.error = null
        state.results = null
      })
      .addCase(runOptimization.fulfilled, (state, action) => {
        state.isRunning = false
        state.progress = 100
        state.results = action.payload
        state.error = null
      })
      .addCase(runOptimization.rejected, (state, action) => {
        state.isRunning = false
        state.progress = 0
        state.error = action.payload as string || 'Optimization failed'
      })
  },
})

export const { 
  stopOptimization, 
  setProgress, 
  setResults, 
  updateParameters, 
  setMethod,
  setError,
  clearResults,
} = optimizationSlice.actions

export default optimizationSlice.reducer
