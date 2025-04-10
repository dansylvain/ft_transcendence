window.addEventListener("DOMContentLoaded", () => {
    let lastVisitedPage = history.state?.lastVisitedPage || sessionStorage.getItem("lastVisitedPage");

    console.log("Dernière page visitée:", lastVisitedPage);
    console.log("Page actuelle:", window.location.href);

    // Vérifie si une page précédente existe et si l'URL actuelle n'est pas celle de la page d'erreur
    if (lastVisitedPage && window.location.href === lastVisitedPage && !sessionStorage.getItem("redirected")) {
        console.log("Redirection vers la dernière page visitée :", lastVisitedPage);
        
        // Marque que la redirection a eu lieu pour éviter la boucle infinie
        sessionStorage.setItem("redirected", "true");

    } else {
        sessionStorage.removeItem("redirected");
        console.log("Aucune page précédente trouvée ou déjà sur la page visitée.");
    }
});

document.addEventListener('click', (event) => {
    const overlay = document.getElementById('tuto-overlay');
    const overlayButton = document.getElementById('overlayButton');
    if (!overlay) return;

    if (event.target !=  overlayButton) {
        overlay.style.display = 'none';
    }
});

function replayTuto() {
    const overlay = document.getElementById('tuto-overlay');
    if (!overlay) return;

    overlay.style.display = 'flex';
    localStorage.removeItem('tutoSimpleMatchSeen');
}

function showTutoOverlayIfFirstTime() {
    const overlay = document.getElementById('tuto-overlay');
    if (!overlay) return;

    const alreadySeen = localStorage.getItem('tutoSimpleMatchSeen');
    //! if (!alreadySeen) { exchange the two lines to activate tutorial
    if (alreadySeen) {
        overlay.style.display = 'flex';

        overlay.addEventListener('click', () => {
            overlay.style.display = 'none';
            localStorage.setItem('tutoSimpleMatchSeen', 'true');
        });
    }
}

showTutoOverlayIfFirstTime();