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

// Iterate through the sorted countries, adding them to list
countries.sort().forEach(country => {
  const opt = document.createElement('OPTION')
  opt.innerHTML = country;
  countrySelect.appendChild(opt);
});


// Change display based on country selections made
document.getElementById('country-select').addEventListener('change', event => {

  // Enable/disable email selection box based on the selected country
  if (event.target.value == '') {
    document.getElementById('email').value = '';
  }
  document.getElementById('email').disabled = event.target.value == '';
});