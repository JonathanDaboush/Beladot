import React, { useState, useCallback } from 'react';
import { Card, Button, Alert, Spinner, Form, Row, Col } from 'react-bootstrap';
import axios from 'axios';

/**
 * ImageUpload Component
 * Drag-and-drop or click to upload product images
 * Supports multiple images with preview and progress
 */
const ImageUpload = ({ productId, onUploadComplete, maxImages = 10 }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    
    if (selectedFiles.length + files.length > maxImages) {
      setError(`Maximum ${maxImages} images allowed`);
      return;
    }

    // Validate files
    const validFiles = files.filter(file => {
      const isValid = file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024;
      if (!isValid) {
        setError(`${file.name} is invalid (must be image, max 5MB)`);
      }
      return isValid;
    });

    if (validFiles.length === 0) return;

    setSelectedFiles(prev => [...prev, ...validFiles]);

    // Generate previews
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviews(prev => [...prev, { file: file.name, url: reader.result }]);
      };
      reader.readAsDataURL(file);
    });

    setError(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();

    const files = Array.from(e.dataTransfer.files);
    handleFileSelect({ target: { files } });
  }, [selectedFiles]);

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select at least one image');
      return;
    }

    setUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('product_id', productId);
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });

      const response = await axios.post('/api/upload/product-images-bulk', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      // Clear selections
      setSelectedFiles([]);
      setPreviews([]);
      setUploadProgress(0);

      if (onUploadComplete) {
        onUploadComplete(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Card>
      <Card.Body>
        <h5>Upload Product Images</h5>
        
        {error && (
          <Alert variant="danger" dismissible onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Drag and Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{
            border: '2px dashed #ccc',
            borderRadius: '8px',
            padding: '40px',
            textAlign: 'center',
            backgroundColor: '#f8f9fa',
            cursor: 'pointer',
            marginBottom: '20px'
          }}
          onClick={() => document.getElementById('fileInput').click()}
        >
          <div style={{ fontSize: '48px', color: '#6c757d' }}>📷</div>
          <p className="mb-2">Drag and drop images here, or click to select</p>
          <small className="text-muted">Max {maxImages} images, 5MB each (JPG, PNG, WebP)</small>
        </div>

        <Form.Control
          id="fileInput"
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />

        {/* Preview Grid */}
        {previews.length > 0 && (
          <div className="mb-3">
            <h6>Selected Images ({selectedFiles.length}/{maxImages})</h6>
            <Row xs={2} md={4} className="g-3">
              {previews.map((preview, index) => (
                <Col key={index}>
                  <div style={{ position: 'relative' }}>
                    <img
                      src={preview.url}
                      alt={`Preview ${index + 1}`}
                      style={{
                        width: '100%',
                        height: '150px',
                        objectFit: 'cover',
                        borderRadius: '8px',
                        border: '1px solid #dee2e6'
                      }}
                    />
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => removeFile(index)}
                      style={{
                        position: 'absolute',
                        top: '5px',
                        right: '5px',
                        padding: '2px 8px'
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                </Col>
              ))}
            </Row>
          </div>
        )}

        {/* Upload Progress */}
        {uploading && (
          <div className="mb-3">
            <div className="d-flex align-items-center gap-2">
              <Spinner animation="border" size="sm" />
              <span>Uploading... {uploadProgress}%</span>
            </div>
            <div className="progress mt-2">
              <div
                className="progress-bar progress-bar-striped progress-bar-animated"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Upload Button */}
        <div className="d-flex gap-2">
          <Button
            variant="primary"
            onClick={handleUpload}
            disabled={selectedFiles.length === 0 || uploading}
          >
            {uploading ? 'Uploading...' : `Upload ${selectedFiles.length} Image(s)`}
          </Button>
          {selectedFiles.length > 0 && (
            <Button
              variant="outline-secondary"
              onClick={() => {
                setSelectedFiles([]);
                setPreviews([]);
              }}
              disabled={uploading}
            >
              Clear All
            </Button>
          )}
        </div>
      </Card.Body>
    </Card>
  );
};

export default ImageUpload;
