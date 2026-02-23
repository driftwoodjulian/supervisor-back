import React, { useState } from 'react';
import { Modal, Button } from 'react-bootstrap';
import { getFlamachatUrl } from '../utils/imageResolver';

const DashboardImage = ({ path, alt }) => {
    const [status, setStatus] = useState('loading'); // 'loading', 'loaded', 'error'
    const [showModal, setShowModal] = useState(false);
    const fullUrl = getFlamachatUrl(path);

    const handleLoad = () => setStatus('loaded');
    const handleError = () => setStatus('error');
    const handleRecalculate = () => {
        // Force reload if needed or just re-verify
        const result = confirm("Is the image broken? Click OK to try forcing a reload.");
        if (result) {
            setStatus('loading');
            setTimeout(() => {
                const img = new Image();
                img.src = fullUrl; // Cache bust?
                // Simple state reset for now
            }, 100);
        }
    };

    if (status === 'error') {
        return (
            <div className="d-flex align-items-center justify-content-center border border-danger p-3 my-2 text-danger"
                style={{ width: '200px', height: '150px', background: 'rgba(255,0,0,0.1)', fontSize: '0.8rem' }}
                title={`Failed to load: ${fullUrl}`}>
                <i className="bi bi-exclamation-triangle me-2"></i>
                IMG ERROR
            </div>
        );
    }

    return (
        <>
            <div
                className="dashboard-image-container my-2"
                style={{ position: 'relative', minHeight: status === 'loaded' ? 'auto' : '150px', cursor: status === 'loaded' ? 'zoom-in' : 'default' }}
                onClick={() => status === 'loaded' && setShowModal(true)}
            >
                {status === 'loading' && (
                    <div className="d-flex align-items-center justify-content-center text-muted border border-secondary"
                        style={{ width: '200px', height: '150px', background: '#111' }}>
                        <div className="spinner-border spinner-border-sm text-secondary me-2" role="status"></div>
                        <span className="small">Loading...</span>
                    </div>
                )}

                <img
                    src={fullUrl}
                    alt={alt || "Chat Image"}
                    title={`Source: ${fullUrl} (Click to Zoom)`}
                    loading="lazy"
                    onLoad={handleLoad}
                    onError={handleError}
                    className="img-fluid border border-secondary rounded"
                    style={{
                        // Fix: display: none prevents onLoad. Use absolute/opacity/pointer-events instead.
                        ...(status === 'loading'
                            ? { position: 'absolute', opacity: 0, width: '1px', height: '1px', pointerEvents: 'none', top: 0 }
                            : { display: 'block', maxWidth: '300px', maxHeight: '400px', objectFit: 'contain' }
                        )
                    }}
                />
            </div>

            {/* Zoom Modal */}
            <Modal show={showModal} onHide={() => setShowModal(false)} size="xl" centered>
                <Modal.Body className="bg-black p-0 d-flex justify-content-center align-items-center position-relative" style={{ minHeight: '500px' }}>
                    <button
                        type="button"
                        className="btn-close btn-close-white position-absolute top-0 end-0 m-3"
                        aria-label="Close"
                        onClick={() => setShowModal(false)}
                        style={{ zIndex: 10, background: 'rgba(255,255,255,0.8)' }}
                    ></button>
                    <img
                        src={fullUrl}
                        alt="Full size"
                        className="img-fluid"
                        style={{ maxHeight: '90vh', maxWidth: '100%' }}
                    />
                </Modal.Body>
            </Modal>
        </>
    );
};

export default DashboardImage;
