clear; clc;
root   = fileparts(mfilename('fullpath'));
csvDir = fullfile(root, 'data', 'steam_demand_day.csv');

M = dlmread(csvDir);
D_input = timeseries(M(:,2), M(:,1));   

disp('D_input 已就绪（From Workspace 的输入变量）：');
disp('  数据点个数 = ' + string(numel(D_input.Time)));
disp('  时间范围   = ' + string(D_input.Time(1)) + ' ~ ' + string(D_input.Time(end)) + ' s');
disp('  现在可以打开 boiler_level_pid.slx 点"运行"（停止时间 86400）');