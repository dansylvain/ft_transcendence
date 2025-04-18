if (typeof window.applyBackground === 'undefined') {
    // console.log("typeof");

    window.applyBackground = (bg) => {
        const main = document.getElementById('main_content');
        if (main && bg) {
            main.style.backgroundImage = `url(${bg})`;
            main.style.backgroundRepeat = 'no-repeat';
            main.style.backgroundSize = '100% 100%';
            main.style.backgroundPosition = 'top center';
            main.style.transition = 'background-image 0.3s ease';
            main.style.maxHeight = '100vh';
        }
    };
}

document.querySelectorAll('.side-nav').forEach(item => {
    const text = document.querySelector('.myText');
    // console.log("queryselector");
    // console.log(text);

    item.addEventListener('mouseenter', () => {
        if (text) text.style.opacity = '0';
        const bg = item.getAttribute('data-bg');
        // console.log("bg 1: ", bg)
        window.currentBg = bg;
        window.currentNav = item.querySelector('a');
        window.applyBackground(bg);

    });
    item.addEventListener('mouseleave', () => {
        if (text) text.style.opacity = '1';
        setFirstBgImage();
      });
});

function setFirstBgImage()
{
    // console.log("first image");



    window.currentBg = 'https://dansylvain.github.io/pictures/marvin.jpg';
    window.applyBackground(window.currentBg);

}
window.addEventListener('DOMContentLoaded', () => {
    // console.log("DOM CONTENT LOQDED");

    // console.log("%%%%%%%% func onload executed %%%%%%%%");
    setFirstBgImage();
    
});

document.body.addEventListener('htmx:afterSwap', () => {
    // console.log("%%%%%%%% HTMX content swapped %%%%%%%%");
    // console.log("AFTER SWAP");
    window.currentBg = 'https://dansylvain.github.io/pictures/marvin.jpg';

    if (!window.currentBg)
        setFirstBgImage();
    else {
        setTimeout(() => {
            window.applyBackground(window.currentBg);
        }, 100);
    }
});

if (typeof window.currentBg == 'undefined')
{
    // console.log("UNDEFINED");

    setFirstBgImage();
    window.applyBackground(window.currentBg);
}



