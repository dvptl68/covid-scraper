// Function to set element positions
const setPositions = () => {

  // Get elements that need to be styled
  const titleBlock = document.getElementById('title-block');
  const infoBlock = document.getElementById('info-block');
  const mainContainer = document.getElementById('main-container');

  // Set vertical position of elements
  infoBlock.style.top = `${titleBlock.clientHeight}px`;
  mainContainer.style.top = `${titleBlock.clientHeight + infoBlock.clientHeight}px`
};

// Set initial position of elements
setPositions();

// Set position of elements on window resize
window.onresize = setPositions;