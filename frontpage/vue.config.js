module.exports = {
  // lintOnSave:false,
  // publicPath:"./",
  publicPath:"/novel_download_static/",
  pages:{
    search:{
      entry:"./src/main.js",
      template:"./public/index.html",
      filename:"index.html",
      title:"小说下载器"
    }
  },
  runtimeCompiler:true
}