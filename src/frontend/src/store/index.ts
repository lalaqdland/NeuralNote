import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import graphReducer from './graphSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    graph: graphReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

