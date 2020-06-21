<template>
  <div class="test">
    <div class="block animate__animated animate__bounce">
    </div>
    <h1 class="animate__animated animate__infinite animate__bounce animate__delay-2s">Example</h1>
    <h1 class="animate__animated animate__backOutLeft">Example</h1>
    <div class="animate__animated animate__bounceInDown">bounceInDown</div>
  </div>
</template>

<script>
export default {
  name:"Test"
}
</script>

<style lang="scss" scoped>
.block
{
  width:100px;
  height:100px;
  background-color:blue;
  position:absolute;
  top:300px;
  left:300px;
}

// @keyframes move {
//   to {
//     left:400px;
//     top:100px;
//   }
// }

// .bb
// {
//   animation: move 0.5s;
// }

// .bb-leave-active
// {
//   animation: move 0.5s;
// }
</style>