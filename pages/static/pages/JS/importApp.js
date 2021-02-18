const previousBtn = document.getElementById('previousBtn');
const nextBtn = document.getElementById('nextBtn');
const finshBtn = document.getElementById('finishBtn');
const navigateBtn = document.getElementById('navigateBtn');
const gpaBtn = document.getElementById('gpaBtn');
const manualBtn = document.getElementById('manualBtn');
const content = document.getElementById('content');
const bullets = [... document.querySelectorAll('.bullet')];
const tLinks = [... document.querySelectorAll('.tablink')];
const files = [... document.querySelectorAll('.file-input')];
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

nextBtn.addEventListener('click', () => {
    const currentBullet =  bullets[currentStep - 1];
    const currentFile = files[currentStep - 1];
    const nextFile = files[currentStep];
    currentBullet.classList.add('completed');
    currentFile.classList.add('hidden');
    nextFile.classList.remove('hidden');
    currentStep++;
    previousBtn.disabled = false;
    if(currentStep == MAX_STEPS) {
        nextBtn.disabled = true;
        finishBtn.disabled = false;
    }
})

previousBtn.addEventListener('click', () => {
    const currentBullet = bullets[currentStep - 2];
    const currentFile = files[currentStep - 2];
    const currentFileSelected = files[currentStep - 1];
    currentBullet.classList.remove('completed');
    currentFile.classList.remove('hidden');
    currentFileSelected.classList.add('hidden');
    currentStep--;
    nextBtn.disabled = false;
    finishBtn.disabled = true;
    if(currentStep == 1) {
        previousBtn.disabled = true;
    }
})

// finishBtn.addEventListener('click', () => {
//     location.reload();
// })


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