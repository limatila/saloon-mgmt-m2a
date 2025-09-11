

// JS para tornar os rows de radio button clicável
document.addEventListener("DOMContentLoaded", function() {
    const rows = document.querySelectorAll("tbody tr[data-radio-id]");

    rows.forEach(row => {
        row.addEventListener("click", function(e) {
            // Ignora cliques em links ou botões dentro da row
            if(e.target.tagName.toLowerCase() === 'a' || e.target.tagName.toLowerCase() === 'button') return;

            const radioId = this.dataset.radioId;
            const radio = document.getElementById(radioId);
            if(radio) {
                radio.checked = true;
            }
        })
    })
})