import React, { useState } from 'react';
import { Form, Button, Row, Col, Card } from 'react-bootstrap';

const MetadataEditor = ({ metadata = {}, onChange, errors = {} }) => {
  const [fields, setFields] = useState(() => {
    // Initialize with existing metadata or default fields
    const defaultFields = [
      { key: 'title', label: 'Title', type: 'text', required: true },
      { key: 'author', label: 'Author', type: 'text', required: false },
      { key: 'publisher', label: 'Publisher', type: 'text', required: false },
      { key: 'year', label: 'Publication Year', type: 'number', required: false },
      { key: 'isbn', label: 'ISBN', type: 'text', required: false },
      { key: 'description', label: 'Description', type: 'textarea', required: false }
    ];

    // Merge with existing metadata
    const existingKeys = Object.keys(metadata);
    const mergedFields = defaultFields.map(field => ({
      ...field,
      value: metadata[field.key] || ''
    }));

    // Add any custom fields from existing metadata
    existingKeys.forEach(key => {
      if (!defaultFields.find(field => field.key === key)) {
        mergedFields.push({
          key,
          label: key.charAt(0).toUpperCase() + key.slice(1),
          type: 'text',
          required: false,
          value: metadata[key] || '',
          isCustom: true
        });
      }
    });

    return mergedFields;
  });

  const handleFieldChange = (fieldKey, value) => {
    const updatedFields = fields.map(field =>
      field.key === fieldKey ? { ...field, value } : field
    );
    setFields(updatedFields);

    // Create metadata object from fields
    const newMetadata = {};
    updatedFields.forEach(field => {
      if (field.value) {
        newMetadata[field.key] = field.value;
      }
    });

    onChange(newMetadata);
  };

  const addCustomField = () => {
    const newKey = prompt('Enter field name:');
    if (newKey && !fields.find(field => field.key === newKey)) {
      const newField = {
        key: newKey,
        label: newKey.charAt(0).toUpperCase() + newKey.slice(1),
        type: 'text',
        required: false,
        value: '',
        isCustom: true
      };
      setFields(prev => [...prev, newField]);
    }
  };

  const removeCustomField = (fieldKey) => {
    const updatedFields = fields.filter(field => field.key !== fieldKey);
    setFields(updatedFields);

    // Update metadata without the removed field
    const newMetadata = {};
    updatedFields.forEach(field => {
      if (field.value) {
        newMetadata[field.key] = field.value;
      }
    });
    onChange(newMetadata);
  };

  const renderField = (field) => {
    const isInvalid = errors[field.key];

    if (field.type === 'textarea') {
      return (
        <Form.Control
          as="textarea"
          rows={3}
          value={field.value}
          onChange={(e) => handleFieldChange(field.key, e.target.value)}
          placeholder={`Enter ${field.label.toLowerCase()}`}
          isInvalid={isInvalid}
        />
      );
    }

    return (
      <Form.Control
        type={field.type}
        value={field.value}
        onChange={(e) => handleFieldChange(field.key, e.target.value)}
        placeholder={`Enter ${field.label.toLowerCase()}`}
        isInvalid={isInvalid}
      />
    );
  };

  return (
    <Card>
      <Card.Body>
        <Row>
          {fields.map((field, index) => (
            <Col md={6} key={field.key} className="mb-3">
              <Form.Group>
                <Form.Label>
                  {field.label}
                  {field.required && <span className="text-danger">*</span>}
                  {field.isCustom && (
                    <Button
                      variant="outline-danger"
                      size="sm"
                      className="ms-2"
                      onClick={() => removeCustomField(field.key)}
                    >
                      ×
                    </Button>
                  )}
                </Form.Label>
                {renderField(field)}
                {errors[field.key] && (
                  <Form.Control.Feedback type="invalid">
                    {errors[field.key]}
                  </Form.Control.Feedback>
                )}
              </Form.Group>
            </Col>
          ))}
        </Row>

        <div className="mt-3">
          <Button variant="outline-primary" size="sm" onClick={addCustomField}>
            + Add Custom Field
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

export default MetadataEditor;
