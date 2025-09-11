import axios from "axios";
import { get_params } from "@/mixins/params.js";

let counter = 0;
let maxCounter = null;
let resetTimeOnMouseMove = true;

function initTimer() {
  setInterval(() => {
    if (counter < maxCounter) {
      counter++;
    } else {
      logout();
    }
  }, 1000);

  if (resetTimeOnMouseMove) {
    document.addEventListener("mousemove", () => {
      counter = 0;
    });

    document.addEventListener("keypress", () => {
      counter = 0;
    });
  }
}

async function startTimer() {
  const params = await get_params();
  if (params?.session_timeout) {
    maxCounter = Number(params.session_timeout);
  } else {
    maxCounter = 600;
  }
  initTimer();
}

const logout = async () => {
  try {
    await axios.get("/auth/logout");
    window.location.href = "/";
  } catch (error) {
    console.error("Error during logout:", error);
  }
};

export { startTimer };
