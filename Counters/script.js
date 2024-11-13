// Maksimalt antall tellere
const maxCounters = 5;

// Funksjon for å opprette tellere med input for navngivning
function createCounter() {
  const counterDiv = document.createElement("div");
  counterDiv.className = "counter";

  // Input for navn på telleren
  const nameInput = document.createElement("input");
  nameInput.className = "counter-input";
  nameInput.placeholder = "Navn på teller";

  // Element for å vise navnet
  const counterName = document.createElement("span");
  counterName.className = "counter-name";

  // Lytte til endringer i input-feltet og oppdatere navnet
  nameInput.addEventListener("input", () => {
    counterName.textContent = nameInput.value + ":";
  });

  // Telleren verdi
  const counterValue = document.createElement("span");
  counterValue.className = "counter-value";
  counterValue.textContent = "0";

  // Knapp for å øke telleren
  const incrementButton = document.createElement("button");
  incrementButton.textContent = "+";
  incrementButton.addEventListener("click", () => {
    counterValue.textContent = parseInt(counterValue.textContent) + 1;
  });

  counterDiv.appendChild(nameInput);
  counterDiv.appendChild(counterName);
  counterDiv.appendChild(counterValue);
  counterDiv.appendChild(incrementButton);

  document.getElementById("counters").appendChild(counterDiv);
}

// Opprette fem tellere
for (let i = 0; i < maxCounters; i++) {
  createCounter();
}
