# Simple EDA

Simple EDA 是一个用于电路分析和仿真的简单EDA工具。

## 设计思路

使用改进的节点分析法（MNA，参考：[维基百科](https://en.wikipedia.org/wiki/Modified_nodal_analysis)）在 s 域建立方程求解，最后通过逆拉式变换得到时域解。

## 功能

- 绘制电路图
- 添加电阻、电容、电感、电压源、电流源等元件
- 求解电路节点电势和电压源电流
- 显示电路元件信息
- 绘制电流和电压的时域波形

## 安装

1. 克隆项目到本地：

    ```bash
    git clone https://github.com/yourusername/SimpleEDA.git
    ```

2. 进入项目目录：

    ```bash
    cd SimpleEDA
    ```

3. 安装依赖：

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
