import axios from "axios";
import { getCookie } from "@/mixins/csrftoken.js";

const csrfToken = getCookie("csrftoken");
axios.defaults.headers.common["X-CSRFToken"] = csrfToken;

let user = localStorage.getItem("user-info");
const user_data = JSON.parse(user);
let id = user_data?.currentUser?.id;

async function get_lang() {
  let lang = null;
  try {
    let res = await axios.get(`/users/getLanguage/${id}`);
    lang = res.data.language;
    localStorage.setItem("lang", lang.toLowerCase());
    return lang;
  } catch (error) {
    console.error(error);
  }
}
get_lang();

export { get_lang, id };
