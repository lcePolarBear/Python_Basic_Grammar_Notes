## 数据源
- 中央气象台天气实况  [http://www.nmc.cn](http://www.nmc.cn/publish/observations/hourly-precipitation.html)
## 目标数据
- 43 类气象图像数据
- 3 类降水量地区排行列表数据
## 基础环境与组件版本
- python 版本：

  3.6.14

- python 依赖组件版本：

  beautifulsoup4==4.6.0  
  kafka==1.3.5  
  pip==18.1  
  PyMySQL==1.0.2  
  redis==2.10.6  
  selenium==2.48.0  
  setuptools==40.6.2  

- kafka 版本：

  2.8.1

- redis 版本

  6.2.6

## 解决上一版本的问题
网站无法访问
网站访问后，图片无法加载
图片可加载，但是加载的图片为错误图片（url 错误）
由于 qt 组件故障导致崩溃