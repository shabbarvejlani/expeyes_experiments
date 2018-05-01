% viplot1.m
close all
% Filenames for scope channel1, channel 2 data
% Get these from looking at directory of flash drive

% F0008 had VGS=3.7V
ch_1_file='vgs_1p82.dat';
nfit=33;

vgs=1.82;

% put VDS (v1) and ID (i2) data in one variable
sortdata = dlmread(ch_1_file);
v1= sortdata(:,1);

% total number of points in scope waveform capture
npts=size(sortdata(:,1),1);



% plot total data as sanity check to look at before doing fitting
figure(4)
plot(sortdata(:,1),sortdata(:,2),'.')
% Label axes
xlabel('V_{DS} [V]')
ylabel('I_{D} [A]')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Fit parameters : triode region first

% For triode region, use nfit to limit to points in triode for parabola fit
% Fit to 2nd order polynomial using polyfit
triode_fit_poly=polyfit(sortdata(1:nfit,1),sortdata(1:nfit,2),2)
% parabola is 
%         2
% I  = a V   + b V   + c
%  D      DS      DS

a=triode_fit_poly(1);
b=triode_fit_poly(2);
c=triode_fit_poly(3);

% Set derivative to zero: maximum ID occurs at vds_max given by
vds_max=-0.5*b/a;

% Evaluate parabola at vds_max to get id_max maximum current
% at triode-active boundary
id_max=polyval(triode_fit_poly,vds_max);

% Choose range of points to show parabola
t_fitpts=0:0.01:1.5*vds_max;
% evaluate parabola at these points to plot
% will agree with rising half of plot when triode region is valid
triode_fit=polyval(triode_fit_poly,t_fitpts);

% For "on" resistance: Evaluate derivative at vds=0
Ron=1/b;
% Choose range of points to show linear part
r_fitpts=0:0.01:.6*vds_max;
% calculate linear fit for Ron portion of characteristic
I_lin_fit=b*r_fitpts;

% For output resistance in active: fit line to points in active region
% degree = 1 for linear fit
active_fit_poly=polyfit(sortdata(nfit:npts,1),sortdata(nfit:npts,2),1)
% Choose range of points to show parabola
a_fitpts=vds_max:0.01:max(v1);
% For small signal output resistance: slope of line
Ro=1/active_fit_poly(1);
% calculate linear fit for active portion of characteristic
I_active_fit=polyval(active_fit_poly,a_fitpts);



%Plot everything
figure(5)
hold off

% Plot data used in fit in red
plot(sortdata(1:nfit,1),sortdata(1:nfit,2),'.','Color',[1 .4 .4])

hold on

% plot other data in blue
plot(sortdata(nfit:npts,1),sortdata(nfit:npts,2),'.','Color',[.6 .6 1])

% plot parabola fit in black solid line
plot(t_fitpts,triode_fit,'k','Linewidth',2)

% plot linear fit in black dashed line
plot(r_fitpts,I_lin_fit,':k','Linewidth',2)

% plot active fit in black dashed line
plot(a_fitpts,I_active_fit,'-k','Linewidth',2)

% indicate maximum current at boundary of triode, active
text(0,max(sortdata(:,2)),['R_{on} = ' num2str(1/b,'%5.0f') '\Omega'])

% Indicate Ron in ohms
text(1.5*vds_max,id_max,['I_{D} = ' num2str(id_max,'%5.3e') 'A'], ...
    'HorizontalAlignment','Left')
text(1.5*vds_max,0.9*id_max,['@ V_{DS} = ' num2str(vds_max,'%5.3e') 'V'], ...
    'HorizontalAlignment','Left')
text(1.5*vds_max,0.8*id_max,['V_{GS} = ' num2str(vgs,'%+5.3f') 'V'], ...
    'HorizontalAlignment','Left')

% Label for output resistance
text(0.95*max(a_fitpts),0.8*id_max,['r_{o} = ' num2str(.001*Ro,'%+5.2f') 'k\Omega'], ...
    'HorizontalAlignment','Right')
% Label axes
xlabel('V_{DS} [V]')
ylabel('I_{D} [A]')

axis tight





