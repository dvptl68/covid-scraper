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

// Get form and email label elements
const form = document.getElementById('selections')
const email = document.getElementById('email-label');

// Function that creates a country selection list
const createCountryList = () => {

  // Row for contents
  const row = document.createElement('DIV');
  row.classList.add('row');

  // Column for contents
  const col = document.createElement('DIV');
  col.classList.add('col-auto');

  // Create label for selection list
  const label = document.createElement('LABEL');
  label.classList.add('labels');
  label.innerHTML = 'Country: ';

  // Create selection list
  const list = document.createElement('SELECT');

  // Iterate through all countries, adding them to list
  countries.forEach(e => {
    const opt = document.createElement('OPTION')
    opt.innerHTML = e;
    list.appendChild(opt);
  });

  // Separator columns
  const colLeft = document.createElement('DIV');
  colLeft.classList.add('col');
  const colRight = document.createElement('DIV');
  colRight.classList.add('col');

  // Append all column elements
  col.appendChild(label);
  col.appendChild(list);

  // Append all row elements
  row.appendChild(colLeft);
  row.appendChild(col);
  row.appendChild(colRight);

  // Add label and list to form
  form.insertBefore(row, email);
};

createCountryList();