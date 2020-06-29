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

// Iterate through the sorted countries, adding them to list
countries.sort().forEach(country => {
  if (country === 'United States') return;
  const opt = document.createElement('OPTION')
  opt.innerHTML = country;
  countrySelect.appendChild(opt);
});

//Get state selection list
const stateSelect = document.getElementById('state-select');

//Add blank element to list
stateSelect.appendChild(document.createElement('OPTION'));

// Iterate through the sorted states, adding them to list
Object.keys(states).sort().forEach(state => {
  const opt = document.createElement('OPTION')
  opt.innerHTML = state;
  stateSelect.appendChild(opt);
});

// Get state and county rows
const stateRow = document.getElementById('state-row');
const countyRow = document.getElementById('county-row');

// Change display based on country selections made
document.getElementById('country-select').addEventListener('change', event => {

  // Enable/disable email selection box based on the selected country
  if (event.target.value === '') {
    document.getElementById('email').value = '';
  }
  document.getElementById('email').disabled = event.target.value == '';
});