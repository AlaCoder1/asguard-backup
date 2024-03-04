function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const trimmedCookie = cookie.trim();
      if (trimmedCookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(
          trimmedCookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}

export { getCookie };
