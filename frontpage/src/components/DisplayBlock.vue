<template>
  <div class="item-display">
    <div class="info-display">
      <div class="title-line">
        <div class="title">{{info.name}}</div>
        <div class="button-div">
          <button v-if="info.download_url" @click="download(order)" class="enter-button" :class="{downloading:downloading}" :disabled="downloading">
            <span class="enter" title="download" v-if="!downloading">
              <span>下载整本&nbsp;&nbsp;</span>
              <Icon class="icon" type="md-arrow-round-down" :size="20"/>
            </span>
            <span class="enter" title="download" v-else>
              <span>下载整本&nbsp;&nbsp;</span>
              <Icon class="icon loading" type="ios-loading" :size="20"/>
            </span>
          </button>
          <transition enter-active-class="animate__animated animate__flipInY" leave-active-class="animate__animated animate__flipOutY">
            <div class="time-alert" v-if="downloading">
              大约还需{{time_interval}}s
            </div>
          </transition>
        </div>
      </div>
      <hr />
      <div class="introduction">
        <div>
          <template v-for="(line,index) in info.introduction" >
            {{line}}
            <br :key="index"/>
          </template>
        </div>
        <a :href="info.download_url" target="_blank" class="source">
          <img v-if="info.source_img_url" :src="info.source_img_url" />
          <span>资源来源于{{info.source_name}}</span>
        </a>
      </div>
      <ImgBox
      v-if="opened"
      :imageList="info.imageList"
      :rawImage="false"
      class="img-box"
      ></ImgBox>
    </div>
    <div
    :class="{'open-button':true,opened:opened,'no-img':info.imageList==undefined||info.imageList.length==0}"
    @click="open">
      <!-- <i :class="{fa:true,'fa-angle-double-down':!opened,'fa-times':opened}"></i> -->
      <Icon v-if="!opened" class="fa fa-open" type="ios-arrow-down"/>
      <Icon v-else class="fa" type="md-close" />
    </div>
    <div class="order" :class="{'small-order':display_order.length==3,'mini-order':display_order.length>3}">
      <i>{{display_order}}</i>
    </div>
  </div>
</template>

<script>
import ImgBox from "./ImgBox.vue";
export default {
  name:"DisplayBlock",
  props:{
    info:Object,
    order:Number
  },
  data:function(){
    return {
      opened:false
    };
  },
  methods:{
    open:function(){
      this.opened=!this.opened;
    }
  },
  inject:[
    "download"
  ],
  computed:{
    downloading:function(){
      if(this.info.downloading==undefined)
        return false;
      return this.info.downloading;
    },
    time_interval:function(){
      if(this.info.process == undefined)
        return " ? ";
      else if(this.info.process > 999)
        return "999";
      return this.info.process;
    },
    display_order:function(){
      if(this.order > 998)
        return "999+"
      return String(this.order + 1)
    }
  },
  components:{
    ImgBox
  }
}
</script>

<style scoped lang="scss">
.item-display,.item-display *
{
  box-sizing:border-box;
}

.item-display
{
  padding:0;
  margin-bottom:20px;
  display:flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items:flex-start;
  position:relative;
  .info-display
  {
    box-shadow:0 0 6px rgb(244, 225, 248);
    padding:15px;
    width:100%;
    border-radius:25px 4px 4px 4px;
    background-color:white;
    z-index:1;
    .title-line
    {
      display:flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      .title
      {
        color:#444444;
        font-weight:normal;
        padding:0 0 5px 0;
        margin:0;
        position: relative;
        font-size:1.1rem;
        font-weight:bold;
        border-bottom:2px solid #444444;
        display:inline-block;
        z-index:1;
        margin-left:50px;
      }
      .enter-button
      {
        outline:none;
        border:none;
        transition: all 0.5s;
        font-size:1.1rem;
        cursor:pointer; 
        background-color:rgb(47, 115, 218);
        color:white;
        padding:0px 5px 1px 5px;
        border-radius: 4px 25px 25px 4px;
        z-index:2;
      }
      .enter-button:hover
      {
        background-color:rgb(51, 68, 124);
        .icon
        {
          color:rgb(51, 68, 124);
        }
      }
      .enter-button .enter
      {
        display:flex;
        flex-direction: row;
        justify-content: space-around;
        align-items: center;
        span
        {
          margin-right:5px;
        }
      }
      .enter-button.downloading
      {
        background-color:rgb(66, 168, 66);
        cursor:unset;
      }
      .enter-button.downloading:hover
      {
        background-color:rgb(66, 168, 66);
        .icon
        {
          color:white;
        }
      }
      .icon
      {
        color:rgb(47, 115, 218);
        background-color:white;
        border-radius:100px;
        transition: all 1s;
      }
      .icon.loading
      {
        color:white;
        background-color:transparent;
      }
      .button-div
      {
        position:relative;
        .time-alert
        {
          position:absolute;
          height:28px;
          line-height:28px;
          width:85px;
          text-align: center;
          font-size:0.7rem;
          font-family: "Verdana",youyuan;
          background-color:rgb(209, 54, 54);
          // background-color:rgb(182, 89, 86);
          color:white;
          bottom:-28px;
          left:5px;
          z-index:1;
          padding:0 5px 0 5px;
          border-radius:0 0 4px 4px;
        }
      }
    }
    hr
    {
      margin:0;
      height:2px;
      background-color:rgb(247, 249, 252);
      border:none;
      position: relative;
      top:-2px;
    }
  }
}

.item-display .introduction
{
  color:rgb(100, 100, 100);
  font-size:1rem;
  line-height: 28px;
  overflow-y:hidden;
  margin:0 ;
  background-color:#f5f5f5;
  padding:6px 10px 6px 10px;
  margin:10px 0 0 0;
  border-radius:4px;
  max-height:150px;
  font-family: "Verdana",youyuan;

  .source
  {
    display:inline-flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    img
    {
      // width:18px;
      height:18px;
      margin-right:3px;
      // box-shadow:0 0 1px rgb(92, 92, 92);
    }
  }
}

.item-display .introduction-span
{
  color:#A1A7B7;
}

.item-display .open-button
{
  margin-top:40px;
  padding:10px 15px 10px 10px;
  font-size:1.1rem;
  background-color:rgb(233, 75, 70);
  background-color:rgb(209, 54, 54);
  color:white;
  border-radius:0 100px 100px 0;
  box-shadow:0 0 6px rgb(244, 225, 248);
  cursor:pointer;
}
.item-display .open-button.no-img
{
  visibility: hidden;
}

.item-display .open-button.opened
{
  background-color:rgb(47, 115, 218);
}

.item-display .open-button:hover
{
  background-color:rgb(199, 33, 27);
}

.item-display .open-button.opened:hover
{
  background-color:rgb(78, 102, 180);
}

.img-box
{
  margin-top:10px;
}

@keyframes flash
{
  from
  {
    opacity:1;
    top:-2px;
  }
  to
  {
    opacity:0;
    top:2px;
  }
}

.item-display .fa.fa-open
{
  animation:flash infinite 1s;
  position:relative;
}

.item-display .order
{
  position:absolute;
  font-size:2rem;
  height:50px;
  width:50px;
  text-align: center;
  line-height: 50px;
  top:0px;
  left:0px;
  z-index:1;
  background-color:rgb(211, 98, 22);
  border-radius:100px;
  font-family:"Verdana",youyuan;
  // font-weight:bold;
  color:white;
}
.order.small-order
{
  font-size:1.5rem;
}
.order.mini-order
{
  font-size:1rem;
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