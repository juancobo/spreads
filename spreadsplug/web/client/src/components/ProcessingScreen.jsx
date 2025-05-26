import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, ProgressBar, Alert, Row, Col, ListGroup } from 'react-bootstrap';
import { useWorkflows } from '../hooks/useWorkflows';
import { useWebSocket } from '../hooks/useWebSocket';

const ProcessingScreen = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { getWorkflow } = useWorkflows();
  const { isConnected, sendMessage, lastMessage } = useWebSocket();
  
  const [workflow, setWorkflow] = useState(null);
  const [processingStatus, setProcessingStatus] = useState({
    stage: 'initializing',
    progress: 0,
    currentStep: '',
    steps: [],
    logs: []
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    loadWorkflow();
  }, [slug]);

  useEffect(() => {
    if (lastMessage) {
      handleWebSocketMessage(lastMessage);
    }
  }, [lastMessage]);

  const loadWorkflow = async () => {
    try {
      const workflowData = await getWorkflow(slug);
      setWorkflow(workflowData);
      
      // Start processing if workflow is ready
      if (workflowData.status === 'captured') {
        startProcessing();
      }
    } catch (err) {
      setError('Failed to load workflow');
      console.error('Error loading workflow:', err);
    }
  };

  const startProcessing = () => {
    sendMessage({
      type: 'start_processing',
      workflow_id: workflow.id
    });
  };

  const handleWebSocketMessage = (message) => {
    const data = JSON.parse(message.data);
    
    switch (data.type) {
      case 'processing_status':
        setProcessingStatus(prev => ({
          ...prev,
          stage: data.stage,
          progress: data.progress,
          currentStep: data.currentStep
        }));
        break;
      
      case 'processing_step':
        setProcessingStatus(prev => ({
          ...prev,
          steps: [...prev.steps, {
            name: data.step,
            status: data.status,
            timestamp: new Date().toISOString(),
            duration: data.duration
          }]
        }));
        break;
      
      case 'processing_log':
        setProcessingStatus(prev => ({
          ...prev,
          logs: [...prev.logs, {
            level: data.level,
            message: data.message,
            timestamp: new Date().toISOString()
          }].slice(-50) // Keep only last 50 log entries
        }));
        break;
      
      case 'processing_complete':
        setProcessingStatus(prev => ({
          ...prev,
          stage: 'completed',
          progress: 100
        }));
        setWorkflow(prev => ({ ...prev, status: 'finished' }));
        break;
      
      case 'processing_error':
        setError(data.message);
        setProcessingStatus(prev => ({
          ...prev,
          stage: 'failed'
        }));
        break;
      
      default:
        break;
    }
  };

  const getStageDescription = (stage) => {
    const descriptions = {
      initializing: 'Initializing processing pipeline...',
      preprocessing: 'Preprocessing captured images...',
      deskewing: 'Correcting page orientation and skew...',
      cropping: 'Detecting and cropping page boundaries...',
      splitting: 'Separating left and right pages...',
      dewarping: 'Correcting page curvature...',
      ocr: 'Performing optical character recognition...',
      postprocessing: 'Applying final image enhancements...',
      output: 'Generating output files...',
      completed: 'Processing completed successfully!',
      failed: 'Processing failed'
    };
    
    return descriptions[stage] || 'Processing...';
  };

  const getStageProgress = (stage) => {
    const stageOrder = [
      'initializing', 'preprocessing', 'deskewing', 'cropping', 
      'splitting', 'dewarping', 'ocr', 'postprocessing', 'output', 'completed'
    ];
    
    const currentIndex = stageOrder.indexOf(stage);
    return currentIndex >= 0 ? (currentIndex / (stageOrder.length - 1)) * 100 : 0;
  };

  const handleCancel = () => {
    sendMessage({
      type: 'cancel_processing',
      workflow_id: workflow.id
    });
    navigate(`/workflow/${slug}`);
  };

  const handleViewResults = () => {
    navigate(`/workflow/${slug}`);
  };

  if (error) {
    return (
      <Alert variant="danger" className="m-4">
        <Alert.Heading>Processing Error</Alert.Heading>
        {error}
        <div className="mt-3">
          <Button variant="outline-danger" onClick={() => navigate(`/workflow/${slug}`)}>
            Back to Workflow
          </Button>
        </div>
      </Alert>
    );
  }

  if (!workflow) {
    return (
      <div className="text-center py-5">
        <div>Loading processing interface...</div>
      </div>
    );
  }

  const overallProgress = Math.max(getStageProgress(processingStatus.stage), processingStatus.progress);

  return (
    <div className="container mt-4">
      <Card>
        <Card.Header>
          <div className="d-flex justify-content-between align-items-center">
            <h4>Processing: {workflow.name}</h4>
            <div className="d-flex gap-2">
              {processingStatus.stage === 'completed' ? (
                <Button variant="success" onClick={handleViewResults}>
                  View Results
                </Button>
              ) : (
                <Button variant="outline-danger" onClick={handleCancel}>
                  Cancel Processing
                </Button>
              )}
            </div>
          </div>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col lg={8}>
              {/* Main Progress */}
              <div className="mb-4">
                <div className="d-flex justify-content-between align-items-center mb-2">
                  <h6>Overall Progress</h6>
                  <span className="text-muted">{Math.round(overallProgress)}%</span>
                </div>
                <ProgressBar 
                  now={overallProgress} 
                  variant={processingStatus.stage === 'failed' ? 'danger' : 'primary'}
                />
                <small className="text-muted mt-1 d-block">
                  {getStageDescription(processingStatus.stage)}
                </small>
              </div>

              {/* Current Step */}
              {processingStatus.currentStep && (
                <div className="mb-4">
                  <h6>Current Step</h6>
                  <div className="border rounded p-3 bg-light">
                    <div className="d-flex align-items-center">
                      <div className="spinner-border spinner-border-sm me-2" role="status">
                        <span className="visually-hidden">Loading...</span>
                      </div>
                      {processingStatus.currentStep}
                    </div>
                  </div>
                </div>
              )}

              {/* Processing Steps */}
              {processingStatus.steps.length > 0 && (
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Processing Steps</h6>
                  </Card.Header>
                  <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    <ListGroup variant="flush">
                      {processingStatus.steps.map((step, index) => (
                        <ListGroup.Item 
                          key={index}
                          className="d-flex justify-content-between align-items-center"
                        >
                          <div>
                            <strong>{step.name}</strong>
                            {step.duration && (
                              <small className="text-muted ms-2">
                                ({step.duration}ms)
                              </small>
                            )}
                          </div>
                          <div className="d-flex align-items-center">
                            <small className="text-muted me-2">
                              {new Date(step.timestamp).toLocaleTimeString()}
                            </small>
                            {step.status === 'completed' ? (
                              <i className="fas fa-check-circle text-success"></i>
                            ) : step.status === 'failed' ? (
                              <i className="fas fa-times-circle text-danger"></i>
                            ) : (
                              <div className="spinner-border spinner-border-sm" role="status">
                                <span className="visually-hidden">Loading...</span>
                              </div>
                            )}
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  </Card.Body>
                </Card>
              )}
            </Col>

            <Col lg={4}>
              {/* Workflow Info */}
              <Card className="mb-3">
                <Card.Header>
                  <h6 className="mb-0">Workflow Info</h6>
                </Card.Header>
                <Card.Body>
                  <div className="mb-2">
                    <strong>Pages:</strong> {workflow.pages?.length || 0}
                  </div>
                  <div className="mb-2">
                    <strong>Status:</strong> {workflow.status}
                  </div>
                  <div className="mb-2">
                    <strong>Connection:</strong>{' '}
                    <span className={`badge ${isConnected ? 'bg-success' : 'bg-danger'}`}>
                      {isConnected ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </Card.Body>
              </Card>

              {/* Recent Logs */}
              {processingStatus.logs.length > 0 && (
                <Card>
                  <Card.Header>
                    <h6 className="mb-0">Processing Logs</h6>
                  </Card.Header>
                  <Card.Body style={{ maxHeight: '250px', overflowY: 'auto' }}>
                    {processingStatus.logs.slice(-10).map((log, index) => (
                      <div 
                        key={index} 
                        className={`small mb-1 ${
                          log.level === 'ERROR' ? 'text-danger' : 
                          log.level === 'WARNING' ? 'text-warning' : 
                          'text-muted'
                        }`}
                      >
                        <span className="font-monospace">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                        {' '}
                        {log.message}
                      </div>
                    ))}
                  </Card.Body>
                </Card>
              )}
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </div>
  );
};

export default ProcessingScreen;
