# tornado - session和permission(权限)系统

本项目主要是研究session和权限，对于用户系统属于借用，即通过mongoDB创建
了几条简单的数据，没有做密码加密、登陆验证等...

## session

通过构建一个`Session`类来实现，构建这个对象时需要传入一个`RequestHandler`
实例。

类初始化过程首先检查cookie中是否存在session_id，如果存在着直接用作`_id`属性
没有的话则通过`generate_session_id`来生成，通过`haslib.sha1`这个函数。

session_id作为键名称，存入redis的hash数据结构中，这个session_id可以看作
一个命名空间，在其中可以赋值很多键值对。

在login页面，验证登陆成功后可以将username传入相应session_id的redis结构中，
在`get_current_user()`方法中可以取出这个值和数据库中的User表对照。

并且可以设置session过期时间，通过redis方法`expire`实现，可以在settings中
添加一个`session_expire`来达到目的，单位为**秒**。

## 准备

* 需要redis, mongoDB
* 需要在mongoDB创建一个auth数据库，users集合，以及若干用户文档/行。




