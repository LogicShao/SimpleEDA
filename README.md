# Simple EDA

Simple EDA 是简单的电路分析仿真项目。

## 设计思路

1. 该项目使用 `PyQt6` 实现图形界面以及绘制电路；
2. 使用 `sympy` 实现 s 域方程的构建与求解，以及逆拉式变换得到时域解；
3. 最后使用 `matplotlib` 绘制元件两端的电压以及电流波形；
4. 电路的求解使用改进的节点分析法（MNA，参考：[维基百科](https://en.wikipedia.org/wiki/Modified_nodal_analysis)）在 s 域建立方程求解，得到节点电位以及电压源电流，最后通过逆拉式变换得到时域解。

## 项目结构

* `CircuitItem`：实现电路模块（绘制元件、构建电路拓扑以及求解）
  * `BaseCircuitItem.py`
    * 实现元件基类 `BaseCircuitItem`，元件节点类 `ItemNode`，电路节点类 `CircuitNode`，元件符号类 `ItemSymbol`，元件标签类 `ItemInfo`。
    * 一个元件（`BaseCircuitItem`）由元件的节点（`ItemNode`）列表、元件符号（`ItemSymbol`）组成。每一个元件结点会有一个电路节点（`CircuitNode`）的引用，电路节点会持有一个电位（在 s 域中的表达式）。
    * 在求解之后，通过元件两端的电位绘制电压、电流曲线
  * `BasicItem.py`：实现导线、电阻、电容以及电感类
  * `CircuitTopology.py`
    * 实现电路拓扑结构的构建：对电路图进行缩点，通过 `Flood-Fill` 算法将所有电位相同的元件节点赋上同一个电路节点的引用，并构建对应的图（使用邻接表）
    * 实现电路的求解，并将求解的结果赋到对应的电路节点以及元件上
  * `MeterItem.py`：实现电压表类（TODO：电流表）
  * `SourceItem.py`：实现电压源、电流源类
* `common_import.py`：项目文件的公共导入模块
* `log_config.py`：配置项目的日志，提供 `logger` 用于记录日志
* `main.py`：项目主程序入口
* `MainWindow.py`：实现 `MainWindow` 类，绘制项目的图像界面

## 功能

- 绘制电路图
- 添加电阻、电容、电感、电压源、电流源、电压表元件
- 显示电路元件信息、修改元件数值、删除元件
- 求解电路节点电势和电压源电流
- 绘制电流和电压的时域波形

## 安装

1. 克隆项目到本地：

    ```bash
    git clone https://github.com/LogicShao/SimpleEDA.git
    ```

2. 进入项目目录：

    ```bash
    cd SimpleEDA
    ```

3. 安装依赖（至少需要 `python 3.12`）：

    ```bash
    pip install -r requirements.txt
    ```

## 使用

1. 运行主程序：

    ```bash
    python main.py
    ```

2. 在主窗口中，可以通过按钮添加电路元件，连接节点，进行电路求解。

3. 求解完成后，可以查看电路元件信息，绘制电流和电压的时域波形。

## 运行截图

![运行截图](F:\library\project\SimpleEDA\assets\运行截图.png)
