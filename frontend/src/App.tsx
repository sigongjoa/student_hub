import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { StudentList } from './pages/StudentList';
import { StudentDetail } from './pages/StudentDetail';
import { ChatPanel } from './features/chat/ChatPanel';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/students" element={<StudentList />} />
          <Route path="/students/:id" element={<StudentDetail />} />
          {/* Fallback routes */}
          <Route path="/logic" element={<Navigate to="/" />} />
          <Route path="/q-dna" element={<Navigate to="/" />} />
          <Route path="/reports" element={<Navigate to="/" />} />
          <Route path="/lab" element={<Navigate to="/" />} />
          <Route path="/school" element={<Navigate to="/" />} />
        </Routes>

        {/* Chat Panel - Always visible */}
        <ChatPanel />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
