# CryoPredict Frontend — Antarctic Ice Intelligence Platform

A production-minded, dark-themed scientific research web interface for exploring Antarctic Peninsula ice volume and mass balance research, transient physical modeling outputs, and verified machine-learning historical benchmarks.

---

## 1. Technology Stack

- **Framework:** React 18 (TypeScript 5)
- **Bundler:** Vite 5
- **Styling:** Tailwind CSS 3 (Deep charcoal / near-black palette with ice-blue accents)
- **Routing:** React Router DOM 6
- **Data Visualization:** Recharts
- **Icons:** Lucide React
- **HTTP Client:** Axios (centralized in `src/api/client.ts`)

---

## 2. Platform Architecture

```
frontend/
├── public/
│   └── figures/                 # Authentic scientific figures & cartographic exports
├── src/
│   ├── api/
│   │   ├── client.ts            # Centralized Axios client & API error handlers
│   │   └── types.ts             # Strict TypeScript definitions for backend payloads
│   ├── components/
│   │   ├── common/              # Reusable UI primitives (Card, Badge, StatCard, etc.)
│   │   │   ├── Badge.tsx
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── ErrorMessage.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ScientificDisclaimer.tsx
│   │   │   └── StatCard.tsx
│   │   └── layout/              # Structural chrome (Sidebar, Header, Layout)
│   │       ├── Header.tsx
│   │       ├── Layout.tsx
│   │       └── Sidebar.tsx
│   ├── pages/                   # Seven authoritative scientific research pages
│   │   ├── OverviewPage.tsx     # Region overview, 3 basins, historical timeseries
│   │   ├── ModelLabPage.tsx     # 6-candidate ML benchmark & coefficient analysis
│   │   ├── PredictionLabPage.tsx # Interactive live inference console (POST /api/predictions/run)
│   │   ├── IceSheetExplorerPage.tsx # Spatial maps, Bedmap3 thickness, velocity fields
│   │   ├── DatasetExplorerPage.tsx  # 14-dataset inventory & 14-feature dictionary
│   │   ├── PhysicalModelPage.tsx    # 2D SSA finite-volume formulation & friction inversion
│   │   └── ValidationPage.tsx   # 80-test research audit & limitation disclosures
│   ├── App.tsx                  # Client router configuration
│   ├── index.css                # Tailwind directives & dark scientific scrollbar
│   ├── main.tsx                 # Application DOM bootstrap
│   └── vite-env.d.ts            # Vite client environment typing
├── .env.example                 # Template for environment variables
├── .env                         # Local environment configuration
├── index.html                   # HTML5 shell
├── package.json                 # Dependency manifest
├── postcss.config.js            # PostCSS configuration
├── tailwind.config.js           # Scientific dark theme color extensions
├── tsconfig.json                # TypeScript project configuration
├── tsconfig.node.json           # Vite node configuration
└── vite.config.ts               # Vite server & bundler configuration
```

---

## 3. Getting Started

### Prerequisites
- Node.js 18+ (tested with v24.3.0)
- CryoPredict FastAPI backend running on `http://127.0.0.1:8000`

### Installation
From the repository root:
```bash
cd frontend
npm install
```

### Running the Development Server
```bash
npm run dev
```
The application will launch on `http://127.0.0.1:5173`.

### Building for Production
```bash
npm run build
```

### Running the Production Preview
```bash
npm run preview -- --port 5173 --host 127.0.0.1
```

---

## 4. Configuration

Environment settings are configured via `.env` using Vite's `VITE_` prefix:

```bash
# CryoPredict Backend API Origin
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend uses `CryoApi` (`src/api/client.ts`) for all network requests. The API base URL is never hardcoded across components.

---

## 5. Authoritative Pages

1. **Overview (`/`):**
   - Geographic summary of Antarctic Peninsula Domain A (866,358 grounded cells).
   - Basin metrics across Palmer Land West (`Hp-I`), Graham Land (`I-Ipp`), and Palmer Land East (`Ipp-J`).
   - Dynamic 46-year historical mass balance and volume change trajectory chart.
2. **Model Laboratory (`/models`):**
   - Comparative evaluation across all six candidates: ElasticNet (Selected Primary), Bayesian Ridge, Random Forest, Gradient Boosting, Historical Mean, and Persistence.
   - Per-basin fold validation metrics and learned feature coefficients/importances.
3. **Prediction Laboratory (`/predictions`):**
   - Interactive live inference console invoking `POST /api/predictions/run`.
   - Real-time conversion: $\Delta V = \Delta M / 0.917\ \text{Gt/km}^3$.
   - Strict centennial 2100 forecast rejection guardrail.
4. **Ice Sheet Explorer (`/explorer`):**
   - Authentic spatial maps: BedMachine v4.1 boundary, Bedmap3 thickness, flotation masks, InSAR satellite ice velocity, and mass budget divergence.
5. **Dataset Explorer (`/datasets`):**
   - Complete 14-dataset inventory and the frozen 14-feature dictionary with operational lags and ElasticNet sparsity weights.
6. **Physical Model (`/physical-model`):**
   - Depth-integrated 2D SSA momentum equations, Glen's Flow Law ($n=3$), Weertman regularized basal friction ($C_{\text{bed}}$), and finite-volume conservation.
7. **Validation & Audit (`/validation`):**
   - Stratified testing audit: 80 core research tests (`tests/`) and 24 web backend tests (`backend/tests/`).
   - CryoSat-2 altimetry discrepancy disclosure (+60.52 Gt/yr hold status).
   - Formal statement on the prohibition of century-scale projections.

---

## 6. Scientific Integrity & Disclosures

- **No Fabricated Data:** Every figure, metric, and coefficient originates from the verified research outputs.
- **Dual-Tier Prediction System:** Historical predictions and live inference are kept strictly segregated in both UI presentation and API routes.
- **Prohibition of 2100 Extrapolations:** Requests for years $\ge 2100$ are blocked at both client and server boundaries.
