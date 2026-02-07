import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { KnowledgeGraph } from '../services/knowledgeGraph';

interface GraphState {
  currentGraph: KnowledgeGraph | null;
  graphs: KnowledgeGraph[];
  loading: boolean;
}

const initialState: GraphState = {
  currentGraph: null,
  graphs: [],
  loading: false,
};

const graphSlice = createSlice({
  name: 'graph',
  initialState,
  reducers: {
    setCurrentGraph: (state, action: PayloadAction<KnowledgeGraph | null>) => {
      state.currentGraph = action.payload;
    },
    setGraphs: (state, action: PayloadAction<KnowledgeGraph[]>) => {
      state.graphs = action.payload;
    },
    addGraph: (state, action: PayloadAction<KnowledgeGraph>) => {
      state.graphs.unshift(action.payload);
    },
    updateGraph: (state, action: PayloadAction<KnowledgeGraph>) => {
      const index = state.graphs.findIndex((g) => g.id === action.payload.id);
      if (index !== -1) {
        state.graphs[index] = action.payload;
      }
      if (state.currentGraph?.id === action.payload.id) {
        state.currentGraph = action.payload;
      }
    },
    removeGraph: (state, action: PayloadAction<string>) => {
      state.graphs = state.graphs.filter((g) => g.id !== action.payload);
      if (state.currentGraph?.id === action.payload) {
        state.currentGraph = null;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setCurrentGraph, setGraphs, addGraph, updateGraph, removeGraph, setLoading } =
  graphSlice.actions;
export default graphSlice.reducer;

