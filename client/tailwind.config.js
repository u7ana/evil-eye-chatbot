/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // semantic tokens — resolved by CSS variables so dark mode swaps in one place
        paper: 'var(--paper)',
        card: 'var(--card)',
        side: 'var(--side)',
        line: 'var(--line)',
        body: 'var(--text)',
        dim: 'var(--dim)',
        // fixed brand greens (safe to use with /opacity modifiers)
        pine: '#1e5128',
        moss: '#6b9b4e',
        sage: '#94b877',
        cream: '#f2f5e8',
        inkg: '#10331b',
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        sans: ['Karla', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
