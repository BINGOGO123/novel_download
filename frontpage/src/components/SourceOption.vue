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
  methods:{
    getSourceName:function(result){
      if(result == null)
        return null;
      else if((typeof(result) == "string") || (result instanceof Error))
        return null;
      else if(result instanceof Array)
      {
        return result.map(value => {
          return value.source_name;
        });
      }
      else
      {
        if(result.source_name != undefined)
          return result.source_name;
        else
          return null;
      }
    }
  },
  watch:{
    result:function(new_result,old_result){
      let old_source_name = this.getSourceName(old_result);
      let new_source_name = this.getSourceName(new_result);
      // 两方有一方没有source_name，那么order调整为0
      if(old_source_name == null || new_source_name == null)
        this.order = 0;
      // 新方是单项，那么order调整为0
      else if(!(new_source_name instanceof Array))
        this.order = 0;
      else {
        if(old_source_name instanceof Array)
          old_source_name = old_source_name[this.order];
        let new_order = new_source_name.indexOf(old_source_name);
        this.order = new_order >=0 ? new_order : 0;
      }
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