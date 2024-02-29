import axios from "axios";

let counter = 0;
const maxCounter = 600;
let resetTimeOnMouseMove = true;

function startTimer() {
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
const logout = async () => {
  try {
    await axios.get("/auth/logout");
    window.location.href = "/";
  } catch (error) {
    console.error("Error during logout:", error);
  }
};

export { startTimer };
