<template>
  <div class="search">
    <transition name="first" leave-active-class="animate__animated animate__fadeOut">
      <div v-if="searchPage" class="first-page">
      <!-- <div v-if="searchPage" :class="{'first-page':true,'animate__animated':true,'animate__fadeOut':searched}"> -->
        <div class="search-item">
          <div class="introduction">
            <div class="title">
              多站小说下载器
            </div>
            <div class="detail">
              本网站仅供交流学习使用，请勿用作他用
            </div>
          </div>
          <div class="search-line">
            <input class="search-input"
            v-model.trim="content"
            placeholder="请输入小说名称"
            v-focus :maxlength="100"
            @keyup.enter="search"/>
            <button class="search-button" @click="search">
              <Icon type="md-search" :size="25"/>
            </button>
          </div>
          <div class="loading-region" v-if="searching">
            <!-- <Spin size="1000" class="loading"></Spin> -->
            <Icon type="ios-loading" class="loading" size="50"/>
            <span class="loading-word">{{searchText}}</span>
          </div>
        </div>
        <Link class="link"/>
      </div>
    </transition>
    <transition name="second" enter-active-class="animate__animated animate__fadeInDownBig">
      <div v-if="!searchPage" class="second-page">
      <!-- <div v-if="!searchPage" :class="{'second-page':true,'animate__animated':true,'animate__zoomInDown':searched}" > -->
        <div class="nav">
          <div class="logo" @click="$router.push({name:'search'})">
            多站小说下载器
          </div>
          <div :class="{'search-line':true,'search-line-focus':searchLineFocus}">
            <input
            class="search-input"
            v-model.trim="content"
            placeholder="请输入小说名称"
            :maxlength="100"
            v-focus @focus="searchLineFocus=true"
            @blur="searchLineFocus=false"
            @keyup.enter="search"
            />
            <button class="search-button" @click="search">
              <Icon type="md-search" :size="20" v-if="!searching" class="search-button-icon"/>
              <Icon type="ios-loading" class="loading search-button-icon" :size="20" v-else />
            </button>
          </div>
        </div>
        <router-view
        class="display-region"
        :result="result"
        :searchKey="presentKey"
        :searching="searching"
        @getMore="getMore"
        ></router-view>
        <!-- <Link class="link"/> -->
      </div>
    </transition>
    <BackTop :bottom="0" :right="0">
      <Icon type="ios-arrow-up" class="top"/>
    </BackTop>
  </div>
</template>

<script>
import Link from "./Link.vue";
import config from "../config.json";

export default {
  name:"Search",
  data:function(){
    return {
      content:"",
      searching:false,
      result:null,
      presentKey:"",
      controller:null,
      searchText:"搜索中",
      searchTextClock:null,
      searchLineFocus:false,
      download_url:config.download_url
    }
  },
  watch:{
    searching:function(value){
      // 必须要是search路由才需要这样做
      if(this.searchPage && value)
      {
        this.searchTextClock = setInterval(()=>{
          if(this.searchText.length >= 6)
            this.searchText = "搜索中";
          else
            this.searchText += ".";
        },500);
      }
      else if(this.searchTextClock!=null)
      {
        clearInterval(this.searchTextClock);
        this.searchText = "搜索中";
        this.searchTextClock = null;
      }
    }
  },
  // 直接通过修改url进行搜索
  beforeRouteUpdate :function(to,from,next){
    // console.log(to)
    // console.log(from)
    // console.log(this.$route)
    // 从content跳转到search
    if(from.name=="search" && to.name=="content")
    {
      // 当前搜索结果与跳转页面的url一致，说明是通过搜索功能成功进行跳转的，不必再次搜索
      // 还有一种可能就是从content路由返回到search路由
      if(this.presentKey == to.params.content)
        next();
      // 否则说明是直接通过url更改进行的跳转，那么我们先搜索再看情况
      else
      {
        this.content = to.params.content.trim();
        this.search();
      }
    }
    // 从content跳往search，这种情况下不可能是搜索跳转只能是更改url的跳转
    else if(from.name=="content" && to.name=="search")
    {
      // 这里把所有的信息全部还原
      if(this.searching && this.controller != null)
        this.controller.abort();
      this.controller=null;
      this.searching=false;
      this.content="";
      this.presentKey="";
      this.result=null;
      this.searchText="搜索中";
      this.searchTextClock=null;
      next();
    }
    // 如果是content跳往content
    if(to.name=="content" && from.name=="content")
    {
      // 当前搜索结果与跳转页面的url一致，说明是通过搜索功能成功进行跳转的，不必再次搜索
      if(this.presentKey == to.params.content)
        next();
      // 否则说明是通过更改url的方式进行跳转的，那么我们先搜索再看情况
      else
      {
        this.content=to.params.content.trim();
        this.search();
      }
    }
  },
  computed:{
    searchPage:function(){
      if(this.$route.name=="search")
        return true;
      else if(this.$route.name=="content")
        return false;
      else
        return false;
    }
  },
  // 如果是content路由，那么需要搜索内容
  created:function(){
    // 如果是处于content那么就必须要进行这一步操作，如果是跳到search那么不需要任何操作
    if(!this.searchPage)
    {
      this.content = this.$route.params.content.trim();
      this.search();
    }
  },
  methods:{
    search:function(){
      // 内容为空则返回，如果搜索的结果与上次相同那么我们依然搜索
      if(this.content == "")
        return;
      // 如果当前有正在搜索的内容，那么先放弃掉
      if(this.searching && this.controller != null)
        this.controller.abort();
      // 标记目前正在搜索状态
      this.searching = true;
      // 记住当前搜索框中的内容，防止用户在此期间修改
      let presentKey = this.content;
      // 准备发送http请求
      this.controller = new AbortController();
      let formData = new FormData();
      formData.append("search",this.content);
      let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
      let token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
      fetch(config.search,{
        method:"POST",
        body:formData,
        headers:{
          "X-CSRFToken":token
        },
        credentials: "include",
        signal:this.controller.signal
      }).then((response) => {
        return response.json();
      }).then((json) => {
        this.searching = false;
        this.controller = null;
        // 根据返回结果的不同来设定result
        if(json.status == config.success)
          this.result = json.result;
        else
          this.result = json.information;
        this.presentKey = presentKey;
        // 如果目前的url与搜索内容一致那么就不需要跳转了，但是不管成功与否我们都会考虑进行跳转
        if(!(this.$route.name == "content" && this.$route.params.content == presentKey))
          this.$router.push({name:"content",params:{content:this.presentKey}});
      }).catch((error) => {
        // 如果是手动终止，那么直接返回就好，注意这个一定要放在下面更改信息前面，否则手动终止完成就会直接判定为结束当前搜索
        if(error instanceof DOMException)
          return;
        this.searching = false;
        this.controller = null;
        this.result = error;
        // this.result = {
        //   empty:true,
        //   url:"http://www.xinhuanet.com/video/2020-01/26/1210452637_15800000011261n.jpg"
        // };
        // this.result = {
        //   empty:false,
        //   end:false,
        //   length:100,
        //   content:[
        //     {
        //       name:"三国演义",
        //       introduction:"三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义",
        //       download_url:"www.baidu.com",
        //       imageList:[
        //         "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592159453680&di=edb8f09c8fb193dbba6bde8dd6f24a6d&imgtype=0&src=http%3A%2F%2Fimage.gqjd.net%2Fimage%2F2009-12%2F72712457221.jpg",
        //         "http://image.gqjd.net/image/2009-12/57295513513.jpg"
        //       ],
        //       source_name:"笔趣看",
        //       source_url:"www.baidu.com",
        //       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
        //     },
        //     {
        //       name:"三国演义",
        //       introduction:"三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义",
        //       download_url:"www.baidu.com",
        //       imageList:[
        //         "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592159453680&di=edb8f09c8fb193dbba6bde8dd6f24a6d&imgtype=0&src=http%3A%2F%2Fimage.gqjd.net%2Fimage%2F2009-12%2F72712457221.jpg",
        //       ],
        //       source_name:"笔趣看",
        //       source_url:"www.baidu.com",
        //       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
        //     },
        //     {
        //       name:"三国演义",
        //       introduction:"三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义",
        //       download_url:"www.baidu.com",
        //       imageList:[],
        //       source_name:"笔趣看",
        //       source_url:"www.baidu.com",
        //       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
        //     },
        //     {
        //       name:"三国演义",
        //       introduction:"三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义",
        //       download_url:"www.baidu.com",
        //       imageList:[
        //         "https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1592159453680&di=edb8f09c8fb193dbba6bde8dd6f24a6d&imgtype=0&src=http%3A%2F%2Fimage.gqjd.net%2Fimage%2F2009-12%2F72712457221.jpg",
        //       ],
        //       source_name:"笔趣看",
        //       source_url:"www.baidu.com",
        //       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
        //     },
        //     {
        //       name:"三国演义",
        //       introduction:"三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义三国演义",
        //       download_url:"www.baidu.com",
        //       imageList:[],
        //       source_name:"笔趣看",
        //       source_url:"www.baidu.com",
        //       source_img_url:"https://static.npmjs.com/58a19602036db1daee0d7863c94673a4.png"
        //     }
        //   ]
        // };
        this.presentKey = presentKey;
        console.log(this.$route.params.content);
        console.log(presentKey);
        if(!(this.$route.name == "content" && this.$route.params.content == presentKey))
          this.$router.push({name:"content",params:{content:this.presentKey}});
      });
    },
    getMore:function(resolve){
      let regex = /.*csrftoken=([^;.]*).*$/; // 用于从cookie中匹配 csrftoken值
      let token = document.cookie.match(regex) === null ? null : document.cookie.match(regex)[1];
      fetch(config.search_more,{
        method:"POST",
        headers:{
          "X-CSRFToken":token
        },
        credentials: "include",
      }).then(response => response.json()).then(
        json => {
          if(json.status == config.success)
          {
            this.result.end = json.result.end;
            if(json.result.content.length > 0)
              this.result.content = this.result.content.concat(json.result.content);
            else
              this.$Message.info({
                content:"已加载全部信息",
                duration:2
              });
          }
          else
            this.$Message.error({
              content:"加载失败:" + json.information,
              duration:2
            });
        }
      ).catch(error => {
        this.$Message.error({
          content:"加载失败:" + error,
          duration:2
        });
      }).finally(()=>{
        resolve();
      });
    },
    download:function(order){
      // 表示该文件正在下载中
      this.$set(this.result.content[order],"downloading",true);
      // this.result.content[order].downloading = true;
      this.download_file(order);
    },
    download_file:function(order){
      let formData = new FormData();
      formData.append("url",this.result.content[order].download_url);
      let promise = new Promise((resolve,reject) => {
        fetch(config.downloaded,{
          method:"POST",
          body:formData
        }).then(response => response.json()).then(json => {
          if(json.status == config.success) 
            resolve(json);
          else
            reject(json.information);
        }).catch(error => {
          reject(error)
        });
      });
      promise.then(json => {
        // 如果没有返回进度，那么1s之后再次询问
        if(json.percent == false) {
          setTimeout(()=>{
            this.download_file(order);
          },1000);
        }
        else if(typeof(json.percent)=="string") {
          // 这里假设0.3s的时间爬取一章
          let time_node = json.percent.split("/");
          let time_interval = (Number(time_node[1]) - Number(time_node[0])) * 250;
          if(this.result.content[order].reduce_time_out != undefined)
          {
            clearTimeout(this.result.content[order].reduce_time_out);
            this.result.content[order].reduce_time_out = null;
          }
          this.$set(this.result.content[order],"process",Math.ceil((Number(time_node[1]) - Number(time_node[0]))*0.3));
          this.reduce_process(order);
          setTimeout(()=>{
            this.download_file(order)
          },time_interval);
        }
        else {
          let url = json.result;
          fetch(url,{
            method:"GET"
          }).then(res => res.blob()).then(blob => {
            let filename = this.result.content[order].name + ".txt";
            let a = document.createElement('a');
            document.body.appendChild(a);
            let url = window.URL.createObjectURL(blob); 
            a.href = url;
            a.download = filename;
            a.target = "_blank";
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
          }).catch(error => {
            this.$Message.error({
              content:"加载失败:" + error,
              duration:2
            });
          }).finally(() => {
            if(this.result.content[order].reduce_time_out != undefined)
            {
              clearTimeout(this.result.content[order].reduce_time_out);
              this.result.content[order].reduce_time_out = null;
            }
            this.$set(this.result.content[order],"downloading",false);
            this.$set(this.result.content[order],"process",undefined);
          });
        }
      }).catch(error => {
        this.$Message.error({
          content:"加载失败:" + error,
          duration:2
        });
        if(this.result.content[order].reduce_time_out != undefined)
        {
          clearTimeout(this.result.content[order].reduce_time_out);
          this.result.content[order].reduce_time_out = null;
        }
        this.$set(this.result.content[order],"downloading",false);
        this.$set(this.result.content[order],"process",undefined);
      });
    },
    // 定时减少秒数，但是不会减到1以下
    reduce_process:function(order) {
      if(this.result.content.legnth <= order | this.result.content[order].process == undefined)
        return;
      if(this.result.content[order].process <= 1)
      {
        // 先清除一下
        this.result.content[order].reduce_time_out = undefined;
        return;
      }
      this.result.content[order].reduce_time_out = setTimeout(()=>{
        this.result.content[order].process -= 1
        this.reduce_process(order)
      },1000);
    }
  },
  provide:function(){
    return {
      download:this.download
    }
  },
  components:{
    Link
  }
}
</script>

<style scoped lang="scss">
$small-white:rgb(255, 255, 255);

.search
{
  background-color:#F1F2F9;
}
.search-item
{
  width:100%;
  position: absolute;
  top: 30%;
  display:flex;
  flex-direction: column;
  align-items: center;  
  justify-content: flex-start;
  padding:5px 0 5px 0;
  .introduction
  {
    padding:10px;
    font-family: "Verdana",youyuan;
    .title
    {
      color:white;
      font-size:2rem;
      text-align:center;
      padding-bottom:10px;
      font-weight: bold;
    }
    .detail
    {
      color:rgb(204, 204, 204);
      font-size:1rem;
      text-align: center;
    }
  }
  .search-line
  {
    border-radius: 40px;
    background-color:rgba(0,0,0,0.5);
    display:flex;
    flex-direction: flex-start;
    align-items: center;
    display:inline-block;
    .search-input
    {
      background-color:rgba(0,0,0,0);
      outline:none;
      border:none;
      height:60px;
      padding:0 10px 0 20px;
      width:420px;
      font-size:1.1rem;
      color:$small-white;
      caret-color: $small-white;
      font-family: "Verdana",youyuan;
    }
    .search-button
    {
      margin-right:10px;
      color:rgb(53, 63, 92);
      background-color:$small-white;
      border:none;
      border-radius:100px;
      padding:10px;
      cursor:pointer;
      outline:none;
    }
  }
  .loading-region
  {
    color:$small-white;
    font-size:1.2rem;
    display:flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top:20px;
    font-family: "Verdana",youyuan;
    .loading
    {
      color:$small-white;
      margin-right:10px;
    }
    .loading-word
    {
      width:100px;
      font-weight: bold;
    }
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
.link
{
  position:absolute;
  bottom:0;
  left:50%;
  transform: translate(-50%,0);
  margin-bottom:20px;
}
.first-page,.second-page
{
  width:100%;
  height: 100%;
  position:absolute;
  top:0;
  left:0;
  min-width:1000px;
  min-height:500px;
}
.second-page
{
  background-color:#F1F2F9;
  display:flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: stretch;
}
.first-page
{
  background-image: url("../img/79f33f3f.png");
}
.nav
{
  // position:absolute;
  // top:0;
  // left:0;
  width:100%;
  box-shadow:0 0 3px rgb(200,200,200);
  box-shadow:0 0 6px #bbbedb;
  box-shadow:0 0 6px #4d4d4d;
  padding:5px 20px 5px 20px;
  background-color:#F1F2F9;
  background-color:#eaecfd;
  background-color:#2b2b2b;
  background-image: url("../img/79f33f3f.png");
  display:flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  height:45px;
  .logo
  {
    font-family: "Verdana",youyuan;
    font-size:1.1rem;
    font-weight: bold;
    margin-right:100px;
    flex-shrink: 0;
    cursor:pointer;
    color:$small-white;
  }
  .search-line
  {
    border-radius: 25px;
    background-color:white;
    background-color:rgba(0,0,0,0.5);
    display:flex;
    flex-direction: flex-start;
    align-items: center;
    display:inline-block;
    flex-shrink: 0;
    margin-right:20px;
    border:1px solid rgb(117, 117, 117);
    transition: all 0.5s;
    .search-input
    {
      background-color:rgba(0,0,0,0);
      outline:none;
      border:none;
      height:30px;
      line-height: 30px;
      padding:0 5px 0 10px;
      width:420px;
      font-size:1rem;
      color:#fff;
      color:$small-white;
      font-family: "Verdana",youyuan;
    }
    .search-button
    {
      margin-right:10px;
      color:rgb(53, 63, 92);
      border:none;
      border-radius:100px;
      cursor:pointer;
      outline:none;
      color:rgb(43, 117, 255);
      color:$small-white;
      background-color:transparent;
      .search-button-icon
      {
        background-color:blue;
        background-color:transparent;
      }
    }
    .loading
    {
      color:$small-white;
    }
  }
  .search-line:hover,.search-line-focus
  {
    border:1px solid rgb(216, 216, 216);
  }
}
.display-region
{
  background-color:#F1F2F9;
  flex:1;
  // margin-top:42px;
  // margin-bottom:25px;
}
.top
{
  color:white;
  background-color:rgba(211, 98, 22, 0.8);
  width:50px;
  height:50px;
  display:flex;
  flex-direction: row;
  justify-self: center;
  align-items: center;
  box-shadow:0 0 3px rgba(248, 128, 49,0.6);
  border-radius:25px 25px 0 25px;
}
.top:hover
{
  background-color:rgba(211, 98, 22, 1);
}
</style>