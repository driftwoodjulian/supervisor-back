const GATEWAY_URL = `http://${window.location.hostname}:6002/api`; // Pointing to Gateway (which points to Backend)

export async function login(username, password) {
    const response = await fetch(`${GATEWAY_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    return response.json();
}

export async function getEvaluations(token) {
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

export async function getChatDetails(chatId, token) {
    const response = await fetch(`${GATEWAY_URL}/chats/${chatId}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    if (!response.ok) throw { status: response.status };
    return response.json();
}
