document.body.classList.add("match-active");

window.gameInProgress = true;

document.addEventListener('keydown', function (e) {
    if (window.gameInProgress && ['ArrowUp', 'ArrowDown'].includes(e.key)) {
        e.preventDefault();
    }
});

window.addEventListener("DOMContentLoaded", () => {
    let lastVisitedPage = history.state?.lastVisitedPage || sessionStorage.getItem("lastVisitedPage");

    if (lastVisitedPage && window.location.href === lastVisitedPage && !sessionStorage.getItem("redirected")) {
        sessionStorage.setItem("redirected", "true");
    } else {
        sessionStorage.removeItem("redirected");
    }
});

function toggleSize() {
    const match = document.getElementById('match');

    match.classList.toggle('small-size');
    document.activeElement.blur();
}
