import { getToken } from './auth';

const GATEWAY_URL = `http://${window.location.hostname}:6002/api`;

export async function login(username, password) {
    const response = await fetch(`${GATEWAY_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    return response.json();
}

export async function getEvaluations() {
    const token = getToken();
    const response = await fetch(`${GATEWAY_URL}/evaluations`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (response.status === 401) {
        throw { status: 401 };
    }
    return response.json();
}

export async function getChatDetails(chatId) {
    const token = getToken();
    const response = await fetch(`${GATEWAY_URL}/chats/${chatId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) throw { status: response.status };
    return response.json();
}

export async function getAgentStats(filterType = 'current') {
    const token = getToken();
    const response = await fetch(`${GATEWAY_URL}/stats/agents?filter=${filterType}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) throw { status: response.status };
    if (!response.ok) throw { status: response.status };
    return response.json();
}

export async function getModelStatus() {
    const token = getToken();
    const response = await fetch(`${GATEWAY_URL}/admin/model-status`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) throw new Error('Failed to get status');
    return response.json();
}

export async function switchModel(modelName) {
    const token = getToken();
    const response = await fetch(`${GATEWAY_URL}/admin/switch-model`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ model: modelName })
    });
    if (!response.ok) throw new Error('Failed to switch model');
    return response.json();
}

