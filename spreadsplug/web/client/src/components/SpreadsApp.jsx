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

import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import NavigationBar from './NavigationBar';
import WorkflowList from './WorkflowList';
import WorkflowDetails from './WorkflowDetails';
import WorkflowForm from './WorkflowForm';
import CaptureScreen from './CaptureScreen';
import MetadataEditor from './MetadataEditor';
import ConfigurationEditor from './ConfigurationEditor';
import { useWorkflows } from '../hooks/useWorkflows';
import { useConfiguration } from '../hooks/useConfiguration';
import { useWebSocket } from '../hooks/useWebSocket';

/**
 * Core application component.
 *
 * Handles routing, state management, and error messages.
 */
function SpreadsApp() {
  const [errorMessage, setErrorMessage] = useState('');
  const [infoMessage, setInfoMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  
  const { workflows, selectedWorkflow, loading: workflowsLoading } = useWorkflows();
  const { configuration, loading: configLoading } = useConfiguration();
  const { connected, lastMessage } = useWebSocket();

  // Handle WebSocket messages for notifications
  useEffect(() => {
    if (lastMessage) {
      const data = JSON.parse(lastMessage.data);
      if (data.type === 'log' && ['WARNING', 'ERROR'].includes(data.level)) {
        setErrorMessage(data.message);
        setTimeout(() => setErrorMessage(''), 5000);
      } else if (data.type === 'notification') {
        setInfoMessage(data.message);
        setTimeout(() => setInfoMessage(''), 3000);
      }
    }
  }, [lastMessage]);

  const handleError = useCallback((error) => {
    console.error('Application error:', error);
    setErrorMessage(error.message || 'An unexpected error occurred');
    setTimeout(() => setErrorMessage(''), 5000);
  }, []);

  const handleSuccess = useCallback((message) => {
    setInfoMessage(message);
    setTimeout(() => setInfoMessage(''), 3000);
  }, []);

  const isAppLoading = workflowsLoading || configLoading || isLoading;

  return (
    <div className="spreads-app">
      <NavigationBar 
        workflows={workflows}
        selectedWorkflow={selectedWorkflow}
        configuration={configuration}
        connected={connected}
        onError={handleError}
      />
      
      <main className="container-fluid">
        {/* Error/Info Messages */}
        {errorMessage && (
          <div className="alert alert-danger alert-dismissible fade show" role="alert">
            <i className="fas fa-exclamation-triangle me-2"></i>
            {errorMessage}
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => setErrorMessage('')}
              aria-label="Close"
            ></button>
          </div>
        )}
        
        {infoMessage && (
          <div className="alert alert-info alert-dismissible fade show" role="alert">
            <i className="fas fa-info-circle me-2"></i>
            {infoMessage}
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => setInfoMessage('')}
              aria-label="Close"
            ></button>
          </div>
        )}

        {/* Loading Indicator */}
        {isAppLoading && (
          <div className="d-flex justify-content-center my-4">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}

        {/* Route Components */}
        <Routes>
          <Route 
            path="/" 
            element={
              <WorkflowList 
                workflows={workflows}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/workflow/new" 
            element={
              <WorkflowForm 
                isNew={true}
                globalConfig={configuration}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/workflow/:slug" 
            element={
              <WorkflowDetails 
                workflows={workflows}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/workflow/:slug/edit" 
            element={
              <WorkflowForm 
                isNew={false}
                globalConfig={configuration}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/workflow/:slug/capture" 
            element={
              <CaptureScreen 
                workflows={workflows}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/workflow/:id/submit" 
            element={
              <SubmissionForm 
                workflows={workflows}
                configuration={configuration}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/preferences" 
            element={
              <Preferences 
                configuration={configuration}
                onError={handleError}
                onSuccess={handleSuccess}
              />
            } 
          />
          <Route 
            path="/logs" 
            element={
              <LogDisplay 
                onError={handleError}
              />
            } 
          />
        </Routes>
      </main>
    </div>
  );
}

export default SpreadsApp;
