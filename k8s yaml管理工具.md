# k8s yaml管理工具

这是一个可以在windows运行的（最好跨平台兼容）可视化的kubernetes yaml管理工具。它主要包含三个功能：yaml命令生成器、yaml比较器、yaml信息提取器。工具对读取的一个或多个集群的yaml文件夹结构有要求：对每个集群，顶层文件夹是集群名，下一层文件夹每个文件夹都是这个集群的命名空间名，每个命名空间文件夹下是这个空间下的所有资源类型文件夹（资源名可包括：Application,Deployment,ConfigMap,PersistantVolumeClaim,Secret,Service，目前先支持这些，后续可再支持其他类型），资源类型文件夹下就是具体的部署资源yaml。

所有yaml文件后缀为.yaml。

我的yaml可能通过---这种三横线在一个文件里面描述了多个kind的资源，资源名在metadata下的name字段，命名空间名在metadata下的namespace字段。

1. yaml命令生成工具

这是针对kubernetes yaml文件的命令生成器。你需要根据yaml信息解析，在命令生成功能页面先生成一个表格（称为资源表），上面有kind类型，命名空间，资源名，解析的根文件夹名，并支持excel导出。命令文件生成规则为：生成一个utf-8格式的sh文件，里面是一行一行部署或删除资源的命令。

（1）批量生成删除资源的功能，。

用户可以勾选想生成的资源类型，或者从上面解析出的资源表选择需要生成命令的yaml文件。

你需要注意删除时需要保证删除资源的顺序：Service,Application,ConfigMap,Secret,PersistantVolumeClaim。
Service的删除命令格式为：condep delete -t svc -n {解析的命名空间名} -c {根目录名} {资源名}
Application的删除命令格式为：condep delete -t app -n {解析的命名空间名} -c {根目录名} {资源名}
ConfigMap的删除命令格式为：condep delete -t cfgm -n {解析的命名空间名} -c {根目录名} {资源名}
Secret的删除命令格式为：condep delete -t scrt -n {解析的命名空间名} -c {根目录名} {资源名}
PersistantVolumeClaim的删除命令格式为： condep delete -t pvc -n {解析的命名空间名} -c {根目录名} {资源名}  

删除命令可以不生成Deployment类型

（2）部署命令生成功能

用户可以勾选想生成的资源类型，或者从上面解析出的资源表选择需要生成命令的yaml文件。

需要注意生成时需要保证部署资源的顺序：PersistantVolumeClaim，Secret，ConfigMap，Application，Service。

部署Application资源时命令是 condep deploy -f {解析出的从集群根路径开始的yaml文件路径} -n {解析的命名空间名} -c {根目录名} --app yes

部署其他任意非Application类型资源命令是 condep deploy -f {解析出的从集群根路径开始的yaml文件路径} -n {解析的命名空间名} -c {根目录名} --app no

2. yaml比较器

yaml比较器可比较任意两个集群文件夹下同命名空间名下相同资源类型（kind）和资源名的yaml比较。也可选定两个yaml文件直接进行比较（要求相同资源类型kind）。

我需要针对不同的kind的yaml指定比较的key来定制化输出比较结果。注意一个yaml文件可能有多个kind，每个kind通过---进行分隔。

对于每个kind，我可以定义类似a.b.c这种路径来定义需要比较的key的路径。

对于configmap, 或者secret，我可能会把文件名定义成key，value是文件内容以便挂载。此时用户可以填写key然后直接比较value文本，或者填写key以后选择文件类型（yaml或者properties）：不论是yaml格式或者properties格式，都可以写a.b.c的方式表示key路径。对于configmap或secret的比较结果，其实就可能会多一层文件名（直接文本比较除外）。

比较结果：

（1）如果是集群文件夹比较，则可以导出两个选定集群下每个对应同名命名空间下同资源类型和资源名的yaml比较结果。每个资源类型生成一个单独的excel，每个excel通过sheet页区分资源名（注意excel最大sheet页数，所以每个资源类型可以有一个或多个文件）。

（2）如果是单yaml比较，如果没有相同资源类型和资源名则可以前端弹窗提示，如果可比较，则单独输出一个excel文件，文件和上面集群集比较结果一样也输出资源类型比较结果的excel，sheet页是资源名。

3. yaml信息提取器

其实就是上述比较器的一个简化版，可复用。即选取单个集群文件夹，或命名空间文件夹，或单个资源类型文件夹，或单个yaml，针对yaml比较器里面用户所定义的key进行具体值的解析。

它支持导出成excel，excel里面按资源类型分为多个excel文件，每个excel里面sheet页代表一个资源名，里面是对指定key的值的解析结果。

另外可选给key起一个别名，用于在key后展示含义（同一个单元格）。