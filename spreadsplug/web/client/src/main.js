/*
 * Copyright (C) 2014 Johannes Baiter <johannes.baiter@gmail.com>
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.

 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import SpreadsApp from './components/SpreadsApp.jsx';

// Load stylesheets
import '../scss/app.scss';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/css/all.min.css';

// Initialize the React application
const container = document.getElementById('spreads-app');
const root = createRoot(container);

root.render(
  <BrowserRouter>
    <SpreadsApp />
  </BrowserRouter>
);

// Handle browser navigation
window.addEventListener('popstate', () => {
  // Modern browser history handling is handled by React Router
});

// Intercept default form submission
document.addEventListener('submit', (e) => {
  if (e.target.tagName === 'FORM' && !e.target.dataset.allowDefault) {
    e.preventDefault();
  }
});
