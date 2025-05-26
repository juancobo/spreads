import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWorkflows } from '../hooks/useWorkflows';

/**
 * Modern workflow list component
 */
function WorkflowList({ onError, onSuccess }) {
  const { workflows, loading, deleteWorkflow } = useWorkflows();
  const [sortBy, setSortBy] = useState('created');
  const [sortOrder, setSortOrder] = useState('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedWorkflows, setSelectedWorkflows] = useState(new Set());

  // Filter and sort workflows
  const filteredWorkflows = workflows
    .filter(workflow => 
      workflow.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      workflow.metadata?.title?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];
      
      if (sortBy === 'created' || sortBy === 'modified') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }
      
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedWorkflows(new Set(workflows.map(w => w.id)));
    } else {
      setSelectedWorkflows(new Set());
    }
  };

  const handleSelectWorkflow = (workflowId, checked) => {
    const newSelection = new Set(selectedWorkflows);
    if (checked) {
      newSelection.add(workflowId);
    } else {
      newSelection.delete(workflowId);
    }
    setSelectedWorkflows(newSelection);
  };

  const handleDelete = async (workflowId) => {
    if (window.confirm('Are you sure you want to delete this workflow?')) {
      try {
        await deleteWorkflow(workflowId);
        onSuccess?.('Workflow deleted successfully');
        setSelectedWorkflows(prev => {
          const newSelection = new Set(prev);
          newSelection.delete(workflowId);
          return newSelection;
        });
      } catch (error) {
        onError?.(error);
      }
    }
  };

  const handleBulkDelete = async () => {
    if (selectedWorkflows.size === 0) return;
    
    if (window.confirm(`Are you sure you want to delete ${selectedWorkflows.size} workflows?`)) {
      try {
        const promises = Array.from(selectedWorkflows).map(id => deleteWorkflow(id));
        await Promise.all(promises);
        onSuccess?.(`${selectedWorkflows.size} workflows deleted successfully`);
        setSelectedWorkflows(new Set());
      } catch (error) {
        onError?.(error);
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'new': { class: 'bg-secondary', icon: 'fa-circle' },
      'capture': { class: 'bg-primary', icon: 'fa-camera' },
      'processing': { class: 'bg-warning', icon: 'fa-cog' },
      'done': { class: 'bg-success', icon: 'fa-check' },
      'error': { class: 'bg-danger', icon: 'fa-exclamation-triangle' }
    };
    
    const config = statusConfig[status] || statusConfig['new'];
    return (
      <span className={`badge ${config.class}`}>
        <i className={`fas ${config.icon} me-1`}></i>
        {status}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center my-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading workflows...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-list">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3">
          <i className="fas fa-list me-2"></i>
          Workflows
        </h1>
        <Link to="/workflow/new" className="btn btn-primary">
          <i className="fas fa-plus me-2"></i>
          New Workflow
        </Link>
      </div>

      {/* Search and Controls */}
      <div className="row mb-3">
        <div className="col-md-6">
          <div className="input-group">
            <span className="input-group-text">
              <i className="fas fa-search"></i>
            </span>
            <input
              type="text"
              className="form-control"
              placeholder="Search workflows..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <div className="col-md-6 text-end">
          {selectedWorkflows.size > 0 && (
            <button 
              className="btn btn-outline-danger"
              onClick={handleBulkDelete}
            >
              <i className="fas fa-trash me-2"></i>
              Delete Selected ({selectedWorkflows.size})
            </button>
          )}
        </div>
      </div>

      {/* Workflows Table */}
      {filteredWorkflows.length === 0 ? (
        <div className="text-center py-5">
          <i className="fas fa-folder-open fa-3x text-muted mb-3"></i>
          <h5 className="text-muted">No workflows found</h5>
          <p className="text-muted">
            {searchTerm ? 'Try adjusting your search terms.' : 'Create your first workflow to get started.'}
          </p>
        </div>
      ) : (
        <div className="table-responsive">
          <table className="table table-hover">
            <thead className="table-light">
              <tr>
                <th>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    checked={selectedWorkflows.size === workflows.length && workflows.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                </th>
                <th 
                  className="sortable" 
                  onClick={() => handleSort('name')}
                  style={{ cursor: 'pointer' }}
                >
                  Name
                  {sortBy === 'name' && (
                    <i className={`fas fa-sort-${sortOrder === 'asc' ? 'up' : 'down'} ms-1`}></i>
                  )}
                </th>
                <th>Status</th>
                <th>Pages</th>
                <th 
                  className="sortable" 
                  onClick={() => handleSort('created')}
                  style={{ cursor: 'pointer' }}
                >
                  Created
                  {sortBy === 'created' && (
                    <i className={`fas fa-sort-${sortOrder === 'asc' ? 'up' : 'down'} ms-1`}></i>
                  )}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredWorkflows.map(workflow => (
                <tr key={workflow.id}>
                  <td>
                    <input
                      type="checkbox"
                      className="form-check-input"
                      checked={selectedWorkflows.has(workflow.id)}
                      onChange={(e) => handleSelectWorkflow(workflow.id, e.target.checked)}
                    />
                  </td>
                  <td>
                    <Link 
                      to={`/workflow/${workflow.id}`}
                      className="text-decoration-none fw-medium"
                    >
                      {workflow.name}
                    </Link>
                    {workflow.metadata?.title && (
                      <div className="text-muted small">{workflow.metadata.title}</div>
                    )}
                  </td>
                  <td>{getStatusBadge(workflow.status)}</td>
                  <td>
                    {workflow.pages ? workflow.pages.length : 0}
                  </td>
                  <td className="text-muted small">
                    {formatDate(workflow.created)}
                  </td>
                  <td>
                    <div className="btn-group btn-group-sm">
                      <Link 
                        to={`/workflow/${workflow.id}`}
                        className="btn btn-outline-primary"
                        title="View Details"
                      >
                        <i className="fas fa-eye"></i>
                      </Link>
                      <Link 
                        to={`/workflow/${workflow.id}/capture`}
                        className="btn btn-outline-secondary"
                        title="Capture"
                      >
                        <i className="fas fa-camera"></i>
                      </Link>
                      <button 
                        className="btn btn-outline-danger"
                        onClick={() => handleDelete(workflow.id)}
                        title="Delete"
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default WorkflowList;
