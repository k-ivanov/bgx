# Astroship Theme Update

This document describes the updated design system based on the **Astroship** theme from TailAwesome. The new design follows a cleaner, more minimalist aesthetic with lighter colors and subtle styling.

## Color Palette Update

### Primary Color (Sky Blue)
```js
primary: {
  50: '#f0f9ff',
  100: '#e0f2fe',
  200: '#bae6fd',
  300: '#7dd3fc',
  400: '#38bdf8',
  500: '#0ea5e9',
  600: '#0284c7',  // DEFAULT
  700: '#0369a1',  // dark
  800: '#075985',
  900: '#0c4a6e',
}
```

### Secondary Color (Zinc Gray)
```js
secondary: {
  50: '#fafafa',
  100: '#f4f4f5',
  200: '#e4e4e7',
  300: '#d4d4d8',
  400: '#a1a1aa',
  500: '#71717a',  // DEFAULT
  600: '#52525b',
  700: '#3f3f46',
  800: '#27272a',
  900: '#18181b',
}
```

### Accent Color (Magenta/Purple)
```js
accent: {
  50: '#fdf4ff',
  100: '#fae8ff',
  200: '#f5d0fe',
  300: '#f0abfc',
  400: '#e879f9',
  500: '#d946ef',
  600: '#c026d3',  // DEFAULT
  700: '#a21caf',  // dark
  800: '#86198f',
  900: '#701a75',
}
```

### Success Color
```js
success: {
  DEFAULT: '#10b981',
  light: '#34d399',
  dark: '#059669',
}
```

## Shadow System

Lighter, more subtle shadows:
```js
boxShadow: {
  'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  'soft': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
  'medium': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
  'large': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)',
  'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
}
```

## Typography

- **Font Family**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700, 800
- **Fallback**: System UI fonts

## Component Updates

### 1. App Header
**Before:**
- Heavy blue gradient background
- White text
- Wave pattern overlay
- Drop shadow

**After:**
- Clean white background
- Dark text (`#18181b`)
- Subtle shadow and border
- Sticky positioning with backdrop blur
- Minimalist button styling

### 2. App Footer
**Before:**
- Dark gradient background
- White/translucent text

**After:**
- Light gray background (`#fafafa`)
- Medium gray text (`#71717a`)
- Simple border-top

### 3. Dashboard
**Before:**
- Gradient header with white text
- Heavy shadows on cards
- Colorful gradients

**After:**
- White sticky header with subtle shadow
- Clean card borders and soft shadows
- Text-based navigation
- Hover effects with border color changes

### 4. Buttons

**Primary Button:**
```css
background: #0284c7
color: white
border-radius: 8px
font-weight: 600
hover: background: #0369a1
```

**Secondary Button:**
```css
color: #52525b
hover: color: #18181b
font-weight: 500
```

### 5. Cards

**Standard Card:**
```css
background: white
border-radius: 12px
border: 1px solid #e4e4e7
box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)
hover: border-color: #0284c7
```

### 6. Tables
- **Header background**: `#fafafa`
- **Border color**: `#e4e4e7`
- **Header text**: `#52525b`
- **Hover row**: `#fafafa`

### 7. Loading Spinner
- **Border color**: `#e4e4e7`
- **Active border**: `#0284c7`
- Simpler, cleaner animation

### 8. Status Badges
- Lighter backgrounds (50-100 shades)
- Medium font weight (not bold)
- Subtle borders

## Design Principles

1. **Minimalism**: Remove unnecessary gradients and heavy effects
2. **Clarity**: Use clear borders and spacing instead of shadows
3. **Subtle Interactions**: Gentle hover effects and transitions
4. **Readability**: High contrast text on clean backgrounds
5. **Consistency**: Uniform spacing and sizing throughout

## Migration Notes

### Key Color Replacements:
- `#2563eb` → `#0284c7` (primary)
- `#64748b` → `#71717a` (secondary)
- `#e2e8f0` → `#e4e4e7` (borders)
- `#f8fafc` → `#fafafa` (backgrounds)
- `#0f172a` → `#18181b` (dark text)

### Shadow Replacements:
- Heavy drop shadows → `shadow-soft`
- Large shadows → `shadow-medium`
- Colored shadows → Neutral gray shadows

### Button Updates:
- Remove gradients
- Solid colors with simple hover states
- Smaller padding and font sizes
- Border-radius: 8px (was 12px+)

## Files Updated

1. `tailwind.config.js` - Color palette and shadow system
2. `bgx-fe/src/App.css` - Main app styling
3. `bgx-fe/src/App.jsx` - Header button styling
4. `bgx-fe/src/components/Dashboard.jsx` - Dashboard styling
5. `bgx-fe/src/components/ChampionshipSelector.css` - Selector styling
6. `bgx-fe/src/components/RaceList.css` - Table and list styling

## Result

The application now has a:
- ✨ Cleaner, more professional appearance
- 📱 Better mobile-first responsive design
- 🎨 Subtle, elegant color palette
- 🚀 Modern, minimalist aesthetic
- 👁️ Improved readability and clarity

The Astroship theme emphasizes content over decoration, making the racing data and functionality the star of the show.

