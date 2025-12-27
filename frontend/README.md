# Reconciliation Engine - Frontend

A modern, real-time React dashboard for monitoring transaction reconciliation with live updates, beautiful UI, and enterprise-grade features.

## 🚀 Features

- **Real-Time Updates**: Socket.IO integration for live transaction and mismatch notifications
- **Modern UI**: Glassmorphism design with dark theme and smooth animations
- **Responsive**: Mobile-first design that works on all devices
- **Data Visualization**: Interactive charts using Recharts
- **Authentication**: Mock authentication for development
- **Type Safety**: Built with modern React patterns and hooks

## 📦 Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **TailwindCSS** - Utility-first CSS framework
- **Socket.IO Client** - Real-time communication
- **Axios** - HTTP client
- **Recharts** - Chart library

- **Lucide React** - Icon library

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

Create a `.env` file in the frontend directory (or copy from `.env.example`):

```env
# Backend API Configuration
VITE_API_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Keycloak Configuration
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=reconciliation
VITE_KEYCLOAK_CLIENT_ID=reconciliation-frontend

# Feature Flags
VITE_ENABLE_KEYCLOAK=false
VITE_ENABLE_SOCKET=true
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/          # Reusable components
│   │   ├── dashboard/       # Dashboard-specific components
│   │   └── layout/          # Layout components
│   ├── pages/               # Page components
│   ├── services/            # API and service layer
│   ├── hooks/               # Custom React hooks
│   ├── context/             # React context providers
│   ├── utils/               # Utility functions
│   ├── styles/              # Global styles
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # Tailwind configuration
└── package.json             # Dependencies
```

## 🎨 Design System

The application uses a custom design system with:

- **Glassmorphism**: Frosted glass effect cards
- **Dark Theme**: Premium dark color palette
- **Animations**: Smooth transitions and micro-interactions
- **Typography**: Inter font family
- **Color Palette**: Custom primary, success, warning, and danger colors

## 🔌 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default. API endpoints:

- `GET /transactions/` - List all transactions
- `GET /transactions/{id}` - Get transaction by ID
- `GET /mismatches/` - List all mismatches
- `GET /mismatches/{id}` - Get mismatch by ID

## 🔄 Real-Time Features

Socket.IO events:
- `new_transaction` - New transaction received
- `new_mismatch` - New mismatch detected
- `connect` - Connection established
- `disconnect` - Connection lost

## 🔐 Authentication

The app supports two authentication modes:

1. **Mock Auth** (Development): Simplified authentication for development

## 📱 Pages

- **Dashboard** (`/`) - Overview with stats, charts, and recent activity
- **Transactions** (`/transactions`) - Searchable transaction table
- **Mismatches** (`/mismatches`) - Mismatch detection and resolution

## 🎯 Next Steps

1. **Backend Integration**: Ensure backend API endpoints are implemented
2. **Socket.IO Server**: Add Socket.IO to FastAPI backend
3. **CORS Configuration**: Enable CORS for frontend origin

5. **Testing**: Add unit and integration tests

## 📝 Development Notes

- The app uses mock data when backend endpoints return errors
- Mock authentication is used for simplified development
- Socket.IO will gracefully degrade if server is unavailable
- All components are responsive and mobile-friendly

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Change port in vite.config.js or use:
npm run dev -- --port 3000
```

**API connection errors:**
- Ensure backend is running on port 8000
- Check CORS configuration in backend
- Verify `VITE_API_URL` in `.env`

**Socket.IO not connecting:**
- Ensure Socket.IO server is running in backend
- Check `VITE_SOCKET_URL` in `.env`
- Verify firewall/proxy settings

## 📄 License

MIT
