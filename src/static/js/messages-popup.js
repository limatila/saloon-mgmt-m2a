
document.addEventListener('DOMContentLoaded', function() {
    const popups = document.querySelectorAll('.message-popup');
    
    popups.forEach(popup => {
        const closeBtn = popup.querySelector('.btn-close');
        
        // fechar manual
        closeBtn.addEventListener('click', () => {
            popup.classList.add('fade-out');
            setTimeout(() => popup.remove(), 1000);
        });
        
        // fechar automático em 5s
        setTimeout(() => {
            popup.classList.add('fade-out');
            setTimeout(() => popup.remove(), 1000);
        }, 8000);
    });
    console.log("Message Script iniciado.")
});
