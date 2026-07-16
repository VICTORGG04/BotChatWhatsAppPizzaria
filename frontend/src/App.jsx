import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CardapioPage from './pages/CardapioPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CardapioPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
