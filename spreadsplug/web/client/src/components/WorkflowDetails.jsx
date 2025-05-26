import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Badge, Row, Col, Spinner, Alert, ProgressBar, Modal } from 'react-bootstrap';
import { useWorkflows } from '../hooks/useWorkflows';

const WorkflowDetails = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { getWorkflow, deleteWorkflow, updateWorkflow } = useWorkflows();
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadWorkflow();
  }, [slug]);

  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const workflowData = await getWorkflow(slug);
      setWorkflow(workflowData);
    } catch (err) {
      setError('Failed to load workflow details');
      console.error('Error loading workflow:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    navigate(`/workflow/${slug}/edit`);
  };

  const handleCapture = () => {
    navigate(`/workflow/${slug}/capture`);
  };

  const handleProcess = async () => {
    try {
      await updateWorkflow(workflow.id, { status: 'processing' });
      // In a real app, this would trigger the processing workflow
      setWorkflow(prev => ({ ...prev, status: 'processing' }));
    } catch (err) {
      setError('Failed to start processing');
    }
  };

  const handleDelete = async () => {
    try {
      setDeleting(true);
      await deleteWorkflow(workflow.id);
      navigate('/');
    } catch (err) {
      setError('Failed to delete workflow');
      setDeleting(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      new: 'secondary',
      capturing: 'primary',
      captured: 'info',
      processing: 'warning',
      finished: 'success',
      failed: 'danger'
    };
    
    return (
      <Badge bg={variants[status] || 'secondary'}>
        {status?.toUpperCase() || 'UNKNOWN'}
      </Badge>
    );
  };

  const getProgressInfo = (workflow) => {
    if (!workflow.pages) return { progress: 0, text: 'No pages captured' };
    
    const capturedPages = workflow.pages.filter(page => page.captured).length;
    const totalPages = workflow.pages.length;
    const progress = totalPages > 0 ? (capturedPages / totalPages) * 100 : 0;
    
    return {
      progress,
      text: `${capturedPages} of ${totalPages} pages captured`
    };
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <div className="mt-2">Loading workflow details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="m-4">
        <Alert.Heading>Error</Alert.Heading>
        {error}
        <div className="mt-3">
          <Button variant="outline-danger" onClick={() => navigate('/')}>
            Back to Workflows
          </Button>
        </div>
      </Alert>
    );
  }

  if (!workflow) {
    return (
      <Alert variant="warning" className="m-4">
        <Alert.Heading>Workflow Not Found</Alert.Heading>
        The requested workflow could not be found.
        <div className="mt-3">
          <Button variant="outline-warning" onClick={() => navigate('/')}>
            Back to Workflows
          </Button>
        </div>
      </Alert>
    );
  }

  const progressInfo = getProgressInfo(workflow);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>{workflow.name}</h2>
        <div className="d-flex gap-2">
          <Button variant="outline-secondary" onClick={() => navigate('/')}>
            Back to List
          </Button>
          <Button variant="primary" onClick={handleEdit}>
            Edit
          </Button>
          <Button variant="success" onClick={handleCapture}>
            Capture
          </Button>
          {workflow.status === 'captured' && (
            <Button variant="warning" onClick={handleProcess}>
              Process
            </Button>
          )}
          <Button variant="outline-danger" onClick={() => setShowDeleteModal(true)}>
            Delete
          </Button>
        </div>
      </div>

      <Row>
        <Col md={8}>
          <Card className="mb-4">
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Workflow Information</h5>
                {getStatusBadge(workflow.status)}
              </div>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col sm={3}><strong>Slug:</strong></Col>
                <Col sm={9}>{workflow.slug}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={3}><strong>Created:</strong></Col>
                <Col sm={9}>{new Date(workflow.created).toLocaleString()}</Col>
              </Row>
              <Row className="mt-2">
                <Col sm={3}><strong>Last Modified:</strong></Col>
                <Col sm={9}>{new Date(workflow.modified).toLocaleString()}</Col>
              </Row>
              {workflow.path && (
                <Row className="mt-2">
                  <Col sm={3}><strong>Path:</strong></Col>
                  <Col sm={9}><code>{workflow.path}</code></Col>
                </Row>
              )}
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Progress</h5>
            </Card.Header>
            <Card.Body>
              <ProgressBar 
                now={progressInfo.progress} 
                label={`${Math.round(progressInfo.progress)}%`}
                className="mb-2"
              />
              <div className="text-muted">{progressInfo.text}</div>
            </Card.Body>
          </Card>

          {workflow.metadata && Object.keys(workflow.metadata).length > 0 && (
            <Card className="mb-4">
              <Card.Header>
                <h5 className="mb-0">Metadata</h5>
              </Card.Header>
              <Card.Body>
                {Object.entries(workflow.metadata).map(([key, value]) => (
                  <Row key={key} className="mb-2">
                    <Col sm={3}>
                      <strong>{key.charAt(0).toUpperCase() + key.slice(1)}:</strong>
                    </Col>
                    <Col sm={9}>{value}</Col>
                  </Row>
                ))}
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col md={4}>
          {workflow.pages && workflow.pages.length > 0 && (
            <Card>
              <Card.Header>
                <h5 className="mb-0">Pages ({workflow.pages.length})</h5>
              </Card.Header>
              <Card.Body style={{ maxHeight: '400px', overflowY: 'auto' }}>
                {workflow.pages.map((page, index) => (
                  <div key={page.id || index} className="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    <span>Page {index + 1}</span>
                    <Badge bg={page.captured ? 'success' : 'secondary'}>
                      {page.captured ? 'Captured' : 'Pending'}
                    </Badge>
                  </div>
                ))}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          Are you sure you want to delete the workflow "{workflow.name}"? This action cannot be undone.
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="danger" 
            onClick={handleDelete}
            disabled={deleting}
          >
            {deleting ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                  className="me-2"
                />
                Deleting...
              </>
            ) : (
              'Delete Workflow'
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default WorkflowDetails;
