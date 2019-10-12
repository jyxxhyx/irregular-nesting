# 面料裁切利用率优化比赛

启发式方法求解面料裁切问题。

## 使用

运行`/code/main.py`即可，程序会遍历`/data`文件夹下各文件夹（如DatasetA）的算例进行求解，结果存在`/submit`文件夹中同名文件夹下。

### 依赖项（由`pipreqs`生成）

```
  numpy==1.15.2
  matplotlib==3.1.1
  pyclipper==1.1.0.post1
  Shapely==1.6.4.post2
  typing==3.7.4.1
  ujson==1.35
  PyYAML==5.1.2
```

## 初赛算例

### 计算环境

程序用`python3.6`实现，运行于MacBook Pro，处理器为2.3 GHz Intel Core i5，内存为8 GB 2133 MHz LPDDR3。

### 求解结果

| 算例  | 布料长度（m） | 利用率（%） | 运行时间 (s) |
| ----- | ------------- | ----------- | ------------ |
| L0002 | 18.753        | 73.5        | 203.24       |
| L0003 | 17.359        | 75.2        | 147.35       |

## TODO

- [x] ~~用numpy存储坐标点，提升计算效率~~（暂时没啥改善）
- [x] NFP计算结果存储，方便以后local search时候调用
  - [x] NFP结果与问题批次、clipper参数、offset、scale参数相关，结果命名中需要区分。
- [ ] local search部分tabu search方法实现
- [ ] 零件旋转相关的处理（坐标变化，NFP计算）
- [x] 复赛中面料上圆形瑕疵的处理
- [x] 结果校验函数
- [x] 零件相似性判断
  - [ ] 并行版本还没搞定
- [x] NFP并行计算
- [x] zip包使用
- [x] config参数配置