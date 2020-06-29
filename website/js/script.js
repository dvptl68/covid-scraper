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

// Form DOM element
const form = document.getElementById('selections')

// Function that creates a country selection list
const createCountryList = () => {

  // Create label for selection list
  const label = document.createElement('LABEL');
  label.innerHTML = 'Country: ';

  // Create selection list
  const list = document.createElement('SELECT');

  // Iterate through all countries, adding them to list
  countries.forEach(e => {
    const opt = document.createElement('OPTION')
    opt.innerHTML = e;
    list.appendChild(opt);
  });

  // Add label and list to form
  form.appendChild(label);
  form.appendChild(list);
};

createCountryList();