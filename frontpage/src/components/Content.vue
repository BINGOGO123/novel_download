<template>
  <div class="content">
    <!-- 表示尚未搜索 -->
    <div v-if="displayType==0" class="transparent-block">
      <!-- 啥都没有就对了 -->
    </div>
    <!-- 表示搜索后内容错误 -->
    <div v-else-if="typeof(displayType)=='string'" class="error-display margin-bottom">
      <div class="middle-block">
        <div class="middle-title">ERROR</div>
        <div class="error-info">
          <b>原因：</b>
          <span>{{displayType}}</span>
        </div>
        <div class="error-info">
          <b>搜索内容：</b>
          <span>{{searchKey}}</span>
        </div>
        <div class="contact-author">联系作者：<b>416778940@qq.com</b></div>
      </div>
    </div>
    <!-- 表示搜索正确且存在结果 -->
    <div v-else-if="displayType==1" class="relative-block">
      <div class="display-block-title">
        <div class="part">
          当前搜索内容：<b>{{searchKey}}</b>
        </div>
        <div class="part">
          共有 <b>{{result.length}}</b> 条结果
        </div>
      </div>
      <DisplayBlock
      class="display-block"
      v-for="(item,index) in result.content"
      :key="index"
      :info="item"
      :source_name="result.source_name"
      :source_url="result.source_url"
      :source_img_url="result.source_img_url"
      :order="index"
      ></DisplayBlock>
      <div class="display-block-end">
        <Icon type="ios-loading" class="loading" :size="14.4" v-if="loading"/>
        <span :class="{blue:loading}">
          已显示 <span class="number">{{result.content.length}} / {{result.length}}</span>
        </span>
      </div>
    </div>
    <!-- 表示搜索正确但是没有结果 -->
    <div v-else class="margin-bottom">
      <ImgDisplay :info="result">
      </ImgDisplay>
    </div>
  </div>
</template>

<script>
import DisplayBlock from "./DisplayBlock.vue";
import ImgDisplay from "./ImgDisplay.vue";
import config from "../config.json";

export default {
  name:"Content",
  props:["result","searchKey","searching","active"],
  data:function(){
    return {
      loading:false,
      scrollAction:{
        x:undefined,
        y:undefined
      },
      scrollDirection:"no"
    }
  },
  created:function(){
    // 定位目前的位置
    this.scrollAction.x = window.pageXOffset;
    this.scrollAction.y = window.pageYOffset;
    // 绑定事件
    window.addEventListener("scroll",()=>{
      // 只有在搜索过且有结果时才会触发
      this.scrollFunc();
      // 是否已经处于底端
      if(this.getScrollTop() + this.getWindowHeight() == this.getScrollHeight())
        // 除此之外还需要满足当前content正在显示，不在搜索状态，必须是有信息的展示页面，必须是往下滑，还有尚未加载的数据，不是正在加载中
        if(this.active && !this.searching && this.displayType==1 && this.scrollDirection=="down" && this.result.end==false && !this.loading)
        {
          this.loading = true;
          // console.log(this.result);
          // console.log(this.result.end);
          new Promise((resolve)=>{
            this.getMore(resolve,this.result.source_name);
          }).finally(()=>{
            this.loading=false;
          });
        }
    });
  },
  computed:{
    displayType:function(){
      if(typeof(this.result) == "string")
        return this.result;
      else if(this.result == null)
        return 0;
      else if(this.result instanceof Error)
        return String(this.result);
      else if(this.result.status == config.error)
        return this.result.information;
      else if(!this.result.empty)
        return 1;
      else
        return 2;
    }
  },
  methods:{
    getScrollTop:function(){
      var scrollTop = 0, bodyScrollTop = 0, documentScrollTop = 0;
      if(document.body){
        bodyScrollTop = document.body.scrollTop;
      }
      if(document.documentElement){
        documentScrollTop = document.documentElement.scrollTop;
      }
      scrollTop = (bodyScrollTop - documentScrollTop > 0) ? bodyScrollTop : documentScrollTop;
      return scrollTop;
    },
    getScrollHeight:function(){
      let scrollHeight = 0;
      let bSH,dSH
      if(document.body)
        bSH = document.body.scrollHeight;
      if(document.documentElement)
        dSH = document.documentElement.scrollHeight;
      scrollHeight = (bSH - dSH > 0) ? bSH : dSH ;
      return scrollHeight;
    },
    getWindowHeight:function(){
      let windowHeight = 0;
      if(document.compatMode == "CSS1Compat")
        windowHeight = document.documentElement.clientHeight;
      else
        windowHeight = document.body.clientHeight;
      return windowHeight;
    },
    scrollFunc:function(){
      if (typeof this.scrollAction.x== 'undefined') {
        this.scrollAction.x = window.pageXOffset;
        this.scrollAction.y = window.pageYOffset;
      }
      var diffX = this.scrollAction.x - window.pageXOffset;
      var diffY = this.scrollAction.y - window.pageYOffset;
      if (diffX < 0) {
        // Scroll right
        this.scrollDirection = 'right';
      } else if (diffX > 0) {
        // Scroll left
        this.scrollDirection = 'left';
      } else if (diffY < 0) {
        // Scroll down
        this.scrollDirection = 'down';
      } else if (diffY > 0) {
        // Scroll up
        this.scrollDirection = 'up';
      } else {
        // First scroll event
        this.scrollDirection = "no";
      }
      this.scrollAction.x = window.pageXOffset;
      this.scrollAction.y = window.pageYOffset;
    }
  },
  inject:[
    "getMore"
  ],
  components:{
    DisplayBlock,
    ImgDisplay
  }
}
</script>

<style scoped lang="scss">
.content
{
  padding:20px 20px 1px 20px;
  position:relative;
}
.error-display
{
  display:flex;
  flex-direction: row;
  justify-content: center;
  .middle-block
  {
    box-shadow:0 0 4px rgb(201, 158, 158);
    // box-shadow:0 0 6px rgb(0, 0, 0);
    background-color:rgb(255, 230, 230);
    // background-color:rgba(0, 0, 0, 0.89);
    // background-color:#F1F2F9;
    padding:0 8px 0 8px;
    width:100%;
    border-radius:2px;
    .middle-title
    {
      color:rgb(221, 66, 66);
      font-weight:bold;
      font-size:2rem;
      font-family: "Century Gothic",youyuan;
    }
    .error-info
    {
      font-size:1.1rem;
      font-family: "Verdana",youyuan;
      // color:rgb(221, 221, 221);
    }
    .contact-author
    {
      font-size:0.9rem;
      font-family: "Verdana",youyuan;
      margin-top:10px;
      margin-bottom:8px;
      color:#6c7c9e;
      text-align: right;
    }
  }
}
.margin-bottom
{
  margin-bottom:15px;
}
.transparent-block
{
  background-color:transparent;
  // background-color:#F1F2F9;
}
.display-block-title
{
  display:flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  font-family:"Verdana",youyuan;
  font-size:0.9rem;
  margin-bottom:20px;
  .part
  {
    margin-right:20px;
    // background-color:white;
    // padding:4px;
    // border-radius: 3px;
    // box-shadow:0 0 6px rgb(244, 225, 248);
  }
}
.display-block
{
  margin-bottom:20px;
}
.display-block-end
{
  text-align:center;
  margin-bottom:10px;
  font-family: "Verdana",youyuan;
  font-size:.9rem;
  .loading
  {
    color:rgb(43, 117, 255);
  }
  .number
  {
    // font-weight:bold;
  }
  .loading,.blue
  {
    color:rgb(43, 117, 255);
  }
}
.loading
{
  animation: ani-spin 1s linear infinite;
}
@keyframes ani-spin {
  from { transform: rotate(0deg);}
  50%  { transform: rotate(180deg);}
  to   { transform: rotate(360deg);}
}
</style>