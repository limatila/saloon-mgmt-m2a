document.addEventListener('DOMContentLoaded', () => {
    const popup = document.getElementById('popupMesAno');
    const overlay = document.getElementById('popupOverlay');
    const form = document.getElementById('formMesAno');
    const btnFechar = document.getElementById('btnFecharPopup');
    let currentUrl = null;

    // Open popup
    document.querySelectorAll('.btn-gerar-relatorio').forEach(btn => {
        btn.addEventListener('click', () => {
            currentUrl = btn.dataset.url;
            popup.style.display = 'block';
            overlay.style.display = 'block';
        });
    });

    // Close popup
    const fecharPopup = () => {
        popup.style.display = 'none';
        overlay.style.display = 'none';
    };
    btnFechar.addEventListener('click', fecharPopup);
    overlay.addEventListener('click', fecharPopup);

    // Submit form
    form.addEventListener('submit', e => {
        e.preventDefault();
        const mes = document.getElementById('mes').value;
        const ano = document.getElementById('ano').value;
        if (currentUrl) {
            const url = new URL(currentUrl, window.location.origin);
            url.searchParams.set('mes', mes);
            url.searchParams.set('ano', ano);
            window.open(url.toString(), '_blank');
            fecharPopup();
        }
    });
});
