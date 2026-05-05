import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";

const csrfToken = getCookie("csrftoken");
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

async function get_params() {
  let setting = {};
  try {
    let res = await axios.get("/settings/getSettings");
    const { password_length, session_timeout } = res.data;
    setting = { password_length, session_timeout };
    return setting;
  } catch (error) {
    console.error(error);
  }
}
get_params();

export { get_params };
