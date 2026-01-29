import { createContext, useState, useContext } from 'react';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState([]);

  const addToCart = (item) => {
    // Evitar duplicados
    if (!cart.find(i => i.id === item.id)) {
      setCart(prev => {
        const nuevo = [...prev, item];
        if (typeof window !== 'undefined') {
          window.cart = nuevo;
        }
        return nuevo;
      });
    }
  };

  // Exponer addToCart globalmente para uso en Prestamos.jsx
  if (typeof window !== 'undefined') {
    window.addToCart = addToCart;
  }

  const removeFromCart = (id) => {
    setCart(cart.filter(item => item.id !== id));
  };

  const clearCart = () => setCart([]);

  const toggleItem = (item) => {
    if (cart.find(i => i.id === item.id)) {
      removeFromCart(item.id);
    } else {
      addToCart(item);
    }
  };

  return (
    <CartContext.Provider value={{ cart, addToCart, removeFromCart, clearCart, toggleItem }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
