export class ChatDetailsModal {
    constructor() {
        this.modalElement = null;
        this.bootstrapModal = null;
    }

    render() {
        // Create the modal HTML structure if it doesn't exist
        if (!document.getElementById('chatDetailModal')) {
            const modalHtml = `
            <div class="modal fade" id="chatDetailModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="chatModalLabel">Chat Analysis Details</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body" id="chatModalBody">
                            Loading...
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }

        this.modalElement = document.getElementById('chatDetailModal');
        // We assume bootstrap.js is loaded globally in index.html
        this.bootstrapModal = new bootstrap.Modal(this.modalElement);
    }

    show(chatData, reason, improvement, keyMessages) {
        if (!this.bootstrapModal) this.render();

        const body = document.getElementById('chatModalBody');

        // Format messages HTML
        const messagesHtml = chatData.messages.map(m => `
            <div class="message-item ${m.role === 'customer' ? 'message-customer' : 'message-operator'}">
                <div class="message-header">
                    <span class="message-role">${m.role}</span>
                    <span style="opacity:0.6">${new Date(m.created_at).toLocaleTimeString()}</span>
                </div>
                <div class="message-text">${m.content}</div>
            </div>
        `).join('');

        const keyMessagesHtml = keyMessages && keyMessages.length > 0 ?
            `<ul>${keyMessages.map(km => `<li>${km}</li>`).join('')}</ul>` :
            '<em>None identified</em>';

        body.innerHTML = `
            <div class="chat-details-section">
                <h5>Evaluation</h5>
                <p class="chat-reason-modal">${reason}</p>
                <div class="detail-item">
                     <span class="detail-label">Improvement:</span>
                     <span class="detail-value">${improvement || 'N/A'}</span>
                </div>
                 <div class="detail-item">
                     <span class="detail-label">Key Points:</span>
                     <span class="detail-value">${keyMessagesHtml}</span>
                </div>
            </div>
            
            <div class="chat-details-section">
                <h5>Transcript (ID: ${chatData.chat.id})</h5>
                <div class="messages-list" style="max-height: 400px; overflow-y: auto;">
                    ${messagesHtml}
                </div>
            </div>
        `;

        this.bootstrapModal.show();
    }
}
