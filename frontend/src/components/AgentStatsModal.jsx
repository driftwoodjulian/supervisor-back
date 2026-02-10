
import React, { useState, useEffect } from 'react';
import { Modal, Button, Table, ButtonGroup } from 'react-bootstrap';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';
import { getAgentStats } from '../api';

ChartJS.register(ArcElement, Tooltip, Legend);

const AgentStatsModal = ({ show, onHide }) => {
    const [stats, setStats] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filterType, setFilterType] = useState('current'); // 'current' or 'historical'

    useEffect(() => {
        if (show) {
            setLoading(true);
            getAgentStats(filterType) // Pass filterType
                .then(setStats)
                .catch(err => console.error("Error loading stats:", err))
                .finally(() => setLoading(false));
        }
    }, [show, filterType]); // Re-run when show or filterType changes

    return (
        <Modal show={show} onHide={onHide} size="xl" centered>
            <Modal.Header closeButton style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41', color: '#00ff41' }}>
                <div className="d-flex align-items-center w-100 justify-content-between me-4 agent-stats-header">
                    <Modal.Title style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>Agent Performance Statistics</Modal.Title>
                    <ButtonGroup size="sm">
                        <Button
                            style={{
                                backgroundColor: filterType === 'current' ? '#00ff41' : '#000',
                                color: filterType === 'current' ? '#000' : '#00ff41',
                                border: '1px solid #00ff41',
                                borderRadius: 0,
                                fontWeight: 'bold'
                            }}
                            onClick={() => setFilterType('current')}
                        >
                            Current
                        </Button>
                        <Button
                            style={{
                                backgroundColor: filterType === 'historical' ? '#00ff41' : '#000',
                                color: filterType === 'historical' ? '#000' : '#00ff41',
                                border: '1px solid #00ff41',
                                borderRadius: 0,
                                fontWeight: 'bold'
                            }}
                            onClick={() => setFilterType('historical')}
                        >
                            Historical
                        </Button>
                    </ButtonGroup>
                </div>
            </Modal.Header>
            <Modal.Body className="bg-black text-white p-0">
                {loading ? (
                    <div className="text-center p-5">
                        <div className="spinner-border text-success" role="status">
                            <span className="visually-hidden">Loading...</span>
                        </div>
                    </div>
                ) : (
                    <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                        <Table bordered hover variant="dark" responsive className="mb-0 agent-stats-table" style={{ borderColor: '#00ff41', color: '#00ff41' }}>
                            <thead style={{ position: 'sticky', top: 0, zIndex: 1, backgroundColor: '#000' }}>
                                <tr>
                                    <th style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #00ff41' }}>Agent Name</th>
                                    <th style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #00ff41' }}>Total</th>
                                    <th className="text-success" style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41' }}>Great %</th>
                                    <th className="text-info" style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41' }}>Good %</th>
                                    <th className="text-secondary" style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41' }}>Neutral %</th>
                                    <th className="text-warning" style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41' }}>Bad %</th>
                                    <th className="text-danger" style={{ backgroundColor: '#000', borderBottom: '1px solid #00ff41' }}>Horrible %</th>
                                    <th style={{ backgroundColor: '#000', color: '#00ff41', borderBottom: '1px solid #00ff41' }}>Distribution</th>
                                </tr>
                            </thead>
                            <tbody>
                                {stats.length > 0 ? (
                                    stats.map((row, idx) => (
                                        <tr key={idx} style={{ verticalAlign: 'middle' }}>
                                            <td data-label="Agent Name" className="fw-bold" style={{ backgroundColor: '#000', color: '#00ff41', borderRight: '1px solid #003300' }}>{row.agent}</td>
                                            <td data-label="Total" style={{ backgroundColor: '#000', color: '#fff', borderRight: '1px solid #003300' }}>{row.total}</td>
                                            <td data-label="Great %" className="text-success" style={{ backgroundColor: '#000', borderRight: '1px solid #003300' }}>{row.pct_great}%</td>
                                            <td data-label="Good %" className="text-info" style={{ backgroundColor: '#000', borderRight: '1px solid #003300' }}>{row.pct_good}%</td>
                                            <td data-label="Neutral %" className="text-secondary" style={{ backgroundColor: '#000', borderRight: '1px solid #003300' }}>{row.pct_neutral}%</td>
                                            <td data-label="Bad %" className="text-warning" style={{ backgroundColor: '#000', borderRight: '1px solid #003300' }}>{row.pct_bad}%</td>
                                            <td data-label="Horrible %" className="text-danger" style={{ backgroundColor: '#000', borderRight: '1px solid #003300' }}>{row.pct_horrible}%</td>
                                            <td data-label="Distribution" style={{ width: '100px', height: '100px', backgroundColor: '#000' }}>
                                                <div style={{ width: '80px', height: '80px', margin: '0 auto' }}>
                                                    <Doughnut
                                                        data={{
                                                            labels: ['Great', 'Good', 'Neutral', 'Bad', 'Horrible'],
                                                            datasets: [{
                                                                data: [row.pct_great, row.pct_good, row.pct_neutral, row.pct_bad, row.pct_horrible],
                                                                backgroundColor: [
                                                                    '#198754', // Great (Success)
                                                                    '#0dcaf0', // Good (Info)
                                                                    '#6c757d', // Neutral (Secondary)
                                                                    '#ffc107', // Bad (Warning)
                                                                    '#dc3545'  // Horrible (Danger)
                                                                ],
                                                                borderWidth: 0
                                                            }]
                                                        }}
                                                        options={{
                                                            responsive: true,
                                                            maintainAspectRatio: false,
                                                            plugins: {
                                                                legend: { display: false },
                                                                tooltip: { enabled: true }
                                                            },
                                                            cutout: '60%'
                                                        }}
                                                    />
                                                </div>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan="8" className="text-center p-4" style={{ backgroundColor: '#000', color: '#ff003c', border: 'none' }}>
                                            No agent data available
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </Table>
                    </div>
                )}
            </Modal.Body>
            <Modal.Footer style={{ backgroundColor: '#000', borderTop: '1px solid #00ff41' }}>
                <Button
                    style={{ backgroundColor: '#000', color: '#00ff41', border: '1px solid #00ff41', borderRadius: 0 }}
                    onClick={onHide}
                    onMouseOver={(e) => { e.target.style.backgroundColor = '#00ff41'; e.target.style.color = '#000'; }}
                    onMouseOut={(e) => { e.target.style.backgroundColor = '#000'; e.target.style.color = '#00ff41'; }}
                >
                    Close
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default AgentStatsModal;
