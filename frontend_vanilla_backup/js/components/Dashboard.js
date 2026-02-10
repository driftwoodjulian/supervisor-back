import { login, getEvaluations, getChatDetails } from '../utils/api.js';
import { ChatDetailsModal } from './Modal.js';

const app = document.getElementById('app');
let token = localStorage.getItem('token');
const modal = new ChatDetailsModal();

// --- Logic Helpers ---

function groupScores(evals) {
    const groups = {
        Great: [],
        Good: [],
        Neutral: [],
        Bad: [],
        Horrible: [],
        Error: [],
        Unknown: []
    };

    evals.forEach(evalItem => {
        // Handle nested score object or direct value
        let rawScore = evalItem.score;
        if (typeof rawScore === 'object' && rawScore !== null && rawScore.score) {
            rawScore = rawScore.score;
        }

        let scoreTitle = "Unknown";
        if (typeof rawScore === 'string') {
            // Capitalize first letter: "great" -> "Great"
            scoreTitle = rawScore.charAt(0).toUpperCase() + rawScore.slice(1).toLowerCase();
        }

        if (groups[scoreTitle]) {
            groups[scoreTitle].push(evalItem);
        } else {
            groups.Unknown.push(evalItem);
        }
    });

    return groups;
}

// --- Renderers ---

function renderLogin() {
    app.innerHTML = `
        <div class="login-container">
            <div class="login-card p-4">
                <h2 class="login-title">SUPERVISOR AI</h2>
                <div class="mb-3">
                    <input type="text" id="username" class="form-control" placeholder="IDENTIFIER">
                </div>
                <div class="mb-3">
                    <input type="password" id="password" class="form-control" placeholder="ACCESS_CODE">
                </div>
                <button id="loginBtn" class="btn btn-primary w-100">AUTHENTICATE</button>
            </div>
        </div>
    `;

    document.getElementById('loginBtn').addEventListener('click', async () => {
        const user = document.getElementById('username').value;
        const pass = document.getElementById('password').value;
        try {
            const result = await login(user, pass);
            if (result.token) {
                token = result.token;
                localStorage.setItem('token', token);
                renderDashboard();
            } else {
                alert('Authentication Failed');
            }
        } catch (e) {
            alert('Connection Error');
        }
    });
}

function renderScoreCard(item) {
    // Parse inner score object if needed
    const scoreObj = (typeof item.score === 'object') ? item.score : { score: item.score };
    const score = scoreObj.score || "Unknown";
    const reason = item.reason || scoreObj.reason || "No reason provided";
    const improvement = item.improvement || scoreObj.improvement;
    const keyMessages = scoreObj.key_messages || [];

    // Map score to CSS class
    let scoreClass = 'score-unknown';
    if (score.toLowerCase() === 'great') scoreClass = 'score-great';
    if (score.toLowerCase() === 'good') scoreClass = 'score-good';
    if (score.toLowerCase() === 'neutral') scoreClass = 'score-neutral';
    if (score.toLowerCase() === 'bad') scoreClass = 'score-bad';
    if (score.toLowerCase() === 'horrible') scoreClass = 'score-horrible';

    return `
        <div class="score-card">
            <span class="score-badge ${scoreClass}">${score}</span>
            <div class="chat-id">Chat #${item.chat_id}</div>
            <div class="chat-reason" style="height: 60px; overflow: hidden; text-overflow: ellipsis;">
                ${reason}
            </div>
            <button class="btn btn-primary w-100 btn-sm view-details-btn" 
                data-id="${item.chat_id}"
                data-reason="${reason.replace(/"/g, '&quot;')}" 
                data-improvement="${(improvement || '').replace(/"/g, '&quot;')}"
                data-messages='${JSON.stringify(keyMessages).replace(/'/g, "&#39;")}'
            >
                View Transcript
            </button>
        </div>
    `;
}

async function renderDashboard() {
    app.innerHTML = `
        <div class="app-header">
            <h1>SUPERVISOR AI</h1>
            <p>Live Evaluation Stream</p>
            <div style="position: absolute; top: 20px; right: 20px;">
                <button id="logoutBtn" class="btn btn-sm btn-outline-danger">LOGOUT</button>
            </div>
        </div>
        
        <div id="content-area" class="score-container">
            <div class="loading-spinner">Initializing Uplink...</div>
        </div>
    `;

    // Logout Handler
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('token');
        token = null;
        renderLogin();
    });

    // Content Load
    async function refreshData() {
        try {
            const evals = await getEvaluations(token);
            updateGrid(evals);
        } catch (e) {
            if (e.status === 401) {
                localStorage.removeItem('token');
                renderLogin();
            } else {
                console.error(e);
            }
        }
    }

    refreshData();
    setInterval(refreshData, 5000); // Polling every 5s
}

function updateGrid(evals) {
    const container = document.getElementById('content-area');
    if (!evals || evals.length === 0) {
        container.innerHTML = '<div class="text-center text-muted p-5">No active evaluations found.</div>';
        return;
    }

    const groups = groupScores(evals);
    const sectionsObj = [
        { key: "Great", title: "Great - Excellent Satisfaction" },
        { key: "Good", title: "Good - Positive Satisfaction" },
        { key: "Neutral", title: "Neutral - Balanced Experience" },
        { key: "Bad", title: "Bad - Requires Attention" },
        { key: "Horrible", title: "Horrible - Critical Issues" },
        { key: "Unknown", title: "Unknown / Other" }
    ];

    let html = '';

    sectionsObj.forEach(section => {
        const items = groups[section.key];
        if (items && items.length > 0) {
            html += `
                <div class="score-section">
                    <div class="score-section-header">
                        <span class="score-badge score-${section.key.toLowerCase()} mb-0">${section.key}</span>
                        <span>${items.length} Chats</span>
                    </div>
                    <div class="score-cards-grid">
                        ${items.map(item => renderScoreCard(item)).join('')}
                    </div>
                </div>
            `;
        }
    });

    container.innerHTML = html;

    // Attach Event Listeners for Modals
    // Note: Re-rendering innerHTML removes listeners, so we re-attach them here.
    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const chatId = btn.dataset.id;
            const reason = btn.dataset.reason;
            const improvement = btn.dataset.improvement;
            let keyMessages = [];
            try { keyMessages = JSON.parse(btn.dataset.messages); } catch (e) { }

            // Show loading state on button
            const originalText = btn.innerText;
            btn.innerText = 'Loading...';
            btn.disabled = true;

            try {
                const chatData = await getChatDetails(chatId, token);
                modal.show(chatData, reason, improvement, keyMessages);
            } catch (err) {
                alert("Failed to load details: " + err.message);
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        });
    });
}

// Init
if (token) {
    renderDashboard();
} else {
    renderLogin();
}
