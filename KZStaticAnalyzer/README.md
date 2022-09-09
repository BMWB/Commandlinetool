# KZStaticAnalyzer
静态分析和代码格式化。

## 配置用法
1、需要Python3环境（Python2将从2020年1月1日起不再维护）。
2、需要安装pod，如果没有pod可以执行`gem install xcodeproj`来安装ruby插件。

**单工程配置**
将`KZStaticAnalyzer`文件夹放到项目工程目录下，然后执行install文件夹中的`NormalConfig.py`进行配置即可，会在每次commit时候自动进行增量代码质量分析。如果需要进行检测本次添加的文件是否已经添加到可启动的target里面，需要运行`NormalConfigWithTarget.py`安装脚本。

**Boss直聘配置**
在壳工程里的 .PythonLib/KZStaticAnalyzer/install 路径下，运行`BossZPConfig.py`脚本，根据提示进行自动配置，通过--help可以查看安装帮助。
1、命令:
-h, --help          查看配置帮助信息
-q, --query         查看已经进行配置的本地arc信息
2、静态检查根据提示配置即可；
3、自动arc根据提示，如果需要定制指定reviewer，只需要给定模块，然后给定检查人即可，其余的会按照默认配置安装。
4、自动arc时，在commit msg里面添加参数可控制arc：
`-r` : 通过 -r name，可为本次arc指定arc人。
`--no-arc` : 可以放弃本次的自动arc。
实例：`git commit -a -m'test -r liuyaping'`
实例：`git commit -a -m'test --no-arc'`

**整体静态检查和代码格式化**
运行`CodeQualityControl.py `脚本进行静态检查和代码格式化，参数介绍：
`-m` : 文件夹路径。
`-c` : 进行静态检查。
`-f` : 进行代码格式化。
`-d` : list，排除list里包含的文件夹名字。

**增量代码格式化**
运行`IncrementQualityControl.py `脚本进行增量代码格式化，参数介绍：
`-p` : 项目的路径。
`-m` : 主项目路径。
`-d` : list，排除list里包含的文件夹名字。

**静态检查规则**
1、block体内代码每行首字符缩进数不能超过50列；
2、最外层block体内代码行数不能超过40行；
3、block体内嵌套block个数不能超过4个；
4、方法声明最大列数不能超过130列；
5、方法体内最大代码行数不能超过140行；
6、检测`tableView:estimatedHeightForFooterInSection:`返回值不能小于1，小于1在某些版本会崩溃；
7、`collectionView:viewForSupplementaryElementOfKind:atIndexPath:`不能返回nil。