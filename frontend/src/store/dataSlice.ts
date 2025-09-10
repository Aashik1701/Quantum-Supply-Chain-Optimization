import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface DataState {
  warehouses: any[]
  customers: any[]
  routes: any[]
  loading: boolean
  error: string | null
}

const initialState: DataState = {
  warehouses: [],
  customers: [],
  routes: [],
  loading: false,
  error: null,
}

const dataSlice = createSlice({
  name: 'data',
  initialState,
  reducers: {
    setWarehouses: (state, action) => {
      state.warehouses = action.payload
    },
    setCustomers: (state, action) => {
      state.customers = action.payload
    },
    setRoutes: (state, action) => {
      state.routes = action.payload
    },
    setLoading: (state, action) => {
      state.loading = action.payload
    },
    setError: (state, action) => {
      state.error = action.payload
    },
  },
})

export const { setWarehouses, setCustomers, setRoutes, setLoading, setError } = dataSlice.actions
export default dataSlice.reducer
