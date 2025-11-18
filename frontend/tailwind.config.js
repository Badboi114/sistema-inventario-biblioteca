/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1e3a8a', // Azul serio institucional
        secondary: '#fbbf24', // Ámbar para detalles
        danger: '#ef4444', // Rojo alertas
        dark: '#111827', // Fondo oscuro sidebar
        light: '#f3f4f6', // Fondo claro contenido
      },
    },
  },
  plugins: [],
}
