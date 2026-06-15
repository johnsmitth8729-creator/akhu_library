class ModalManager {
    constructor() {
        this.createModalStructure();
    }

    createModalStructure() {
        if (document.getElementById('sys-modal-overlay')) return;
        
        const overlay = document.createElement('div');
        overlay.id = 'sys-modal-overlay';
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 id="sys-modal-title">Confirm Action</h3>
                    <button class="modal-close" onclick="sysModal.close()">&times;</button>
                </div>
                <div class="modal-body" id="sys-modal-body">
                    Are you sure you want to proceed?
                </div>
                <div class="modal-footer" id="sys-modal-footer">
                    <button class="btn btn-ghost" onclick="sysModal.close()">Cancel</button>
                    <button class="btn btn-primary" id="sys-modal-confirm">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
        this.overlay = overlay;
    }

    confirm(title, message, onConfirm, confirmText = "Confirm", confirmClass = "btn-primary") {
        document.getElementById('sys-modal-title').innerText = title;
        document.getElementById('sys-modal-body').innerText = message;
        
        const confirmBtn = document.getElementById('sys-modal-confirm');
        confirmBtn.innerText = confirmText;
        confirmBtn.className = `btn ${confirmClass}`;
        
        confirmBtn.onclick = () => {
            onConfirm();
            this.close();
        };
        
        this.overlay.classList.add('active');
    }

    close() {
        this.overlay.classList.remove('active');
    }
}

window.sysModal = new ModalManager();

// Intercept form submissions requiring confirmation
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            const message = el.getAttribute('data-confirm');
            const isForm = el.tagName === 'BUTTON' && el.form;
            sysModal.confirm('Confirm Action', message, () => {
                if (isForm) el.form.submit();
                else if (el.tagName === 'A') window.location.href = el.href;
            });
        });
    });
});
