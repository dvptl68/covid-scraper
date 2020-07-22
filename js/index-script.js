// Display page when it is done loading
document.onreadystatechange = () => { if (document.readyState === 'complete') document.body.style.opacity = '1'; }

// Get GitHub image element
const github = document.getElementById('github');

// Change GitHub logo color scheme on hover/unhover
github.addEventListener('mouseenter', () => {
  github.style.backgroundColor = '#9FBAD3';
  github.src = 'images/dark-logo.png';
});

github.addEventListener('mouseleave', () => {
  github.style.backgroundColor = '#234574';
  github.src = 'images/light-logo.png';
});

// Open source code page on GitHub logo click
github.addEventListener('click', () => window.open('https://github.com/dvptl68/covid-scraper'));

// Function to set element positions
const setPositions = () => {

  // Get elements that need to be styled
  const titleBlock = document.getElementById('title-block');
  const infoBlock = document.getElementById('info-block');
  const mainContainer = document.getElementById('main-container');

  // Set vertical position of elements
  infoBlock.style.top = `${titleBlock.clientHeight}px`;
  mainContainer.style.top = `${titleBlock.clientHeight + infoBlock.clientHeight}px`;
};

// Set initial position of elements
setPositions();

// Set position of elements on window resize
window.onresize = setPositions;

// Get country selection list
const countrySelect = document.getElementById('country-select')

// Add blank element to list
countrySelect.appendChild(document.createElement('OPTION'))

// Add united states to list
const usa = document.createElement('OPTION');
usa.innerHTML = 'United States'
countrySelect.appendChild(usa)

