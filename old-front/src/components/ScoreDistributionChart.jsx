"use client";

import { useMemo } from "react";

export default function ScoreDistributionChart({ scores }) {
    const distribution = useMemo(() => {
        const counts = {
            Great: 0,
            Good: 0,
            Neutral: 0,
            Bad: 0,
            Horrible: 0,
            Error: 0,
            Unknown: 0
        };

        scores.forEach((item) => {
            let scoreRaw = item.score?.score || item.score;

            // Check for error first
            if (item.score && typeof item.score === 'object' && 'error' in item.score) {
                counts.Error++;
                return;
            }

            let score = "Unknown";
            if (typeof scoreRaw === 'string') {
                score = scoreRaw.charAt(0).toUpperCase() + scoreRaw.slice(1).toLowerCase();
            }

            if (counts.hasOwnProperty(score)) {
                counts[score]++;
            } else {
                counts.Unknown++;
            }
        });

        const total = scores.length;
        return Object.entries(counts).map(([label, count]) => ({
            label,
            count,
            percentage: total > 0 ? (count / total) * 100 : 0
        })).filter(item => item.count > 0);
    }, [scores]);

    // Define colors matching CSS
    const chartColors = {
        Great: "#20c997",   // Teal-ish Green
        Good: "#28a745",    // Standard Green
        Neutral: "#ffc107", // Yellow/Amber
        Bad: "#fd7e14",     // Orange
        Horrible: "#dc3545",// Red
        Error: "#343a40",   // Dark
        Unknown: "#6c757d"  // Grey
    };

    const conicGradient = useMemo(() => {
        let currentDeg = 0;
        const segments = distribution.map((item) => {
            const degrees = (item.percentage / 100) * 360;
            const color = chartColors[item.label] || chartColors.Unknown;
            const segment = `${color} ${currentDeg}deg ${currentDeg + degrees}deg`;
            currentDeg += degrees;
            return segment;
        });

        // If empty, show gray ring
        if (segments.length === 0) return "#e9ecef 0deg 360deg";

        return segments.join(", ");
    }, [distribution]);

    if (!scores || scores.length === 0) return null;

    return (
        <div className="chart-container">
            <h3 className="text-center mb-4 text-dark">Score Distribution</h3>
            <div className="chart-content">
                <div
                    className="donut-chart"
                    style={{
                        background: `conic-gradient(${conicGradient})`
                    }}
                >
                    <div className="donut-hole">
                        <span className="total-count">{scores.length}</span>
                        <span className="total-label">Total</span>
                    </div>
                </div>
                <div className="chart-legend">
                    {distribution.map(item => (
                        <div key={item.label} className="legend-item">
                            <span
                                className="legend-color"
                                style={{ background: chartColors[item.label] || chartColors.Unknown }}
                            ></span>
                            <span className="legend-label">{item.label}</span>
                            <span className="legend-value">
                                {item.count} ({Math.round(item.percentage)}%)
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
