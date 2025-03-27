// Main JavaScript for the ransomware simulation app

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // File upload preview
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', updateFileList);
    }
    
    // Countdown timer for ransomware simulation (if on recovery page)
    const countdownElement = document.getElementById('countdown-timer');
    if (countdownElement) {
        startCountdown(countdownElement, 24 * 60 * 60); // 24 hours in seconds
    }
    
    // Confirmation for dangerous actions
    const dangerButtons = document.querySelectorAll('.btn-danger, .confirm-action');
    dangerButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to proceed with this action?')) {
                e.preventDefault();
            }
        });
    });
    
    // Show file extension warning
    const fileExtensionWarning = document.getElementById('file-extension-warning');
    if (fileExtensionWarning) {
        fileExtensionWarning.style.display = 'block';
    }
});

// Display preview of selected files
function updateFileList() {
    const fileInput = document.querySelector('input[type="file"]');
    const fileListContainer = document.getElementById('file-list');
    
    if (!fileInput || !fileListContainer) return;
    
    // Clear existing list
    fileListContainer.innerHTML = '';
    
    if (fileInput.files.length > 0) {
        const fileList = document.createElement('ul');
        fileList.className = 'list-group mt-3';
        
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            const fileItem = document.createElement('li');
            fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            
            // File name
            const fileName = document.createElement('span');
            fileName.textContent = file.name;
            
            // File size
            const fileSize = document.createElement('span');
            fileSize.className = 'badge bg-primary rounded-pill';
            fileSize.textContent = formatFileSize(file.size);
            
            fileItem.appendChild(fileName);
            fileItem.appendChild(fileSize);
            fileList.appendChild(fileItem);
        }
        
        fileListContainer.appendChild(fileList);
        document.getElementById('simulate-btn').disabled = false;
    } else {
        document.getElementById('simulate-btn').disabled = true;
    }
}

// Format file size in KB, MB
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' B';
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(1) + ' KB';
    } else {
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
}

// Countdown timer for ransomware simulation
function startCountdown(element, duration) {
    let timer = duration;
    
    function updateTimer() {
        const hours = Math.floor(timer / 3600);
        const minutes = Math.floor((timer % 3600) / 60);
        const seconds = timer % 60;
        
        element.textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (--timer < 0) {
            // Handle timer expiry
            element.textContent = '00:00:00';
            clearInterval(interval);
            document.getElementById('timer-expired').classList.remove('d-none');
        }
    }
    
    updateTimer();
    const interval = setInterval(updateTimer, 1000);
}

// Toggle visibility of educational content sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.toggle('d-none');
    }
}

// Copy recovery key to clipboard
function copyRecoveryKey() {
    const keyField = document.getElementById('recovery-key');
    if (keyField) {
        navigator.clipboard.writeText(keyField.value)
            .then(() => {
                // Show success message
                const copyBtn = document.getElementById('copy-key-btn');
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy: ', err);
                alert('Failed to copy key. Please select and copy it manually.');
            });
    }
}
