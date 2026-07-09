document.addEventListener("DOMContentLoaded", () => {
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const statusBadge = document.getElementById("statusBadge");
  const apiUrlInput = document.getElementById("apiUrl");
  const candidateNameInput = document.getElementById("candidateName");
  const logBox = document.getElementById("logBox");

  function log(msg) {
    const p = document.createElement("div");
    p.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    logBox.appendChild(p);
    logBox.scrollTop = logBox.scrollHeight;
  }

  startBtn.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url.includes("meet.google.com")) {
      log("Error: Please open a live Google Meet tab first!");
      return;
    }

    startBtn.style.display = "none";
    stopBtn.style.display = "block";
    statusBadge.textContent = "Live";
    statusBadge.classList.add("active");

    log("Injecting bridge script into Google Meet...");
    chrome.tabs.sendMessage(tab.id, {
      action: "START_CAPTURE",
      apiUrl: apiUrlInput.value,
      candidateName: candidateNameInput.value,
    });
  });

  stopBtn.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      chrome.tabs.sendMessage(tab.id, { action: "STOP_CAPTURE" });
    }

    startBtn.style.display = "block";
    stopBtn.style.display = "none";
    statusBadge.textContent = "Idle";
    statusBadge.classList.remove("active");
    log("Capture stopped.");
  });
});
