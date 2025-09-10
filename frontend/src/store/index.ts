import { configureStore } from '@reduxjs/toolkit'
import authSlice from './authSlice'
import dataSlice from './dataSlice'
import optimizationSlice from './optimizationSlice'
import uiSlice from './uiSlice'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    data: dataSlice,
    optimization: optimizationSlice,
    ui: uiSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
