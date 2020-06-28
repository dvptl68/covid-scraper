// Function to set element positions
const setPositions = () => {

  // Get elements that need to be styled
  const titleBlock = document.getElementById('title-block');
  const infoBlock = document.getElementById('info-block');
  const formBlock = document.getElementById('selection-block');

  // Set vertical position of elements
  infoBlock.style.top = `${titleBlock.clientHeight}px`;
  formBlock.style.top = `${titleBlock.clientHeight + infoBlock.clientHeight + 50}px`
};

// Set initial position of elements
// setPositions();

// Set position of elements on window resize
// window.onresize = setPositions;