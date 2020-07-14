import Vue from 'vue';
import App from './App.vue';
import VueRouter from 'vue-router';
import ViewUI from "view-design";
import 'view-design/dist/styles/iview.css';
import animated from 'animate.css'
import preview from 'vue-photo-preview'
import 'vue-photo-preview/dist/skin.css'

import Search from "./components/Search.vue";
// import Content from "./components/Content.vue";
import Http404 from "./components/Http404.vue";
import SourceOption from "./components/SourceOption.vue";

Vue.use(animated);
Vue.use(ViewUI);
Vue.use(VueRouter);
Vue.use(preview)

Vue.directive('focus', {
  // 当被绑定的元素插入到 DOM 中时……
  inserted: function (el) {
    // 聚焦元素
    el.focus()
  }
});

const routes = [
  {
    path:"/",
    component:Search,
    name:"search",
    children:[
      {
        path:"/:content",
        component:SourceOption,
        name:"content"
      }
    ]
  },
  {
    path:"*",
    component:Http404
  }
];

Vue.config.productionTip = false
const router = new VueRouter({routes});

new Vue({
  router,
  render: h => h(App),
  directives: {
    focus: {
      // 指令的定义
      inserted: function (el) {
        el.focus()
      }
    }
  }
}).$mount('#app');
