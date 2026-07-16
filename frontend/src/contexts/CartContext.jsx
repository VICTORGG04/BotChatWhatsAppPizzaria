import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'pizzaria_cart';
const NOTE_KEY = 'pizzaria_cart_notes';

const CartContext = createContext();

function loadCart() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch { return {}; }
}

function loadNotes() {
  try { return JSON.parse(localStorage.getItem(NOTE_KEY)) || {}; } catch { return {}; }
}

export function CartProvider({ children }) {
  const [cart, setCart] = useState(loadCart);
  const [customNotes, setCustomNotes] = useState(loadNotes);

  useEffect(() => { localStorage.setItem(STORAGE_KEY, JSON.stringify(cart)); }, [cart]);
  useEffect(() => { localStorage.setItem(NOTE_KEY, JSON.stringify(customNotes)); }, [customNotes]);

  const updateQty = useCallback((key, delta) => {
    setCart(prev => {
      const next = { ...prev };
      next[key] = (next[key] || 0) + delta;
      if (next[key] <= 0) delete next[key];
      return next;
    });
  }, []);

  const setQty = useCallback((key, val) => {
    setCart(prev => {
      const next = { ...prev };
      if (val > 0) next[key] = val; else delete next[key];
      return next;
    });
  }, []);

  const removeItem = useCallback((key) => {
    setCart(prev => { const n = { ...prev }; delete n[key]; return n; });
  }, []);

  const setNote = useCallback((chave, val) => {
    setCustomNotes(prev => {
      const n = { ...prev };
      if (val) n[chave] = val; else delete n[chave];
      return n;
    });
  }, []);

  const clearCart = useCallback(() => { setCart({}); setCustomNotes({}); }, []);

  const totalItems = Object.values(cart).reduce((a, b) => a + b, 0);

  return (
    <CartContext.Provider value={{ cart, customNotes, updateQty, setQty, removeItem, setNote, clearCart, totalItems }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() { return useContext(CartContext); }
