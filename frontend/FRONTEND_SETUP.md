# Water Prediction Frontend - Setup Guide

## Quick Start

### Prerequisites
- Node.js 14+ and npm
- Backend API running at `http://localhost:8000`

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings:
   ```
   REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
   REACT_APP_COLLEGE_NAME=IIIT
   REACT_APP_NODE_ID=sensor-node-001
   ```

4. **Start development server:**
   ```bash
   npm start
   ```
   Opens http://localhost:3000 automatically

## Project Structure

```
frontend/
├── public/
│   └── index.html              # Main HTML template
├── src/
│   ├── components/
│   │   ├── Navbar.js           # Top navigation with college branding
│   │   ├── Sidebar.js          # Left sidebar navigation
│   │   └── CustomCharts.js     # Reusable chart components
│   ├── pages/
│   │   ├── Home.js             # Dashboard with sensor data
│   │   ├── Prediction.js       # ML prediction interface
│   │   ├── History.js          # Historical data & analysis
│   │   ├── Settings.js         # System configuration
│   │   └── About.js            # About & tech stack
│   ├── styles/
│   │   ├── App.css             # Global styles & theme
│   │   ├── Navbar.css          # Navigation styling
│   │   ├── Sidebar.css         # Sidebar styling
│   │   ├── Home.css            # Dashboard styling
│   │   ├── Prediction.css      # Prediction page styling
│   │   ├── History.css         # History page styling
│   │   ├── Charts.css          # Chart component styling
│   │   └── Settings.css        # Settings/About styling
│   ├── utils/
│   │   ├── api.js              # Axios client & API endpoints
│   │   └── constants.js        # Shared constants
│   ├── config.js               # Theme colors & college branding
│   ├── App.js                  # Main app component with routing
│   └── index.js                # React entry point
├── package.json                # Dependencies
└── .env.example               # Environment template
```

## Key Features

### 1. College Branding (config.js)
```javascript
const config = {
  COLLEGE_NAME: 'IIIT',
  COLLEGE_LOGO: 'path/to/logo.png',
  THEME: {
    primary: '#1e3a8a',
    success: '#059669',
    // ... more colors
  }
};
```

### 2. Pages

#### Dashboard (Home.js)
- Real-time sensor data display
- Statistics cards with progress bars
- Model status display
- System health indicators
- Auto-refreshes every 30 seconds

#### Prediction Page (Prediction.js)
- Water activity prediction form
- Model information display
- Confidence gauge (SVG-based)
- Activity timeline chart
- Prediction distribution chart
- Prediction history table

#### History (History.js)
- Prediction statistics
- Distribution bars for activity types
- Filterable predictions table
- Sensor history data
- Confidence visualization

#### Settings (Settings.js)
- API configuration
- Display preferences
- Theme selection
- Node ID configuration

#### About (About.js)
- System overview
- Features list
- Technology stack breakdown
- System information
- Contact details

### 3. API Integration

All API calls go through `/src/utils/api.js`:

```javascript
import { apiEndpoints } from './utils/api';

// Get model info
const modelInfo = await apiEndpoints.getModelInfo();

// Make prediction
const result = await apiEndpoints.makePrediction(inputs);

// Get prediction history
const history = await apiEndpoints.getPredictionsHistory();
```

## Customization

### Update College Branding
Edit `src/config.js`:
```javascript
export const config = {
  COLLEGE_NAME: 'Your College Name',
  COLLEGE_LOGO: '/path/to/your/logo.png',
  // ... other settings
};
```

### Change Theme Colors
Edit theme in `src/config.js` or CSS variables in `src/styles/App.css`:
```css
:root {
  --primary-color: #1e3a8a;        /* Primary blue */
  --success-color: #059669;        /* Success green */
  --warning-color: #d97706;        /* Warning orange */
  /* ... update as needed */
}
```

### Update API Base URL
Change `REACT_APP_API_BASE_URL` in `.env`

## Available Scripts

- `npm start` - Start development server (port 3000)
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App (irreversible)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive design)

## Troubleshooting

### 1. "Cannot GET /api/v1/..." errors
**Solution:** Ensure backend is running at the URL in `.env`
```bash
# Backend should be running at:
http://localhost:8000
```

### 2. Port 3000 already in use
**Solution:** Use a different port
```bash
PORT=3001 npm start
```

### 3. Module not found errors
**Solution:** Install dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

### 4. Sidebar not appearing on mobile
**Solution:** Click hamburger menu icon in navbar to toggle

## Performance Tips

1. **Data Refresh Rate:** Adjust in each page component
2. **Chart Updates:** Charts optimize re-renders automatically
3. **Image Optimization:** Compress logo image before adding
4. **Code Splitting:** React Router automatically code-splits pages

## Deployment

### Build for Production
```bash
npm run build
```

### Deploy Built Files
The `build/` folder contains static files ready for:
- Netlify
- Vercel
- GitHub Pages
- Traditional web servers

### Environment Configuration for Production
```bash
# .env
REACT_APP_API_BASE_URL=https://your-backend-api.com/api/v1
```

## API Documentation

See `../IMPLEMENTATION_COMPLETE.md` for backend API details

## Support & Contact

For issues or questions, refer to the project README or backend documentation.
