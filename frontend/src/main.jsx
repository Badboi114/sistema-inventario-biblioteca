
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import PublicConsulta from './PublicConsulta';
import { CartProvider } from './context/CartContext';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CartProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/consulta" element={<PublicConsulta />} />
          <Route path="/*" element={<App />} />
        </Routes>
      </BrowserRouter>
    </CartProvider>
  </StrictMode>
);
