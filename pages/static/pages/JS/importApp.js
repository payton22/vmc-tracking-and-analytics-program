const navigateBtn = document.getElementById('navigateBtn');
const gpaBtn = document.getElementById('gpaBtn');
const manualBtn = document.getElementById('manualBtn');
const content = document.getElementById('content');
const tLinks = [... document.querySelectorAll('.tablink')];
const quotes = [... document.querySelectorAll('.hidden-content')];




const MAX_STEPS = 1;
let currentStep = 1;
let previousQuoteStep = 0;
let currentQuoteStep = 10;

navigateBtn.addEventListener('click', () => {
    const NavigateLink = tLinks[0]
    const GPALink = tLinks[1];
    const ManualLink = tLinks[2];
    GPALink.classList.remove('darkTab');
    ManualLink.classList.remove('darkTab');
    NavigateLink.classList.add('darkTab');
})

gpaBtn.addEventListener('click', () => {
    const NavigateLink = tLinks[0]
    const GPALink = tLinks[1];
    const ManualLink = tLinks[2];
    GPALink.classList.add('darkTab');
    ManualLink.classList.remove('darkTab');
    NavigateLink.classList.remove('darkTab');
})

manualBtn.addEventListener('click', () => {
    const NavigateLink = tLinks[0]
    const GPALink = tLinks[1];
    const ManualLink = tLinks[2];
    GPALink.classList.remove('darkTab');
    ManualLink.classList.add('darkTab');
    NavigateLink.classList.remove('darkTab');
})


function quoteFade() {
    
    if(currentQuoteStep > 9) {
        const currentQuote = quotes[previousQuoteStep];
        currentQuote.classList.add('unhidden');
        previousQuoteStep++;
    }

    setTimeout(function() {
        if(previousQuoteStep % quotes.length - 1 < 0) {
            currentQuoteStep = quotes.length - 1
        } else {
            currentQuoteStep = previousQuoteStep % quotes.length - 1;
        }

        const currentQuote = quotes[previousQuoteStep];
        const previousQuote = quotes[currentQuoteStep];
        previousQuote.classList.remove('unhidden');
        currentQuote.classList.add('unhidden');
        
        previousQuoteStep++;
        if(previousQuoteStep >= quotes.length) {
            previousQuoteStep = 0;    
        }
        quoteFade();
    }, 30000);
}

function openForm(formName) {
    var i;
    var x = document.getElementsByClassName("form");
    for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
    }
    document.getElementById(formName).style.display = "block";
    }