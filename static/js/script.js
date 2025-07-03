// ============== AUTO DATA CLEARING ==============
let sessionData = {};
let autoCleanupInterval;

// Clear all data on page load/refresh
window.addEventListener('load', () => {
    console.log('🧹 Page loaded - clearing any existing data');
    clearAllClientData();
    setupAutoCleanup();
});

// Clear data when user navigates away
window.addEventListener('beforeunload', () => {
    console.log('🧹 Page unload - clearing all data');
    clearAllClientData();
    clearServerSession();
});

// Clear data on browser tab close
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        console.log('🧹 Tab hidden - scheduling data clear');
        setTimeout(clearAllClientData, 1000);
    }
});

function clearAllClientData() {
    // Clear all variables
    window.encryptedData = null;
    window.decryptedMessage = null;
    sessionData = {};
    
    // Clear all forms
    document.querySelectorAll('form').forEach(form => {
        if (form) form.reset();
    });
    
    // Clear all result panels
    document.querySelectorAll('.result-panel').forEach(panel => {
        if (panel) panel.classList.add('hidden');
    });
    
    // Clear QR image
    const qrImage = document.getElementById('qrImage');
    if (qrImage) qrImage.src = '';
    
    // Clear decrypted message
    const messageElement = document.getElementById('decryptedMessage');
    if (messageElement) messageElement.textContent = '';
    
    // Reset upload area
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) {
        uploadArea.innerHTML = `
            <i class="fas fa-cloud-upload-alt upload-icon"></i>
            <p>Click to select QR code image</p>
        `;
    }
    
    // Clear local storage and session storage
    localStorage.clear();
    sessionStorage.clear();
    
    console.log('✅ All client data cleared');
}

function clearServerSession() {
    // Clear server session
    fetch('/api/clear-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).catch(() => {}); // Ignore errors
}

function setupAutoCleanup() {
    // Auto-clear data every 5 minutes
    if (autoCleanupInterval) {
        clearInterval(autoCleanupInterval);
    }
    
    autoCleanupInterval = setInterval(() => {
        console.log('🧹 Auto-cleanup triggered');
        clearAllClientData();
        clearServerSession();
    }, 5 * 60 * 1000); // 5 minutes
}

// ============== ENHANCED NOTIFICATION SYSTEM ==============
function showNotification(message, type = 'success') {
    // Remove any existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Add privacy indicator
    const privacyIcon = type === 'success' ? '🔒' : '⚠️';
    notification.innerHTML = `
        <span>${privacyIcon}</span>
        <span>${message}</span>
        <small style="opacity: 0.7; font-size: 0.8rem; display: block; margin-top: 4px;">
            ${type === 'success' ? 'Data will auto-delete' : 'No data stored permanently'}
        </small>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 4000);
}

// ============== ENHANCED ENCRYPTION HANDLER ==============
async function handleEncryption(e) {
    e.preventDefault();
    
    const message = document.getElementById('message').value;
    const password = document.getElementById('password').value;
    
    // Clear previous data first
    clearAllClientData();
    
    // Validation
    if (!message.trim()) {
        showNotification('Message cannot be empty', 'error');
        return;
    }
    
    if (!password || password.length < 6) {
        showNotification('Password must be at least 6 characters', 'error');
        return;
    }
    
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultPanel = document.getElementById('resultPanel');
    
    if (loadingSpinner) loadingSpinner.classList.remove('hidden');
    if (resultPanel) resultPanel.classList.add('hidden');
    
    try {
        const response = await fetch('/api/encrypt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-store, no-cache, must-revalidate'
            },
            body: JSON.stringify({ message, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const qrImage = document.getElementById('qrImage');
            if (qrImage) {
                qrImage.src = data.qr_code;
            }
            
            if (resultPanel) resultPanel.classList.remove('hidden');
            
            // Store temporarily (will be auto-cleared)
            window.encryptedData = JSON.stringify(data.encrypted_data);
            sessionData.encrypted = data.encrypted_data;
            
            showNotification(`QR code generated! (Session: ${data.session_info.session_id})`, 'success');
            
            // Auto-clear the password field for security
            document.getElementById('password').value = '';
            
        } else {
            showNotification(data.error || 'Encryption failed', 'error');
        }
    } catch (error) {
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        if (loadingSpinner) loadingSpinner.classList.add('hidden');
    }
}

// ============== ENHANCED DECRYPTION HANDLER ==============
async function handleDecryption(data) {
    // Clear previous data first
    clearAllClientData();
    
    const loading = document.getElementById('loading');
    const result = document.getElementById('resultPanel');
    
    if (loading) loading.classList.remove('hidden');
    if (result) result.classList.add('hidden');
    
    try {
        const isFormData = data instanceof FormData;
        
        const response = await fetch('/api/decrypt', {
            method: 'POST',
            body: isFormData ? data : JSON.stringify(data),
            headers: isFormData ? {
                'Cache-Control': 'no-store, no-cache, must-revalidate'
            } : {
                'Content-Type': 'application/json',
                'Cache-Control': 'no-store, no-cache, must-revalidate'
            }
        });
        
        const res = await response.json();
        
        if (res.success) {
            const messageElement = document.getElementById('decryptedMessage');
            if (messageElement) {
                messageElement.textContent = res.message;
            }
            
            if (result) result.classList.remove('hidden');
            
            // Store temporarily (will be auto-cleared)
            window.decryptedMessage = res.message;
            sessionData.decrypted = res.message;
            
            showNotification(`Message decrypted! (Session: ${res.session_info.session_id})`, 'success');
            
            // Auto-clear the password fields for security
            document.querySelectorAll('input[type="password"]').forEach(input => {
                input.value = '';
            });
            
            // Schedule auto-clear of decrypted message after 2 minutes
            setTimeout(() => {
                if (messageElement) messageElement.textContent = '[Message auto-cleared for security]';
                window.decryptedMessage = null;
            }, 2 * 60 * 1000);
            
        } else {
            showNotification('Error: ' + (res.error || 'Decryption failed'), 'error');
        }
    } catch (error) {
        console.error('Decryption error:', error);
        showNotification('Network error: ' + error.message, 'error');
    } finally {
        if (loading) loading.classList.add('hidden');
    }
}

// ============== INITIALIZATION ==============
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔐 QR Code Locker - Zero Persistence Mode');
    
    // Setup all event handlers with auto-clear
    setupEventHandlers();
    
    // Display privacy notice
    setTimeout(() => {
        showNotification('Privacy Mode: No data stored permanently', 'success');
    }, 1000);
});

function setupEventHandlers() {
    // Encryption form
    const encryptForm = document.getElementById('encryptForm');
    if (encryptForm) {
        encryptForm.addEventListener('submit', handleEncryption);
    }
    
    // Upload form
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('qrFile');
            const passwordInput = document.getElementById('uploadPassword');
            
            if (!fileInput?.files?.[0]) {
                showNotification('Please select a file', 'error');
                return;
            }
            
            if (!passwordInput?.value) {
                showNotification('Please enter password', 'error');
                return;
            }
            
            const formData = new FormData();
            formData.append('qr_file', fileInput.files[0]);
            formData.append('password', passwordInput.value);
            
            await handleDecryption(formData);
        });
    }
    
    // Paste form
    const pasteForm = document.getElementById('pasteForm');
    if (pasteForm) {
        pasteForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const encryptedData = document.getElementById('encryptedData').value;
            const password = document.getElementById('pastePassword').value;
            
            if (!encryptedData.trim() || !password) {
                showNotification('Please provide both encrypted data and password', 'error');
                return;
            }
            
            await handleDecryption({ encrypted_data: encryptedData, password });
        });
    }
    
    // Copy buttons with auto-clear
    const copyDataBtn = document.getElementById('copyDataBtn');
    if (copyDataBtn) {
        copyDataBtn.addEventListener('click', () => {
            if (window.encryptedData) {
                navigator.clipboard.writeText(window.encryptedData);
                showNotification('Data copied! (will auto-clear)', 'success');
                
                // Clear copied data from memory after 30 seconds
                setTimeout(() => {
                    window.encryptedData = null;
                }, 30000);
            }
        });
    }
    
    const copyBtn = document.getElementById('copyBtn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (window.decryptedMessage) {
                navigator.clipboard.writeText(window.decryptedMessage);
                showNotification('Message copied! (will auto-clear)', 'success');
                
                // Clear copied data from memory after 30 seconds
                setTimeout(() => {
                    window.decryptedMessage = null;
                }, 30000);
            }
        });
    }
    
    // Clear buttons
    const newButtons = document.querySelectorAll('#newEncryptBtn, #newBtn');
    newButtons.forEach(btn => {
        if (btn) {
            btn.addEventListener('click', () => {
                clearAllClientData();
                clearServerSession();
                showNotification('All data cleared!', 'success');
            });
        }
    });
}

console.log('🚀 Zero Persistence JavaScript loaded');
