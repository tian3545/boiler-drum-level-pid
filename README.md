# 锅炉汽包水位 PID 控制系统

基于 MATLAB/Simulink 的锅炉汽包水位 PID 控制仿真项目。

## 项目简介
模拟锅炉汽包水位控制系统，当蒸汽用量突然增大时，通过 PID 控制器自动调节给水量，将水位稳定在安全范围内（±30mm）。

## 模型结构
- 蒸汽扰动输入（第2小时阶跃突增8%）
- 虚假水位环节（75s/(30s+1)）
- 单回路 PID 控制器（P=1.0, I=0.03）
- 调节阀惯性环节（1/(10s+1)）
- 汽包水位积分（蒸汽侧 + 给水侧）

## 仿真结果
- 24小时仿真，水位最大偏差 ±19.9mm（安全范围 ±30mm）
- 蒸汽突增后 0.2 分钟内回到 ±5mm 以内
- 给水流量调节范围 [-9.6, 20.1] %Dn

## 文件说明
- boiler_level_pid.slx - Simulink 模型文件
- run_level_pid_sim.m - 一键仿真脚本
- prepare_workspace.m - 数据准备脚本
- boiler_simple_analysis.m - 开环分析脚本
- data/steam_demand_day.csv - 蒸汽扰动数据
- results/ - 仿真结果图