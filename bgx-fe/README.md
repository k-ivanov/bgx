# BGX Racing Platform - Frontend

React frontend for the BGX Racing Platform built with Vite and Tailwind CSS.

## Prerequisites

- Node.js 18+ and npm
- BGX API running on `http://localhost:8000`

## Getting Started

### 1. Install Dependencies

```bash
cd bgx-fe
npm install
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features

- 🏆 Browse championships and view races
- 🏁 View race details with category filtering
- 📊 View race results by category
- 👤 User registration with activation codes
- 🔑 Account activation system
- 🌍 Internationalization (English & Bulgarian)
- 📱 Responsive design
- 🎨 Modern UI with Tailwind CSS
- ⚡ Fast performance with Vite

## Internationalization

The application supports two languages:
- **English (EN)** - Default language
- **Bulgarian (BG)** - Full translation

### Language Switching

Users can switch languages using the language switcher in the header (EN | BG).

**Language preference is synchronized between frontend and backend using cookies:**
- Cookie name: `django_language`
- Persistence: 1 year
- Syncs automatically on page load
- Includes `Accept-Language` header in API requests

### Translation Files

Translation files are located in `src/i18n/locales/`:
- `en.json` - English translations
- `bg.json` - Bulgarian translations

### Language Synchronization

The app automatically syncs language preferences:

1. **On Load:** Reads `django_language` cookie
2. **On Change:** Updates both frontend and backend
3. **API Requests:** Include `Accept-Language` header
4. **Persistence:** Cookie stored for 1 year

```javascript
// Language utilities
import { syncLanguageOnInit, changeLanguage } from './utils/languageSync'

// Sync on app load
await syncLanguageOnInit()

// Change language
await changeLanguage('bg')
```

### Adding Translations

To add or modify translations:

1. Edit the JSON files in `src/i18n/locales/`
2. Use the `useTranslation` hook in components:

```jsx
import { useTranslation } from 'react-i18next'

function MyComponent() {
  const { t } = useTranslation()
  
  return <h1>{t('my.translation.key')}</h1>
}
```

### Supported Translation Keys

See `src/i18n/locales/en.json` for the complete list of translation keys.

## User Registration Flow

### 1. Register
Navigate to `/register` or click "Register" in the header:
- Fill in: First Name, Last Name, Username, Email, Password
- Submit the form
- You'll receive an **Activation Code** (save it!)

### 2. Activate
Navigate to `/activate` or click "Activate" in the header:
- Enter your activation code
- Submit to activate your account
- You'll be automatically logged in and redirected

### 3. Race Results
- Browse championships on the home page
- Click "View Details" on any race
- Select a category (Expert, Profi, Junior, etc.)
- View results with rider names, clubs, points, and times

## Project Structure

```
bgx-fe/
├── src/
│   ├── api/              # API integration
│   │   └── api.js
│   ├── components/       # React components
│   │   ├── ChampionshipSelector.jsx/.css
│   │   ├── RaceList.jsx/.css
│   │   ├── RaceDetail.jsx/.css
│   │   ├── Register.jsx/.css
│   │   ├── Activate.jsx/.css
│   │   └── LanguageSwitcher.jsx/.css
│   ├── i18n/             # Internationalization
│   │   ├── config.js
│   │   └── locales/
│   │       ├── en.json
│   │       └── bg.json
│   ├── App.jsx          # Main app component
│   ├── App.css
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles (Tailwind)
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── vite.config.js
└── package.json
```

## Building for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

## Connecting to API

The frontend uses a proxy configuration in `vite.config.js` to connect to the Django backend:

- Development: Proxies `/api` requests to `http://localhost:8000`
- Production: Set `VITE_API_URL` environment variable

## Technologies

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **i18next** - Internationalization
- **Tailwind CSS** - Styling
- **React i18next** - React bindings for i18next

## License

MIT
