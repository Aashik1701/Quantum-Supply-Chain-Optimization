import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import apiService from '@/services/api'

// --- Types -----------------------------------------------------------------
interface ValidationResult {
  valid: boolean
  errors: any[]
  warnings: any[]
}

interface DataState {
  warehouses: any[]
  customers: any[]
  routes: any[]
  dashboardData: any | null
  validation: ValidationResult | null
  loading: boolean
  error: string | null
}

// --- Initial State ---------------------------------------------------------
const initialState: DataState = {
  warehouses: [],
  customers: [],
  routes: [],
  dashboardData: null,
  validation: null,
  loading: false,
  error: null,
}

// --- Thunks ----------------------------------------------------------------
export const fetchDashboardData = createAsyncThunk('data/fetchDashboardData', async (_, { rejectWithValue }) => {
  try {
    return await apiService.getDashboardData()
  } catch (e: any) {
    return rejectWithValue('Failed to fetch dashboard data')
  }
})

export const fetchData = createAsyncThunk('data/fetchData', async (_, { rejectWithValue }) => {
  try {
    const [warehouses, customers, routes] = await Promise.all([
      apiService.getWarehouses(),
      apiService.getCustomers(),
      apiService.getRoutes(),
    ])
    return { warehouses, customers, routes }
  } catch (e: any) {
    return rejectWithValue('Failed to fetch data sets')
  }
})

export const uploadData = createAsyncThunk(
  'data/uploadData',
  async ({ file, dataType }: { file: File; dataType: string }, { rejectWithValue }) => {
    try {
      const resp = await apiService.uploadData(file, dataType)
      return { dataType, data: resp.data || [] }
    } catch (e: any) {
      return rejectWithValue('Upload failed')
    }
  }
)

export const validateData = createAsyncThunk(
  'data/validateData',
  async (payload: { warehouses: any[]; customers: any[]; routes: any[] }, { rejectWithValue }) => {
    try {
      return await apiService.validateData(payload)
    } catch (e: any) {
      return rejectWithValue('Validation failed')
    }
  }
)

export const deleteData = createAsyncThunk(
  'data/deleteData',
  async (dataType: string, { rejectWithValue }) => {
    try {
      await apiService.deleteData(dataType)
      return dataType
    } catch (e: any) {
      return rejectWithValue('Delete failed')
    }
  }
)

// --- Slice -----------------------------------------------------------------
const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    clearError: (state) => { state.error = null },
    clearValidation: (state) => { state.validation = null },
    setWarehouses: (state, action: PayloadAction<any[]>) => { state.warehouses = action.payload },
    setCustomers: (state, action: PayloadAction<any[]>) => { state.customers = action.payload },
    setRoutes: (state, action: PayloadAction<any[]>) => { state.routes = action.payload },
  },
  extraReducers: (builder) => {
    // Dashboard
    builder
      .addCase(fetchDashboardData.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchDashboardData.fulfilled, (state, action) => { state.loading = false; state.dashboardData = action.payload })
      .addCase(fetchDashboardData.rejected, (state, action) => { state.loading = false; state.error = action.payload as string })

    // Bulk Data Fetch
    builder
      .addCase(fetchData.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchData.fulfilled, (state, action) => {
        state.loading = false
        state.warehouses = action.payload.warehouses
        state.customers = action.payload.customers
        state.routes = action.payload.routes
      })
      .addCase(fetchData.rejected, (state, action) => { state.loading = false; state.error = action.payload as string })

    // Upload
    builder
      .addCase(uploadData.pending, (state) => { state.loading = true; state.error = null })
      .addCase(uploadData.fulfilled, (state, action) => {
        state.loading = false
        const { dataType, data } = action.payload
        if (dataType === 'warehouses') state.warehouses = data
        if (dataType === 'customers') state.customers = data
        if (dataType === 'routes') state.routes = data
      })
      .addCase(uploadData.rejected, (state, action) => { state.loading = false; state.error = action.payload as string })

    // Validation
    builder
      .addCase(validateData.pending, (state) => { state.loading = true; state.error = null; state.validation = null })
      .addCase(validateData.fulfilled, (state, action) => { state.loading = false; state.validation = action.payload as ValidationResult })
      .addCase(validateData.rejected, (state, action) => { state.loading = false; state.error = action.payload as string })

    // Deletion
    builder
      .addCase(deleteData.pending, (state) => { state.loading = true; state.error = null })
      .addCase(deleteData.fulfilled, (state, action) => {
        state.loading = false
        const dt = action.payload
        if (dt === 'warehouses') state.warehouses = []
        if (dt === 'customers') state.customers = []
        if (dt === 'routes') state.routes = []
      })
      .addCase(deleteData.rejected, (state, action) => { state.loading = false; state.error = action.payload as string })
  }
})

export const { clearError, clearValidation, setWarehouses, setCustomers, setRoutes } = dataSlice.actions
export default dataSlice.reducer
