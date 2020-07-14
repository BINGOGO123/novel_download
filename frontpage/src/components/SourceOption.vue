<template>
  <div class="source-option">
    <template v-if="result instanceof Array">
      <div class="option">
        <span><b>来源：</b></span>
        <ul>
          <li v-for="(item,index) in result" :key="'li'+index" :class="{active:index==order}"
          @click="order=index">
            {{item.source_name}}
          </li>
        </ul>
      </div>
      <Content
      v-for="(item,index) in result"
      :key="index"
      v-show="order==index"
      class="content"
      :searchKey="searchKey"
      :searching="searching"
      :result="item"
      :active="index==order"
      >
      </Content>
    </template>
    <Content v-else
    class="content"
    :result="result"
    :searchKey="searchKey"
    :searching="searching"
    :active="true">
    </Content>
    <Spin size="large" fix v-if="searching"></Spin>
  </div>
</template>

<script>
import Content from "./Content.vue";

export default {
  name:"SourceOption",
  props:["result","searchKey","searching"],
  data:function(){
    return {
      order:0
    }
  },
  components:{
    Content
  }
}
</script>

<style scoped lang="scss">
.option::-webkit-scrollbar
{
  height:2px;
}
.option::-webkit-scrollbar-thumb
{
  border-radius:0px;
  border-radius:100px;
  background-color:rgb(118, 173, 255);
}
.option
{
  padding:10px 20px 10px 20px;
  width:100%;
  display:flex;
  flex-shrink: 0;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  font-family: "Verdana",youyuan;
  font-size:1rem;
  background-color:rgb(215, 229, 255);
  overflow-x:scroll;
  span
  {
    flex-shrink: 0;
  }
  ul
  {
    display:flex;
    flex-direction: row;
    justify-content: flex-start;
    align-items: center;
    li
    {
      list-style:none;
      padding:1px 5px 1px 5px;
      color:rgb(47, 115, 218);
      cursor:pointer;
      margin-left:5px;
      margin-right:5px;
      border-radius:4px;
      -webkit-user-select: none;
      flex-shrink: 0;
    }
    li.active
    {
      background-color:rgb(47, 115, 218);
      // background-color:rgb(211, 98, 22);
      color:white;
    }
  }
}
.source-option
{
  display:flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
  .content
  {
    flex:1;
  }
  position:relative;
}

</style>