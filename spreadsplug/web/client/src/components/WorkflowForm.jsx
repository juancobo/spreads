import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Form, Alert, Spinner } from 'react-bootstrap';
import MetadataEditor from './MetadataEditor';
import ConfigurationEditor from './ConfigurationEditor';

const WorkflowForm = ({ workflow, isNew = false, globalConfig }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: workflow?.name || '',
    metadata: workflow?.metadata || {},
    config: workflow?.config || {}
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (workflow) {
      setFormData({
        name: workflow.name || '',
        metadata: workflow.metadata || {},
        config: workflow.config || {}
      });
    }
  }, [workflow]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Workflow name is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const workflowData = {
        ...formData,
        id: workflow?.id,
        slug: workflow?.slug || formData.name.toLowerCase().replace(/\s+/g, '-')
      };

      const url = isNew ? '/api/workflow' : `/api/workflow/${workflow.id}`;
      const method = isNew ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        setErrors(errorData.errors || { general: 'Failed to save workflow' });
        return;
      }

      const savedWorkflow = await response.json();
      
      // Navigate to capture screen for new workflows, or back to list for edits
      if (isNew) {
        navigate(`/workflow/${savedWorkflow.slug}/capture`);
      } else {
        navigate('/');
      }
    } catch (error) {
      console.error('Error saving workflow:', error);
      setErrors({ general: 'Network error occurred while saving workflow' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  return (
    <div className="container mt-4">
      <Card>
        <Card.Header>
          <h3>{isNew ? 'Create New Workflow' : 'Edit Workflow'}</h3>
        </Card.Header>
        <Card.Body>
          {errors.general && (
            <Alert variant="danger" className="mb-3">
              {errors.general}
            </Alert>
          )}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Workflow Name *</Form.Label>
              <Form.Control
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter workflow name"
                isInvalid={!!errors.name}
                disabled={isSubmitting}
              />
              <Form.Control.Feedback type="invalid">
                {errors.name}
              </Form.Control.Feedback>
            </Form.Group>

            <div className="mb-4">
              <h5>Metadata</h5>
              <MetadataEditor
                metadata={formData.metadata}
                onChange={(metadata) => handleInputChange('metadata', metadata)}
                errors={errors.metadata}
              />
            </div>

            <div className="mb-4">
              <h5>Configuration</h5>
              <ConfigurationEditor
                config={formData.config}
                globalConfig={globalConfig}
                onChange={(config) => handleInputChange('config', config)}
                errors={errors.config}
              />
            </div>

            <div className="d-flex gap-2">
              <Button
                type="submit"
                variant="primary"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      aria-hidden="true"
                      className="me-2"
                    />
                    Saving...
                  </>
                ) : (
                  isNew ? 'Create Workflow' : 'Save Changes'
                )}
              </Button>
              
              <Button
                type="button"
                variant="secondary"
                onClick={handleCancel}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

export default WorkflowForm;
