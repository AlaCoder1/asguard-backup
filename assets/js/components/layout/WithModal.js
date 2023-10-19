import Vue from 'vue';

function WithModal(WrappedComponent) {
  // We will return a new component that renders WrappedComponent
  return Vue.extend({
    created() {
      console.log('HOC component created');
    },
  
    render(createElement) {
      return createElement(WrappedComponent);
    }
  });
}

export default WithModal;
