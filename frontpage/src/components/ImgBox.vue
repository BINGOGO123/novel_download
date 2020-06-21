<template>
  <div class="image-box">
    <div class="image-display">
      <img :src="imageList[selected]" ref="img" :class="{animated:true,'raw-image':rawImage}" alt="图片无法显示" preview="1"/>
    </div>
    <div class="select">
      <div class="option" v-for="(image,index) in imageList" :key="index">
        <!-- <i :class="{fa:true,'fa-circle':index==selected,'fa-circle-thin':index!=selected}"></i> -->
        <span :class="{fa:true,circle:index==selected,'circle-thin':index!=selected}" @click="convert(index)"></span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name:"ImgBox",
  props:{
    imageList:{
      type:Array,
      required:false
    },
    rawImage:{
      type:Boolean,
      default:false
    }
  },
  data:function(){
    return {
      selected:0
    }
  },
  methods:{
    convert:function(order){
      // 如果选择的按钮和目前selected相同则直接返回
      if(order == this.selected)
        return;
      // this.$refs.img.className = "animated rollOut"
      // this.$refs.img.className = "animated rollIn"
      this.selected = order; 
    }
  }
}
</script>

<style scoped>
.image-box .image-display img
{
  max-height:100%;
  height:475px;
  margin:0 auto;
  display:block;
  box-shadow:0 0 6px rgb(200,200,200);
  border-radius:4px;
  cursor:pointer;
}

.image-box .image-display img.raw-image
{
  height:auto;
}

.image-box .select
{
  display:flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-top:15px;
}

.image-box .select .option
{
  margin-right:15px;
}

.image-box .select .option .fa
{
  display:inline-block;
  background-color:rgb(78, 102, 180);
  height:10px;
  width:10px;
  border-radius:100px;
  cursor:pointer;
}

.image-box .select .option .fa.circle-thin
{
  background-color:white;
  border:1px solid rgb(78, 102, 180);
}

</style>