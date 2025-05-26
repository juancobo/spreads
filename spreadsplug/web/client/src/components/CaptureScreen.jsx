import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Row, Col, Alert, Badge, Modal, ProgressBar } from 'react-bootstrap';
import { useWorkflows } from '../hooks/useWorkflows';
import { useWebSocket } from '../hooks/useWebSocket';

const CaptureScreen = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { getWorkflow, updateWorkflow } = useWorkflows();
  const { isConnected, sendMessage, lastMessage } = useWebSocket();
  
  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [capturing, setCapturing] = useState(false);
  const [captureStatus, setCaptureStatus] = useState('idle'); // idle, preparing, ready, capturing
  const [currentPage, setCurrentPage] = useState(0);
  const [previewImages, setPreviewImages] = useState({ odd: null, even: null });
  const [showHelpModal, setShowHelpModal] = useState(false);

  useEffect(() => {
    loadWorkflow();
  }, [slug]);

  useEffect(() => {
    // Handle WebSocket messages for capture updates
    if (lastMessage) {
      handleWebSocketMessage(lastMessage);
    }
  }, [lastMessage]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return; // Don't capture when typing in form fields
      }

      switch (event.key) {
        case ' ': // Space bar
          event.preventDefault();
          handleCapture();
          break;
        case 'r':
        case 'R':
          event.preventDefault();
          handleRetake();
          break;
        case 'f':
        case 'F':
          event.preventDefault();
          handleFinish();
          break;
        case '?':
          event.preventDefault();
          setShowHelpModal(true);
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [captureStatus]);

  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const workflowData = await getWorkflow(slug);
      setWorkflow(workflowData);
      setCurrentPage(workflowData.pages?.length || 0);
    } catch (err) {
      setError('Failed to load workflow');
      console.error('Error loading workflow:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleWebSocketMessage = (message) => {
    const data = JSON.parse(message.data);
    
    switch (data.type) {
      case 'capture_status':
        setCaptureStatus(data.status);
        break;
      case 'capture_complete':
        handleCaptureComplete(data);
        break;
      case 'preview_update':
        setPreviewImages(data.images);
        break;
      case 'error':
        setError(data.message);
        setCapturing(false);
        break;
      default:
        break;
    }
  };

  const handleCaptureComplete = (data) => {
    setCapturing(false);
    setCurrentPage(prev => prev + 1);
    
    // Update workflow with new page
    setWorkflow(prev => ({
      ...prev,
      pages: [...(prev.pages || []), {
        id: data.pageId,
        sequence: currentPage + 1,
        captured: true,
        images: data.images,
        timestamp: new Date().toISOString()
      }]
    }));
  };

  const handleCapture = async () => {
    if (capturing || captureStatus !== 'ready') return;

    try {
      setCapturing(true);
      setError(null);
      
      // Send capture command via WebSocket
      sendMessage({
        type: 'capture',
        workflow_id: workflow.id,
        page_number: currentPage + 1
      });
    } catch (err) {
      setError('Failed to start capture');
      setCapturing(false);
    }
  };

  const handleRetake = async () => {
    if (currentPage === 0) return;

    try {
      setCurrentPage(prev => prev - 1);
      
      // Remove last page from workflow
      setWorkflow(prev => ({
        ...prev,
        pages: prev.pages?.slice(0, -1) || []
      }));
    } catch (err) {
      setError('Failed to retake page');
    }
  };

  const handleFinish = async () => {
    try {
      await updateWorkflow(workflow.id, { 
        status: 'captured',
        pages: workflow.pages
      });
      navigate(`/workflow/${slug}`);
    } catch (err) {
      setError('Failed to finish capture session');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'success';
      case 'preparing': return 'warning';
      case 'capturing': return 'primary';
      default: return 'secondary';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-5">
        <div>Loading capture interface...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="m-4">
        <Alert.Heading>Error</Alert.Heading>
        {error}
        <div className="mt-3">
          <Button variant="outline-danger" onClick={() => navigate(`/workflow/${slug}`)}>
            Back to Workflow
          </Button>
        </div>
      </Alert>
    );
  }

  const progress = workflow.pages ? (workflow.pages.length / (workflow.expectedPages || 100)) * 100 : 0;

  return (
    <div className="container-fluid mt-3">
      {/* Header */}
      <Row className="mb-3">
        <Col>
          <Card>
            <Card.Body>
              <Row className="align-items-center">
                <Col>
                  <h4 className="mb-0">Capturing: {workflow.name}</h4>
                  <small className="text-muted">Page {currentPage + 1}</small>
                </Col>
                <Col xs="auto">
                  <Badge bg={getStatusColor(captureStatus)} className="me-2">
                    {captureStatus.toUpperCase()}
                  </Badge>
                  <Badge bg={isConnected ? 'success' : 'danger'}>
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </Badge>
                </Col>
                <Col xs="auto">
                  <Button 
                    variant="outline-secondary" 
                    size="sm" 
                    onClick={() => setShowHelpModal(true)}
                  >
                    Help (?)
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Main capture area */}
      <Row>
        <Col lg={8}>
          <Card className="mb-3">
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">Live Preview</h5>
                <div>
                  <Button
                    variant="primary"
                    onClick={handleCapture}
                    disabled={capturing || captureStatus !== 'ready'}
                    className="me-2"
                  >
                    {capturing ? 'Capturing...' : 'Capture (Space)'}
                  </Button>
                  <Button
                    variant="warning"
                    onClick={handleRetake}
                    disabled={currentPage === 0 || capturing}
                    className="me-2"
                  >
                    Retake (R)
                  </Button>
                  <Button
                    variant="success"
                    onClick={handleFinish}
                    disabled={capturing || currentPage === 0}
                  >
                    Finish (F)
                  </Button>
                </div>
              </div>
            </Card.Header>
            <Card.Body>
              <div style={{ minHeight: '400px', backgroundColor: '#f8f9fa' }} className="d-flex align-items-center justify-content-center border rounded">
                {previewImages.odd || previewImages.even ? (
                  <Row>
                    {previewImages.odd && (
                      <Col md={6}>
                        <img 
                          src={previewImages.odd} 
                          alt="Odd page preview" 
                          className="img-fluid border"
                        />
                        <div className="text-center mt-2">
                          <small className="text-muted">Odd Page</small>
                        </div>
                      </Col>
                    )}
                    {previewImages.even && (
                      <Col md={6}>
                        <img 
                          src={previewImages.even} 
                          alt="Even page preview" 
                          className="img-fluid border"
                        />
                        <div className="text-center mt-2">
                          <small className="text-muted">Even Page</small>
                        </div>
                      </Col>
                    )}
                  </Row>
                ) : (
                  <div className="text-center text-muted">
                    <i className="fas fa-camera fa-3x mb-3"></i>
                    <div>Camera preview will appear here</div>
                    <small>Make sure your capture device is connected</small>
                  </div>
                )}
              </div>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* Progress */}
          <Card className="mb-3">
            <Card.Header>
              <h6 className="mb-0">Progress</h6>
            </Card.Header>
            <Card.Body>
              <div className="mb-2">
                <strong>Pages captured: {workflow.pages?.length || 0}</strong>
              </div>
              {workflow.expectedPages && (
                <ProgressBar 
                  now={progress} 
                  label={`${Math.round(progress)}%`}
                  className="mb-2"
                />
              )}
            </Card.Body>
          </Card>

          {/* Recent pages */}
          {workflow.pages && workflow.pages.length > 0 && (
            <Card>
              <Card.Header>
                <h6 className="mb-0">Recent Pages</h6>
              </Card.Header>
              <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                {workflow.pages.slice(-5).reverse().map((page, index) => (
                  <div key={page.id} className="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                    <span>Page {page.sequence}</span>
                    <small className="text-muted">
                      {new Date(page.timestamp).toLocaleTimeString()}
                    </small>
                  </div>
                ))}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Help Modal */}
      <Modal show={showHelpModal} onHide={() => setShowHelpModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Keyboard Shortcuts</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <div className="mb-3">
            <strong>Space Bar:</strong> Capture current page
          </div>
          <div className="mb-3">
            <strong>R:</strong> Retake last page
          </div>
          <div className="mb-3">
            <strong>F:</strong> Finish capture session
          </div>
          <div className="mb-3">
            <strong>?:</strong> Show this help dialog
          </div>
          <hr />
          <div className="text-muted">
            <small>
              Position your book pages in the camera view and press Space to capture. 
              The system will automatically detect both pages if using a dual-camera setup.
            </small>
          </div>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowHelpModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default CaptureScreen;
