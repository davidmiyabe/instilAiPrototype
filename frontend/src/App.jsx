import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Dashboard from './pages/Dashboard'
import Constituents from './pages/Constituents'
import ConstituentDetail from './pages/ConstituentDetail'
import Contributions from './pages/Contributions'
import Layout from './components/Layout'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="constituents" element={<Constituents />} />
            <Route path="constituents/:id" element={<ConstituentDetail />} />
            <Route path="contributions" element={<Contributions />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
