/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'hva-deep': '#050a12',
                'hva-primary': '#0a0f1a',
                'hva-card': '#0f1520',
                'hva-card-hover': '#141c2a',
                'hva-accent': '#5d9a9b',
                'hva-accent-light': '#7ab8b9',
                'hva-cream': '#f5e6d3',
                'hva-muted': '#8a9aaa',
                'hva-dim': '#5a6a7a',
            },
            borderRadius: {
                'hva-sm': '12px',
                'hva-md': '16px',
                'hva-lg': '24px',
                'hva-xl': '32px',
            }
        },
    },
    plugins: [],
}
