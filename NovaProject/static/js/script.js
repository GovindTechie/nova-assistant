/*
 * script.js
 *
 * This file manages UI interactions for NOVA Assistant.
 * It updates the result text with a fade-in effect, attaches event handlers
 * to persistent control buttons, processes voice and manual command submissions,
 * fetches Google-like search suggestions for "search" commands, and handles
 * autocompletion using the Tab key.
 */

// Wait for the DOM to load before attaching event handlers.
document.addEventListener("DOMContentLoaded", function() {
  attachResultControlEvents();
});

// Global variable to store the AbortController for fetch requests.
let currentController = null;

/**
 * Update the result text in the result box with a fade-in effect.
 * @param {string} text - The text to display.
 */
function updateResult(text) {
  const resultText = document.getElementById("resultText");
  resultText.style.opacity = 0; // Fade out.
  setTimeout(() => {
    resultText.innerText = text;
    resultText.style.opacity = 1; // Fade in.
  }, 100);
}

/**
 * Attach event listeners to persistent copy and clear buttons.
 */
function attachResultControlEvents() {
  const copyBtn = document.getElementById("copyResult");
  const clearBtn = document.getElementById("clearResult");
  
  // Copy button: Copy result text to clipboard.
  if (copyBtn) {
    copyBtn.addEventListener("click", function() {
      const fullText = document.getElementById("resultText").innerText;
      navigator.clipboard.writeText(fullText).then(() => {
        alert("Response copied to clipboard!");
      });
    });
  }
  
  // Clear button: Clear the result text.
  if (clearBtn) {
    clearBtn.addEventListener("click", function() {
      updateResult("");
    });
  }
}

/**
 * Update the interaction instruction text.
 * @param {string} text - The text to display.
 */
function updateInteraction(text) {
  document.getElementById("interactionText").innerText = text;
}

/**
 * Fetch Google search suggestions via the /suggest endpoint.
 * @param {string} query - The search query.
 */
function fetchSuggestions(query) {
  fetch(`/suggest?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      // data format is [query, [suggestion1, suggestion2, ...], ...]
      if (data && data[1]) {
        showSuggestions(data[1]);
      }
    })
    .catch(error => console.error("Error fetching suggestions:", error));
}

/**
 * Display suggestions in the suggestions dropdown.
 * @param {Array} suggestions - Array of suggestion strings.
 */
function showSuggestions(suggestions) {
  const suggestionsDiv = document.getElementById("suggestions");
  suggestionsDiv.innerHTML = ""; // Clear old suggestions.
  suggestions.forEach(s => {
    const div = document.createElement("div");
    div.classList.add("suggestion-item");
    div.innerText = s;
    // On click, fill the input with "search " plus the suggestion.
    div.addEventListener("click", function() {
      document.getElementById("manualCommand").value = "search " + s;
      clearSuggestions();
    });
    suggestionsDiv.appendChild(div);
  });
}

/**
 * Clear the suggestions dropdown.
 */
function clearSuggestions() {
  document.getElementById("suggestions").innerHTML = "";
}

// Event handler for manual command input to fetch suggestions when a "search" command is detected.
const manualCommandInput = document.getElementById("manualCommand");
manualCommandInput.addEventListener("keyup", function(e) {
  const value = this.value;
  // If the command starts with "search " (case-insensitive), fetch suggestions.
  if (value.toLowerCase().startsWith("search ")) {
    const parts = value.split(" ");
    if (parts.length > 1) {
      const query = parts.slice(1).join(" ");
      fetchSuggestions(query);
    }
  } else {
    clearSuggestions();
  }
});

/**
 * Handle keydown event on the manual command input.
 * If the user presses Tab while suggestions are available,
 * prevent the default Tab behavior and autocomplete with the first suggestion.
 */
manualCommandInput.addEventListener("keydown", function(e) {
  if (e.key === "Tab") {
    const suggestionsDiv = document.getElementById("suggestions");
    if (suggestionsDiv && suggestionsDiv.children.length > 0) {
      // Prevent default Tab behavior.
      e.preventDefault();
      // Get the first suggestion.
      const firstSuggestion = suggestionsDiv.children[0].innerText;
      // Insert "search " plus the suggestion into the input.
      this.value = "search " + firstSuggestion;
      // Clear the suggestions dropdown.
      clearSuggestions();
    }
  }
});

// Event handler for the microphone button (voice commands).
document.getElementById("micButton").addEventListener("click", function() {
  updateInteraction("Speak now...");
  updateResult("");
  currentController = new AbortController();
  // Send a POST request to the /listen endpoint.
  fetch("/listen", { 
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
    signal: currentController.signal
  })
  .then(response => response.json())
  .then(data => {
    updateResult(data.result);
    document.getElementById("sendCommand").innerText = "Send";
  })
  .catch(error => {
    if (error.name === 'AbortError') {
      updateResult("Response generation stopped.");
    } else {
      updateResult("An error occurred. Please try again later.");
      console.error("Error:", error);
    }
    document.getElementById("sendCommand").innerText = "Send";
  });
});

// Event handler for the Stop Speech button.
document.getElementById("stopSpeechButton").addEventListener("click", function() {
  fetch("/stop_speech", { method: "POST" })
    .then(response => response.json())
    .then(data => {
      alert(data.result); // Notify the user.
    })
    .catch(error => {
      console.error("Error stopping speech:", error);
    });
});

/**
 * Send a manual command to the server.
 */
function sendManualCommand() {
  let commandText = manualCommandInput.value;
  if (!commandText) return;
  
  updateInteraction("Processing command...");
  updateResult("");
  const sendBtn = document.getElementById("sendCommand");
  sendBtn.innerText = "Stop";
  
  // Special case for "who are you?" command.
  if (commandText.trim().toLowerCase() === "who are you?") {
    const intro = "Hello, I'm Nova Desk – your next-generation AI companion and virtual assistant integrated with Gemini. Developed by Govind Khedkar in Beed, Maharashtra. How can I help you today?";
    updateResult(intro);
    sendBtn.innerText = "Send";
    return;
  }
  
  currentController = new AbortController();
  fetch("/command", { 
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ command: commandText }),
    signal: currentController.signal
  })
  .then(response => response.json())
  .then(data => {
    updateResult(data.result);
    sendBtn.innerText = "Send";
  })
  .catch(error => {
    if (error.name === 'AbortError') {
      updateResult("Response generation stopped.");
    } else {
      updateResult("An error occurred. Please try again later.");
      console.error("Error:", error);
    }
    sendBtn.innerText = "Send";
  });
}

// Click handler for the Send/Stop button.
document.getElementById("sendCommand").addEventListener("click", function() {
  const btn = document.getElementById("sendCommand");
  if (btn.innerText === "Stop" && currentController) {
    currentController.abort();
  } else {
    sendManualCommand();
  }
});

// Allow submission of manual command via the Enter key.
manualCommandInput.addEventListener("keydown", function(e) {
  if (e.key === "Enter") {
    sendManualCommand();
  }
});
