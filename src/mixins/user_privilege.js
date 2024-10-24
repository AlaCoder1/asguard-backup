const retriveInfo = localStorage.getItem("user-info");
const user_role = JSON.parse(retriveInfo).currentUser;

function user_privilege(service) {

  let given_acces = null;

  if (user_role.role === 'admin') given_acces = 'see_all'
  else if (user_role.role === 'viewer') given_acces = 'viewer'
  else if (user_role.role === 'default') given_acces = 'default'

  else {
    if (user_role.list_fonctionalities) {
      const validArray = user_role.list_fonctionalities.replace(/'/g, '"');
      let list_func = JSON.parse(validArray);

      if (list_func.includes(service)) given_acces = true
      else given_acces = false
    }
    else given_acces = false
  }

  return given_acces;
}

export { user_privilege };