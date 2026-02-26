import React, { useState, useEffect } from 'react';
import { Card, Container, Row, Col, ListGroup, Button, Form, Badge, Modal } from 'react-bootstrap';
import { getToken } from '../auth';

const ConfigurationManager = ({ onBack }) => {
    const [prompts, setPrompts] = useState([]);
    const [manuals, setManuals] = useState([]);
    const [activeConfig, setActiveConfig] = useState({ active_prompt_id: null, active_manual_id: null });

    // Modal State
    const [showModal, setShowModal] = useState(false);
    const [modalType, setModalType] = useState('prompt'); // 'prompt' or 'manual'
    const [formData, setFormData] = useState({ title: '', content: '' });

    const [isSaving, setIsSaving] = useState(false);
    const [saveActiveStatus, setSaveActiveStatus] = useState('');

    const fetchData = async () => {
        try {
            const token = getToken();
            const headers = { 'Authorization': `Bearer ${token}` };

            const [promptsRes, manualsRes, activeRes] = await Promise.all([
                fetch('/api/config/prompts', { headers }),
                fetch('/api/config/manuals', { headers }),
                fetch('/api/config/active', { headers })
            ]);

            if (promptsRes.ok) setPrompts(await promptsRes.json());
            if (manualsRes.ok) setManuals(await manualsRes.json());
            if (activeRes.ok) setActiveConfig(await activeRes.json());

        } catch (error) {
            console.error("Failed to load configs:", error);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateSubmit = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        const endpoint = modalType === 'prompt' ? '/api/config/prompts' : '/api/config/manuals';
        const token = getToken();

        try {
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (res.ok) {
                setShowModal(false);
                setFormData({ title: '', content: '' });
                fetchData(); // reload lists
            } else {
                alert("Failed to save.");
            }
        } catch (e) {
            console.error(e);
            alert("Error saving.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleSetActive = async (type, id) => {
        const payload = { ...activeConfig };
        if (type === 'prompt') payload.active_prompt_id = id;
        if (type === 'manual') payload.active_manual_id = id;

        setSaveActiveStatus('Saving...');
        try {
            const token = getToken();
            const res = await fetch('/api/config/active', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setActiveConfig(payload);
                setSaveActiveStatus('Saved!');
                setTimeout(() => setSaveActiveStatus(''), 2000);
            }
        } catch (error) {
            console.error(error);
            setSaveActiveStatus('Error!');
        }
    };

    return (
        <Container fluid className="mt-4" style={{ paddingBottom: '100px' }}>
            <Button variant="outline-success" className="mb-3" onClick={onBack}>&larr; Back to Dashboard</Button>
            <h2 className="mb-4 text-center" style={{ fontFamily: "'Courier New', monospace", color: '#00ff41', textShadow: '0 0 10px #00ff41', letterSpacing: '2px', textTransform: 'uppercase' }}>
                SUPERVISOR AI: CONTEXT MANAGER
            </h2>
            <div className="text-center mb-4">
                <span className={`text-${saveActiveStatus === 'Saved!' ? 'success' : 'warning'}`}>{saveActiveStatus}</span>
            </div>

            <Row className="g-4">
                {/* System Prompts Column */}
                <Col md={6}>
                    <Card style={{ backgroundColor: '#000', border: '1px solid #00ff41', borderRadius: '0', boxShadow: '0 0 15px rgba(0, 255, 65, 0.2)' }}>
                        <Card.Header className="d-flex justify-content-between align-items-center" style={{ backgroundColor: '#001100', color: '#00ff41', borderBottom: '1px solid #00ff41', borderRadius: '0' }}>
                            <h5 className="mb-0" style={{ fontFamily: "'Fira Code', monospace", textTransform: 'uppercase' }}>System Prompts</h5>
                            <Button size="sm" variant="outline-success" onClick={() => { setModalType('prompt'); setShowModal(true); }}>+ Create New</Button>
                        </Card.Header>
                        <ListGroup variant="flush">
                            {prompts.map(p => (
                                <ListGroup.Item key={p.id} style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #003300' }}>
                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                        <div className="fw-bold" style={{ fontFamily: "'Fira Code', monospace" }}>{p.title}</div>
                                        <Button
                                            variant={activeConfig.active_prompt_id === p.id ? "primary" : "outline-success"}
                                            size="sm"
                                            style={activeConfig.active_prompt_id === p.id ? { backgroundColor: '#00ff41', color: '#000', fontWeight: 'bold' } : {}}
                                            onClick={() => handleSetActive('prompt', p.id)}
                                        >
                                            {activeConfig.active_prompt_id === p.id ? "ACTIVE" : "SET ACTIVE"}
                                        </Button>
                                    </div>
                                    <div style={{ fontSize: '0.9rem', color: '#00ff41', maxHeight: '400px', overflowY: 'auto', whiteSpace: 'pre-wrap', backgroundColor: '#000500', border: '1px solid #003300' }} className="p-3 rounded">
                                        {p.content}
                                    </div>
                                    <small style={{ color: '#00aa22' }} className="mt-1 d-block">Created: {new Date(p.created_at).toLocaleString()}</small>
                                </ListGroup.Item>
                            ))}
                            {prompts.length === 0 && <ListGroup.Item className="text-center" style={{ backgroundColor: '#000', color: '#00aa22' }}>No prompts saved.</ListGroup.Item>}
                        </ListGroup>
                    </Card>
                </Col>

                {/* Manuals Column */}
                <Col md={6}>
                    <Card style={{ backgroundColor: '#000', border: '1px solid #00ff41', borderRadius: '0', boxShadow: '0 0 15px rgba(0, 255, 65, 0.2)' }}>
                        <Card.Header className="d-flex justify-content-between align-items-center" style={{ backgroundColor: '#001100', color: '#00ff41', borderBottom: '1px solid #00ff41', borderRadius: '0' }}>
                            <h5 className="mb-0" style={{ fontFamily: "'Fira Code', monospace", textTransform: 'uppercase' }}>Quality Manuals</h5>
                            <Button size="sm" variant="outline-success" onClick={() => { setModalType('manual'); setShowModal(true); }}>+ Create New</Button>
                        </Card.Header>
                        <ListGroup variant="flush">
                            {manuals.map(m => (
                                <ListGroup.Item key={m.id} style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #003300' }}>
                                    <div className="d-flex justify-content-between align-items-start mb-2">
                                        <div className="fw-bold" style={{ fontFamily: "'Fira Code', monospace" }}>{m.title}</div>
                                        <Button
                                            variant={activeConfig.active_manual_id === m.id ? "primary" : "outline-success"}
                                            size="sm"
                                            style={activeConfig.active_manual_id === m.id ? { backgroundColor: '#00ff41', color: '#000', fontWeight: 'bold' } : {}}
                                            onClick={() => handleSetActive('manual', m.id)}
                                        >
                                            {activeConfig.active_manual_id === m.id ? "ACTIVE" : "SET ACTIVE"}
                                        </Button>
                                    </div>
                                    <div style={{ fontSize: '0.9rem', color: '#00ff41', maxHeight: '400px', overflowY: 'auto', whiteSpace: 'pre-wrap', backgroundColor: '#000500', border: '1px solid #003300' }} className="p-3 rounded mt-2">
                                        {m.content}
                                    </div>
                                    <small style={{ color: '#00aa22' }} className="mt-1 d-block">Created: {new Date(m.created_at).toLocaleString()}</small>
                                </ListGroup.Item>
                            ))}
                            {manuals.length === 0 && <ListGroup.Item className="text-center" style={{ backgroundColor: '#000', color: '#00aa22' }}>No manuals saved.</ListGroup.Item>}
                        </ListGroup>
                    </Card>
                </Col>
            </Row>

            {/* Create Modal */}
            <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
                <Modal.Header closeButton style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #00ff41', borderRadius: '0' }}>
                    <Modal.Title style={{ fontFamily: "'Fira Code', monospace", textTransform: 'uppercase' }}>
                        CREATE NEW {modalType === 'prompt' ? 'SYSTEM PROMPT' : 'QUALITY MANUAL'}
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body style={{ backgroundColor: '#000', color: '#00ff41' }}>
                    <Form onSubmit={handleCreateSubmit}>
                        <Form.Group className="mb-3">
                            <Form.Label style={{ color: '#00ff41' }}>Title / Version Name</Form.Label>
                            <Form.Control
                                type="text"
                                required
                                value={formData.title}
                                onChange={e => setFormData({ ...formData, title: e.target.value })}
                            />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label style={{ color: '#00ff41' }}>Content (Behavior Rules vs Guidelines)</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={10}
                                required
                                value={formData.content}
                                onChange={e => setFormData({ ...formData, content: e.target.value })}
                            />
                            <Form.Text style={{ color: '#00aa22', fontStyle: 'italic' }}>
                                This content will be strictly encrypted at rest in the database.
                            </Form.Text>
                        </Form.Group>
                        <div className="d-flex justify-content-end gap-2 mt-4">
                            <Button variant="outline-success" onClick={() => setShowModal(false)}>Cancel</Button>
                            <Button variant="primary" type="submit" disabled={isSaving}>{isSaving ? 'Encrypting...' : 'Save & Encrypt'}</Button>
                        </div>
                    </Form>
                </Modal.Body>
            </Modal>
        </Container>
    );
};

export default ConfigurationManager;
