# Day 20: API Client & Routing - Detailed Implementation Plan

## 📋 Overview
**Duration:** 4 hours  
**Difficulty:** Beginner-Friendly  
**Goal:** Set up the foundation for communicating with the backend API and navigating between pages

---

## 🎯 What You'll Build

By the end of Day 20, you'll have:
1. An API client that talks to your FastAPI backend
2. A routing system to navigate between different pages
3. A basic layout structure for your app
4. A navigation menu

---

## 📚 Design Patterns & Concepts

### 1. **Singleton Pattern** (API Client)
- **What:** Only one instance of the API client exists throughout the app
- **Why:** Ensures consistent configuration and prevents multiple connections
- **Where:** `services/api.ts`

### 2. **Service Layer Pattern**
- **What:** Separates business logic from UI components
- **Why:** Makes code reusable and easier to test
- **Where:** All files in `services/` folder

### 3. **Layout Pattern** (React)
- **What:** A wrapper component that provides consistent structure across pages
- **Why:** Avoids repeating navigation/footer code on every page
- **Where:** `components/Layout.tsx`

### 4. **Declarative Routing**
- **What:** Define routes as configuration rather than imperative code
- **Why:** Easier to understand and maintain
- **Where:** `App.tsx`

---

## 🔧 Sub-Tasks Breakdown

### Sub-Task 1: Create API Client Base (45 minutes)

**What you're building:** A centralized service to make HTTP requests to your backend

**File:** `frontend/src/services/api.ts`

**Concepts to understand:**
- **Base URL:** The root address of your API (e.g., `http://localhost:8000`)
- **Axios Instance:** A pre-configured HTTP client
- **Interceptors:** Functions that run before/after every request

**Step-by-step:**

1. **Create the file structure:**
   ```
   frontend/src/services/api.ts
   ```

2. **Import dependencies:**
   ```typescript
   import axios from 'axios';
   ```

3. **Define the base URL:**
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
   ```
   - `import.meta.env` reads environment variables
   - `||` provides a fallback if the variable isn't set

4. **Create an axios instance:**
   ```typescript
   const apiClient = axios.create({
     baseURL: API_BASE_URL,
     headers: {
       'Content-Type': 'application/json',
     },
   });
   ```
   - This creates a pre-configured HTTP client
   - All requests will automatically use this base URL

5. **Add request interceptor (optional but recommended):**
   ```typescript
   apiClient.interceptors.request.use(
     (config) => {
       // You can add auth tokens here later
       console.log('Making request to:', config.url);
       return config;
     },
     (error) => {
       return Promise.reject(error);
     }
   );
   ```
   - Runs before every request
   - Useful for logging and adding authentication

6. **Add response interceptor:**
   ```typescript
   apiClient.interceptors.response.use(
     (response) => response,
     (error) => {
       console.error('API Error:', error.response?.data || error.message);
       return Promise.reject(error);
     }
   );
   ```
   - Runs after every response
   - Handles errors in one place

7. **Export the client:**
   ```typescript
   export default apiClient;
   ```

**Testing:** You can test this later when we create API functions

---

### Sub-Task 2: Create API Service Functions (45 minutes)

**What you're building:** Specific functions to interact with your backend endpoints

**File:** `frontend/src/services/searchRequestService.ts`

**Concepts to understand:**
- **TypeScript Interfaces:** Define the shape of your data
- **Async/Await:** Handle asynchronous operations
- **Generic Types:** Reusable type definitions

**Step-by-step:**

1. **Create TypeScript interfaces for your data:**
   ```typescript
   // Define what a SearchRequest looks like
   export interface SearchRequest {
     id?: number;
     query: string;
     platforms: string[];
     max_price?: number;
     min_price?: number;
     location?: string;
     is_active: boolean;
     created_at?: string;
     updated_at?: string;
   }

   // Define what a Product looks like
   export interface Product {
     id: number;
     title: string;
     price: number;
     url: string;
     platform: string;
     location?: string;
     description?: string;
     image_url?: string;
     match_score?: number;
     created_at: string;
   }
   ```

2. **Create CRUD functions:**
   ```typescript
   import apiClient from './api';

   // GET all search requests
   export const getSearchRequests = async (): Promise<SearchRequest[]> => {
     const response = await apiClient.get('/api/search-requests');
     return response.data;
   };

   // GET single search request
   export const getSearchRequest = async (id: number): Promise<SearchRequest> => {
     const response = await apiClient.get(`/api/search-requests/${id}`);
     return response.data;
   };

   // POST create new search request
   export const createSearchRequest = async (data: Omit<SearchRequest, 'id'>): Promise<SearchRequest> => {
     const response = await apiClient.post('/api/search-requests', data);
     return response.data;
   };

   // PUT update search request
   export const updateSearchRequest = async (id: number, data: Partial<SearchRequest>): Promise<SearchRequest> => {
     const response = await apiClient.put(`/api/search-requests/${id}`, data);
     return response.data;
   };

   // DELETE search request
   export const deleteSearchRequest = async (id: number): Promise<void> => {
     await apiClient.delete(`/api/search-requests/${id}`);
   };
   ```

3. **Create a product service file:**
   `frontend/src/services/productService.ts`
   ```typescript
   import apiClient from './api';
   import { Product } from './searchRequestService';

   export const getProducts = async (): Promise<Product[]> => {
     const response = await apiClient.get('/api/products');
     return response.data;
   };

   export const getMatchingProducts = async (): Promise<Product[]> => {
     const response = await apiClient.get('/api/products/matches');
     return response.data;
   };
   ```

**Key Concepts Explained:**
- `Promise<Type>`: The function returns a promise that resolves to that type
- `async/await`: Makes asynchronous code look synchronous
- `Omit<Type, 'key'>`: Creates a type without the specified key
- `Partial<Type>`: Makes all properties optional

---

### Sub-Task 3: Setup React Router (30 minutes)

**What you're building:** Navigation system for your app

**File:** `frontend/src/App.tsx`

**Concepts to understand:**
- **Routes:** Map URLs to components
- **BrowserRouter:** Enables client-side routing
- **Nested Routes:** Routes within routes

**Step-by-step:**

1. **Import React Router:**
   ```typescript
   import { BrowserRouter, Routes, Route } from 'react-router-dom';
   ```

2. **Create placeholder page components:**
   
   `frontend/src/pages/Dashboard.tsx`:
   ```typescript
   export default function Dashboard() {
     return (
       <div>
         <h1>Dashboard</h1>
         <p>Welcome to your Product Search Agent!</p>
       </div>
     );
   }
   ```

   `frontend/src/pages/Matches.tsx`:
   ```typescript
   export default function Matches() {
     return (
       <div>
         <h1>Matches</h1>
         <p>Your product matches will appear here.</p>
       </div>
     );
   }
   ```

   `frontend/src/pages/Settings.tsx`:
   ```typescript
   export default function Settings() {
     return (
       <div>
         <h1>Settings</h1>
         <p>Configure your preferences here.</p>
       </div>
     );
   }
   ```

3. **Update App.tsx with routes:**
   ```typescript
   import { BrowserRouter, Routes, Route } from 'react-router-dom';
   import Dashboard from './pages/Dashboard';
   import Matches from './pages/Matches';
   import Settings from './pages/Settings';

   function App() {
     return (
       <BrowserRouter>
         <Routes>
           <Route path="/" element={<Dashboard />} />
           <Route path="/matches" element={<Matches />} />
           <Route path="/settings" element={<Settings />} />
         </Routes>
       </BrowserRouter>
     );
   }

   export default App;
   ```

**Understanding Routes:**
- `path="/"`: The home page
- `element={<Component />}`: What to show at this path
- Routes are matched from top to bottom

---

### Sub-Task 4: Create Layout Component (45 minutes)

**What you're building:** A wrapper that provides consistent structure (header, nav, footer)

**File:** `frontend/src/components/Layout.tsx`

**Concepts to understand:**
- **Children Props:** Components can wrap other components
- **Composition:** Building complex UIs from simple pieces
- **Tailwind Classes:** Utility-first CSS

**Step-by-step:**

1. **Create the Layout component:**
   ```typescript
   import { ReactNode } from 'react';
   import { Link } from 'react-router-dom';

   interface LayoutProps {
     children: ReactNode;
   }

   export default function Layout({ children }: LayoutProps) {
     return (
       <div className="min-h-screen bg-gray-50">
         {/* Header */}
         <header className="bg-white shadow">
           <div className="max-w-7xl mx-auto px-4 py-4">
             <h1 className="text-2xl font-bold text-gray-900">
               Product Search Agent
             </h1>
           </div>
         </header>

         {/* Navigation */}
         <nav className="bg-white border-b">
           <div className="max-w-7xl mx-auto px-4">
             <div className="flex space-x-8">
               <Link 
                 to="/" 
                 className="py-4 px-2 border-b-2 border-transparent hover:border-blue-500"
               >
                 Dashboard
               </Link>
               <Link 
                 to="/matches" 
                 className="py-4 px-2 border-b-2 border-transparent hover:border-blue-500"
               >
                 Matches
               </Link>
               <Link 
                 to="/settings" 
                 className="py-4 px-2 border-b-2 border-transparent hover:border-blue-500"
               >
                 Settings
               </Link>
             </div>
           </div>
         </nav>

         {/* Main Content */}
         <main className="max-w-7xl mx-auto px-4 py-8">
           {children}
         </main>

         {/* Footer */}
         <footer className="bg-white border-t mt-auto">
           <div className="max-w-7xl mx-auto px-4 py-4 text-center text-gray-600">
             <p>© 2026 Product Search Agent</p>
           </div>
         </footer>
       </div>
     );
   }
   ```

2. **Wrap routes with Layout in App.tsx:**
   ```typescript
   import Layout from './components/Layout';

   function App() {
     return (
       <BrowserRouter>
         <Layout>
           <Routes>
             <Route path="/" element={<Dashboard />} />
             <Route path="/matches" element={<Matches />} />
             <Route path="/settings" element={<Settings />} />
           </Routes>
         </Layout>
       </BrowserRouter>
     );
   }
   ```

**Tailwind Classes Explained:**
- `min-h-screen`: Minimum height of viewport
- `bg-gray-50`: Light gray background
- `max-w-7xl`: Maximum width constraint
- `mx-auto`: Center horizontally
- `px-4`: Horizontal padding
- `py-4`: Vertical padding
- `space-x-8`: Horizontal spacing between children
- `hover:border-blue-500`: Blue border on hover

---

### Sub-Task 5: Add Active Link Styling (30 minutes)

**What you're building:** Visual feedback showing which page you're on

**File:** `frontend/src/components/Layout.tsx`

**Concepts to understand:**
- **useLocation Hook:** Get current URL
- **Conditional Classes:** Apply classes based on conditions

**Step-by-step:**

1. **Import useLocation:**
   ```typescript
   import { Link, useLocation } from 'react-router-dom';
   ```

2. **Use the hook:**
   ```typescript
   export default function Layout({ children }: LayoutProps) {
     const location = useLocation();
     
     // Helper function to check if link is active
     const isActive = (path: string) => location.pathname === path;
   ```

3. **Update Link components:**
   ```typescript
   <Link 
     to="/" 
     className={`py-4 px-2 border-b-2 ${
       isActive('/') 
         ? 'border-blue-500 text-blue-600' 
         : 'border-transparent hover:border-blue-500'
     }`}
   >
     Dashboard
   </Link>
   ```

**Understanding the Code:**
- `location.pathname`: Current URL path
- Template literals with `${}`: Embed JavaScript in strings
- Ternary operator `? :`: If-else in one line
- Active links get blue border and text

---

### Sub-Task 6: Create Environment Configuration (15 minutes)

**What you're building:** Configuration file for different environments

**File:** `frontend/.env.development`

**Step-by-step:**

1. **Create environment file:**
   ```
   VITE_API_URL=http://localhost:8000
   ```

2. **Create production environment file:**
   `frontend/.env.production`
   ```
   VITE_API_URL=https://your-production-api.com
   ```

3. **Update .gitignore to exclude local env:**
   ```
   .env.local
   ```

**Key Points:**
- Vite requires `VITE_` prefix for environment variables
- `.env.development`: Used during `npm run dev`
- `.env.production`: Used during `npm run build`
- Never commit sensitive data to `.env` files

---

## 🧪 Testing Your Work

### Test 1: API Client
```typescript
// In browser console or a test file
import { getSearchRequests } from './services/searchRequestService';

getSearchRequests().then(data => console.log(data));
```

### Test 2: Routing
1. Start dev server: `npm run dev`
2. Navigate to `http://localhost:5173/`
3. Click navigation links
4. Check URL changes
5. Verify active link styling

### Test 3: Layout
1. Check header appears on all pages
2. Check navigation works
3. Check footer appears
4. Verify responsive design (resize browser)

---

## 📁 Final File Structure

```
frontend/src/
├── services/
│   ├── api.ts                    # Base API client (Singleton)
│   ├── searchRequestService.ts   # Search request API calls
│   └── productService.ts         # Product API calls
├── components/
│   └── Layout.tsx                # Layout wrapper component
├── pages/
│   ├── Dashboard.tsx             # Home page
│   ├── Matches.tsx               # Matches page
│   └── Settings.tsx              # Settings page
├── App.tsx                       # Main app with routing
└── main.tsx                      # Entry point
```

---

## 🎓 Key Learnings

After completing Day 20, you'll understand:

1. **API Communication:**
   - How to make HTTP requests
   - How to handle responses and errors
   - How to organize API calls

2. **Routing:**
   - How to navigate between pages
   - How to define routes
   - How to handle active states

3. **Component Composition:**
   - How to create reusable layouts
   - How to use children props
   - How to structure React apps

4. **TypeScript:**
   - How to define interfaces
   - How to use generic types
   - How to type async functions

---

## 🚨 Common Mistakes to Avoid

1. **Forgetting async/await:**
   ```typescript
   // ❌ Wrong
   const data = getSearchRequests();
   
   // ✅ Correct
   const data = await getSearchRequests();
   ```

2. **Not handling errors:**
   ```typescript
   // ✅ Always use try-catch
   try {
     const data = await getSearchRequests();
   } catch (error) {
     console.error('Failed to fetch:', error);
   }
   ```

3. **Hardcoding URLs:**
   ```typescript
   // ❌ Wrong
   axios.get('http://localhost:8000/api/search-requests');
   
   // ✅ Correct
   apiClient.get('/api/search-requests');
   ```

4. **Not using TypeScript types:**
   ```typescript
   // ❌ Wrong
   const data: any = await getSearchRequests();
   
   // ✅ Correct
   const data: SearchRequest[] = await getSearchRequests();
   ```

---

## 📚 Additional Resources

- [Axios Documentation](https://axios-http.com/docs/intro)
- [React Router Tutorial](https://reactrouter.com/en/main/start/tutorial)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

---

## ✅ Completion Checklist

- [ ] API client created with interceptors
- [ ] Search request service functions implemented
- [ ] Product service functions implemented
- [ ] React Router configured
- [ ] Three page components created
- [ ] Layout component with navigation
- [ ] Active link styling working
- [ ] Environment variables configured
- [ ] All routes accessible
- [ ] No console errors

---

## 🎯 Next Steps (Day 21-22)

After completing Day 20, you'll be ready to:
- Build form components for creating searches
- Display lists of search requests
- Show product cards
- Add real-time notifications

**Estimated Time:** 4 hours  
**Difficulty:** ⭐⭐☆☆☆ (Beginner-Friendly)

Good luck! 🚀