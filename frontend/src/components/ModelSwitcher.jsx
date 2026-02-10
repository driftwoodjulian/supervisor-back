import React, { useState, useEffect } from 'react';
import { Button, Badge, Spinner } from 'react-bootstrap';
import { getModelStatus, switchModel } from '../api';

const ModelSwitcher = () => {
    const [status, setStatus] = useState({ model: 'unknown', status: 'unknown' });
    const [loading, setLoading] = useState(false);
    const [switching, setSwitching] = useState(false);

    const fetchStatus = () => {
        getModelStatus()
            .then(data => {
                setStatus(data);
                if (data.status === 'activating' || data.status === 'turning_off') {
                    setSwitching(true);
                } else {
                    setSwitching(false);
                }
            })
            .catch(err => console.error("Status fetch error:", err));
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(() => {
            // Poll more frequently if in transition
            fetchStatus();
        }, switching ? 2000 : 10000);

        return () => clearInterval(interval);
    }, [switching]);

    const handleSwitch = (targetModel) => {
        if (switching) return;
        setLoading(true);
        switchModel(targetModel)
            .then(() => {
                setSwitching(true);
                fetchStatus();
            })
            .catch(err => alert("Switch failed: " + err.message))
            .finally(() => setLoading(false));
    };

    const getStatusColor = (s) => {
        switch (s) {
            case 'active': return 'success';
            case 'activating': return 'warning';
            case 'turning_off': return 'danger';
            case 'off': return 'secondary';
            default: return 'light';
        }
    };

    return (
        <div className="d-flex align-items-center gap-2">
            <span className="text-secondary fw-bold small text-uppercase" style={{ letterSpacing: '1px' }}>AI Model:</span>

            <div className="position-relative">
                <select
                    className="form-select form-select-sm bg-black text-info fw-bold text-uppercase"
                    style={{
                        width: 'auto',
                        minWidth: '160px',
                        height: '31px', // Exact match for btn-sm
                        fontSize: '0.875rem', // Match btn-sm font
                        paddingTop: '2px',
                        paddingBottom: '2px',
                        borderColor: '#00ff41',
                        borderWidth: '1px',
                        boxShadow: status.status === 'active' ? '0 0 5px rgba(0, 255, 65, 0.3)' : 'none',
                        color: status.status === 'active' ? '#00ff41 !important' : '#17a2b8 !important'
                    }}
                    value={status.model}
                    onChange={(e) => handleSwitch(e.target.value)}
                    disabled={switching}
                >
                    <option value="gptoss">GPTOSS (Supervisor)</option>
                    <option value="gemma">Gemma 3</option>
                </select>

                {/* Status Indicator Dot */}
                <div
                    className="position-absolute rounded-circle"
                    style={{
                        width: '8px',
                        height: '8px',
                        top: '50%',
                        right: '30px',
                        transform: 'translateY(-50%)',
                        backgroundColor: status.status === 'active' ? '#00ff41' : (status.status === 'off' ? '#6c757d' : '#ffc107'),
                        boxShadow: status.status === 'active' ? '0 0 5px #00ff41' : 'none',
                        pointerEvents: 'none'
                    }}
                />
            </div>

            {(switching || loading) && (
                <Spinner animation="border" size="sm" variant="info" style={{ width: '1rem', height: '1rem' }} />
            )}
        </div>
    );
};

export default ModelSwitcher;
