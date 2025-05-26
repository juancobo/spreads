import React, { useState, useEffect } from 'react';
import { Form, Card, Row, Col, Accordion, Alert } from 'react-bootstrap';

const ConfigurationEditor = ({ config = {}, globalConfig = {}, onChange, errors = {} }) => {
  const [configState, setConfigState] = useState({});

  useEffect(() => {
    // Initialize configuration state with global defaults and current values
    const initialState = { ...globalConfig, ...config };
    setConfigState(initialState);
  }, [config, globalConfig]);

  const handleConfigChange = (section, key, value) => {
    const newConfig = {
      ...configState,
      [section]: {
        ...configState[section],
        [key]: value
      }
    };
    setConfigState(newConfig);
    onChange(newConfig);
  };

  const renderConfigField = (section, key, fieldConfig, value) => {
    const fieldKey = `${section}.${key}`;
    const isInvalid = errors[fieldKey];

    switch (fieldConfig.type) {
      case 'boolean':
        return (
          <Form.Check
            type="checkbox"
            id={fieldKey}
            label={fieldConfig.description || key}
            checked={!!value}
            onChange={(e) => handleConfigChange(section, key, e.target.checked)}
            isInvalid={isInvalid}
          />
        );

      case 'integer':
      case 'float':
        return (
          <Form.Group>
            <Form.Label>{fieldConfig.description || key}</Form.Label>
            <Form.Control
              type="number"
              step={fieldConfig.type === 'float' ? 'any' : '1'}
              value={value || ''}
              onChange={(e) => {
                const val = fieldConfig.type === 'integer' 
                  ? parseInt(e.target.value, 10) 
                  : parseFloat(e.target.value);
                handleConfigChange(section, key, isNaN(val) ? null : val);
              }}
              min={fieldConfig.min}
              max={fieldConfig.max}
              isInvalid={isInvalid}
            />
            {fieldConfig.help && (
              <Form.Text className="text-muted">{fieldConfig.help}</Form.Text>
            )}
            {isInvalid && (
              <Form.Control.Feedback type="invalid">
                {errors[fieldKey]}
              </Form.Control.Feedback>
            )}
          </Form.Group>
        );

      case 'string':
        return (
          <Form.Group>
            <Form.Label>{fieldConfig.description || key}</Form.Label>
            <Form.Control
              type="text"
              value={value || ''}
              onChange={(e) => handleConfigChange(section, key, e.target.value)}
              placeholder={fieldConfig.placeholder}
              isInvalid={isInvalid}
            />
            {fieldConfig.help && (
              <Form.Text className="text-muted">{fieldConfig.help}</Form.Text>
            )}
            {isInvalid && (
              <Form.Control.Feedback type="invalid">
                {errors[fieldKey]}
              </Form.Control.Feedback>
            )}
          </Form.Group>
        );

      case 'select':
        return (
          <Form.Group>
            <Form.Label>{fieldConfig.description || key}</Form.Label>
            <Form.Select
              value={value || ''}
              onChange={(e) => handleConfigChange(section, key, e.target.value)}
              isInvalid={isInvalid}
            >
              <option value="">Select an option...</option>
              {fieldConfig.options?.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label || option.value}
                </option>
              ))}
            </Form.Select>
            {fieldConfig.help && (
              <Form.Text className="text-muted">{fieldConfig.help}</Form.Text>
            )}
            {isInvalid && (
              <Form.Control.Feedback type="invalid">
                {errors[fieldKey]}
              </Form.Control.Feedback>
            )}
          </Form.Group>
        );

      case 'path':
        return (
          <Form.Group>
            <Form.Label>{fieldConfig.description || key}</Form.Label>
            <Form.Control
              type="text"
              value={value || ''}
              onChange={(e) => handleConfigChange(section, key, e.target.value)}
              placeholder="Enter file path..."
              isInvalid={isInvalid}
            />
            {fieldConfig.help && (
              <Form.Text className="text-muted">{fieldConfig.help}</Form.Text>
            )}
            {isInvalid && (
              <Form.Control.Feedback type="invalid">
                {errors[fieldKey]}
              </Form.Control.Feedback>
            )}
          </Form.Group>
        );

      default:
        return (
          <Form.Group>
            <Form.Label>{fieldConfig.description || key}</Form.Label>
            <Form.Control
              type="text"
              value={value || ''}
              onChange={(e) => handleConfigChange(section, key, e.target.value)}
              isInvalid={isInvalid}
            />
            {isInvalid && (
              <Form.Control.Feedback type="invalid">
                {errors[fieldKey]}
              </Form.Control.Feedback>
            )}
          </Form.Group>
        );
    }
  };

  const renderConfigSection = (sectionName, sectionConfig) => {
    const sectionValues = configState[sectionName] || {};
    
    return (
      <Card key={sectionName} className="mb-3">
        <Card.Header>
          <h6 className="mb-0">{sectionConfig.description || sectionName}</h6>
        </Card.Header>
        <Card.Body>
          <Row>
            {Object.entries(sectionConfig.fields || {}).map(([fieldKey, fieldConfig]) => (
              <Col md={6} key={fieldKey} className="mb-3">
                {renderConfigField(sectionName, fieldKey, fieldConfig, sectionValues[fieldKey])}
              </Col>
            ))}
          </Row>
        </Card.Body>
      </Card>
    );
  };

  // Default configuration structure if globalConfig is empty
  const defaultSections = {
    capture: {
      description: 'Capture Settings',
      fields: {
        device: {
          type: 'select',
          description: 'Camera Device',
          options: [
            { value: 'dummy', label: 'Dummy Device (Testing)' },
            { value: 'gphoto2', label: 'gPhoto2 Compatible Camera' },
            { value: 'chdkcamera', label: 'CHDK Camera' }
          ],
          help: 'Select the camera device to use for capturing'
        },
        resolution: {
          type: 'string',
          description: 'Image Resolution',
          placeholder: '2592x1944',
          help: 'Resolution in WIDTHxHEIGHT format'
        },
        iso: {
          type: 'integer',
          description: 'ISO Setting',
          min: 100,
          max: 6400,
          help: 'Camera ISO sensitivity'
        }
      }
    },
    processing: {
      description: 'Processing Settings',
      fields: {
        autopilot: {
          type: 'boolean',
          description: 'Enable Autopilot',
          help: 'Automatically process images after capture'
        },
        dpi: {
          type: 'integer',
          description: 'Target DPI',
          min: 150,
          max: 600,
          help: 'Target DPI for processed images'
        },
        format: {
          type: 'select',
          description: 'Output Format',
          options: [
            { value: 'pdf', label: 'PDF' },
            { value: 'djvu', label: 'DjVu' },
            { value: 'images', label: 'Images Only' }
          ]
        }
      }
    },
    plugins: {
      description: 'Plugin Settings',
      fields: {
        autorotate: {
          type: 'boolean',
          description: 'Auto-rotate Images',
          help: 'Automatically detect and correct image rotation'
        },
        tesseract: {
          type: 'boolean',
          description: 'OCR Processing',
          help: 'Enable optical character recognition'
        },
        scantailor: {
          type: 'boolean',
          description: 'ScanTailor Processing',
          help: 'Enable advanced image processing with ScanTailor'
        }
      }
    }
  };

  const sectionsToRender = Object.keys(globalConfig).length > 0 
    ? globalConfig 
    : defaultSections;

  return (
    <div>
      {errors.general && (
        <Alert variant="warning" className="mb-3">
          {errors.general}
        </Alert>
      )}
      
      {Object.entries(sectionsToRender).map(([sectionName, sectionConfig]) =>
        renderConfigSection(sectionName, sectionConfig)
      )}
    </div>
  );
};

export default ConfigurationEditor;
