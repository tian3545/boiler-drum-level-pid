clear; close all; clc;
root    = fileparts(mfilename('fullpath'));
dataDir = fullfile(root,'data');
outDir  = fullfile(root,'results');
mdl     = 'boiler_level_pid';

M = dlmread(fullfile(dataDir,'steam_demand_day.csv'));
D_input = timeseries(M(:,2), M(:,1));

out = sim(mdl, 'StopTime', '86400');
t = out.H.Time; H = out.H.Data; W = out.W.Data;

i2 = find(t >= 7200, 1);
Hw = H(i2:end); tw = t(i2:end);
Hmax  = max(abs(Hw));
rmsH  = sqrt(mean(Hw.^2));
peakH = max(Hw);                      
valleyH = min(Hw);                    
iBack = find(abs(Hw) < 5, 1);          
tBack = (tw(iBack) - 7200)/60;         

f = figure('Visible','off','Position',[100 100 1100 440]);
subplot(1,2,1);
plot(t/3600, H, 'b-','LineWidth',1.3); hold on; grid on;
yline(30,'r--','+30mm'); yline(-30,'r--','-30mm'); yline(0,'k:');
xlabel('时刻 (h)','FontName','Microsoft YaHei'); ylabel('汽包水位 (mm)','FontName','Microsoft YaHei');
title(sprintf('PID 自动控制：扰动窗口最大 |H| %.1f mm（安全 ±30mm）', Hmax),'FontName','Microsoft YaHei');
subplot(1,2,2);
idx = t >= 1.5*3600 & t <= 4*3600;
plot(t(idx)/3600, H(idx), 'b-','LineWidth',1.6); hold on; grid on;
yline(30,'r--','+30mm'); yline(-30,'r--','-30mm'); yline(0,'k:');
xlabel('时刻 (h)','FontName','Microsoft YaHei'); ylabel('汽包水位 (mm)','FontName','Microsoft YaHei');
title('第 2 h 蒸汽突增局部放大（虚假水位 → PID 回中）','FontName','Microsoft YaHei');
set(gca,'FontName','Microsoft YaHei');
exportgraphics(f, fullfile(outDir,'04_pid_level_response.png')); close(f);

sumFile = fullfile(outDir,'summary.txt');
oldTxt = '';
if exist(sumFile,'file'), oldTxt = fileread(sumFile); end
kSim = strfind(oldTxt, '[Simulink 仿真]');
if ~isempty(kSim), oldTxt = oldTxt(1:kSim(1)-1); end
fid = fopen(sumFile,'w'); fprintf(fid,'%s',oldTxt); fclose(fid);

fid = fopen(sumFile,'a');
fprintf(fid,'\n[Simulink 仿真] 模型 %s.slx（单回路 PID，P=1.0 I=0.03）\n', mdl);
fprintf(fid,'24h 仿真；扰动窗口(2-24h)水位峰值 +%.1f mm / 深跌 %.1f mm，RMS %.2f mm\n', peakH, valleyH, rmsH);
fprintf(fid,'最大 |H| %.1f mm（安全 ±30mm）\n', Hmax);
fprintf(fid,'突增后首次回到 ±5mm 内用时 %.1f min\n', tBack);
fprintf(fid,'给水流量偏差范围 [%.1f, %.1f] %%Dn\n', min(W), max(W));
fclose(fid);
disp(fileread(sumFile));