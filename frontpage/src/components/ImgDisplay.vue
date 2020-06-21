<template>
  <div class="img-display">
    <div class="display-region">
      <div class="empty">居然空空如也？属实没想到...</div>
      <img class="img" :src="info.url" preview="1" preview-text="居然空空如也？属实没想到..." />
    </div>
  </div>
</template>

<script>
export default {
  name:"ImgDisplay",
  props:{
    info:Object
  }
}
</script>

<style scoped lang="scss">
.display-region
{
  display:flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  .empty
  {
    font-family: "Verdana",youyuan;
    font-size:1.3rem;
    font-weight:bold;
    margin-bottom:20px;
  }
  .img
  {
    height:450px;
    border-radius:4px;
    box-shadow:0 0 6px rgb(90, 90, 90);
    cursor:pointer;
  }
}
</style>