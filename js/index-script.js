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

// Iterate through the sorted countries, adding them to list
countries.sort().forEach(country => {
  if (country === 'United States') return;
  const opt = document.createElement('OPTION')
  opt.innerHTML = country;
  countrySelect.appendChild(opt);
});

// Get state selection list
const stateSelect = document.getElementById('state-select');

// Add blank element to list
stateSelect.appendChild(document.createElement('OPTION'));

// Iterate through the sorted states, adding them to list
Object.keys(states).sort().forEach(state => {
  const opt = document.createElement('OPTION')
  opt.innerHTML = state;
  stateSelect.appendChild(opt);
});

// Get county selection list
const countySelect = document.getElementById('county-select');

// Function that fills county selection list with correct counties
const fillCounties = state => {

  // Clear current list items
  countySelect.innerHTML = '';

  // Add blank element to list
  countySelect.appendChild(document.createElement('OPTION'));

  // Fill selection list with currect counties
  counties[state].sort().forEach(county => {
    const opt = document.createElement('OPTION')
    opt.innerHTML = county;
    countySelect.appendChild(opt);
  });
}

// Get state and county rows and separators
const stateRow = document.getElementById('state-row');
const stateSep = document.getElementById('state-sep');
const countyRow = document.getElementById('county-row');
const countySep = document.getElementById('county-sep');

// Change display based on country selections made
countrySelect.addEventListener('change', event => {

  // Country name
  const country = event.target.value;

  // Hide/show state and county selection based on the selected country
  stateRow.style.display = (country === 'United States') ? 'flex' : 'none';
  stateSep.style.display = (country === 'United States') ? 'flex' : 'none';
  countyRow.style.display = 'none';
  countySep.style.display = 'none';

  // Reset selections
  stateSelect.children[0].selected = true;

  // Enable/disable email and name input boxes based on the selected country
  document.getElementById('email').disabled = country == '';
  document.getElementById('name').disabled = country == '';
});

// Change display based on state selections made
stateSelect.addEventListener('change', event => {

  // State name
  const state = event.target.value;

  // Hide/show county selection based on the selected state
  countyRow.style.display = (state !== '' && state !== 'Utah') ? 'flex' : 'none';
  countySep.style.display = (state !== '' && state !== 'Utah') ? 'flex' : 'none';

  // Skip rest of function if selected state is Utah or none
  if (state === '' || state =='Utah') return;

  // Set section name depending on state
  let sectionName = 'County';
  if (state === 'Alaska') sectionName = 'Borough'; 
  else if (state === 'Louisiana') sectionName = 'Parish';
  else if (state === 'Rhode Island') sectionName = 'Municipality';

  // Set county selection label text
  document.getElementById('county-label').innerHTML = `${sectionName} in ${state} (optional):`;

  // Fill county selections
  fillCounties(state);

  // Reset selection
  countySelect.children[0].selected = true;
});