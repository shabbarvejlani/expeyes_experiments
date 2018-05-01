'''
expEYES program
Author  : Ajith Kumar B.P, bpajith@gmail.com
License : GNU GPL version 3
'''
import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext

import time, sys, math
sys.path.insert(0,"/home/sav/Downloads/eyes-junior/")
from Tkinter import *
import expeyes.eyesj as eyes, expeyes.eyeplot as eyeplot, expeyes.eyemath as eyemath


TIMER = 10
WIDTH  = 600   # width of drawing canvas
HEIGHT = 400   # height    

VSET    = 0		# this will change in the loop
VSETMIN = 0		# may change this to -5 for zeners
VSETMAX = 5
STEP    = 0.050		# 50 mV
MINX    = 0			# may change this to -5 for zeners
MAXX    = 6         # We have only 5V supply
MINY    = 0			# may change this to -5 for zeners
MAXY    = 600			# Maximum possible current
history = []		# Data store
trial = 0			# trial number
data = [ [], [] ]	# Current & Voltage
index = 0
running = False
vbias = 0

def is_bounded(val,ref,tol_per):
   tol=(ref*tol_per/100.0)
   
   if (val > (ref-tol)) and (val < (ref+tol)):
   	return True
   else:
   	return False	

def compare_it(val,ref,tol_per):
   tol=(ref*tol_per/100.0)
   if val < (ref-tol):
   	return -1
   if val > (ref+tol):
   	return 1	

def start():
	global VSET, running, index, data, vbias,vbias_actual
	if running == True:
		msg.config(text=_('Busy Drawing'))
		return
	p.set_voltage(0)	
	vbset = float(Bias.get())
	p.set_sqr1_dc(vbset)
	time.sleep(1)			
	vbias = vbset # V
	vbias_adj=vbias
	msg.config(text=_('Vgs = %5.2f V')%(vbias))
	stable_count=0
	timeout_count=0
	while 1:
		vbias_actual = p.get_voltage(3)
		msg.config(text=_('Actual Voltage = %5.2f V')%(vbias_actual))
		if is_bounded(vbias_actual,vbias,2):
			
			stable_count=stable_count+1
			if stable_count > 10:
				print("sqr stabalized : iteration count=%0d"%(timeout_count))
				break
		else:
		   stable_count=0
		   if compare_it(vbias_actual,vbias,2)==1:
		   	vbias_adj=vbias_adj-0.01
		   if compare_it(vbias_actual,vbias,2)==-1:
		   	vbias_adj=vbias_adj+0.01
		   print("vbias_adj =%0f, vbias_actual=%f"%(vbias_adj,vbias_actual))	
		   p.set_sqr1_dc(vbias_adj)
		time.sleep(1)
		timeout_count=timeout_count+1
		if timeout_count==100:
			break    
	
	msg.config(text=_('Final Actual Voltage = %5.2f V')%(vbias_actual))	
	#g.text(1,2,_('test'))
	data = [ [], [] ]
	VSET = VSETMIN
	index = 0
	running = True
	root.after(TIMER,update)

def update():					# Called periodically by the Tk toolkit
	global VSETMAX, VSET, STEP, index, trial, running, data, history
	if running == False:
		return
	vs = p.set_voltage(VSET)	
	time.sleep(0.001)	
	va = p.get_voltage(1)		# voltage across the diode
	i = ((vs-va)/(10e3))/(1e-6) 	 		# in uA, Rload= 10k
	data[0].append(va)
	data[1].append(i)
	VSET += STEP
	if VSET >= VSETMAX :
		running = False
		history.append(data)
		trial += 1
		g.delete_lines()
		for k in range(len(history)):
			g.line(history[k][0], history[k][1], k)
		g.text(va, i, _('Vgs=%3.2f V')%(vbias_actual),k)
		return
	if index > 1:			# Draw the line
		g.delete_lines()
		g.line(data[0], data[1], trial)
	index += 1
	root.after(TIMER, update)

def xmgrace():		# Send the data to Xmgrace
	global history
	p.grace(history, _('Volts'), _('mA'), _('Diode IV Curve'))

def save():
	global history, running
	if running == True:
		return
	s = e1.get()
	if s == '':
		return
	p.save(history, s)
	msg.config(text = _('Data saved to file ')+s)

def clear():
	global history, trial, running
	if running == True:
		return
	g.delete_lines()
	g.delete_text()
	history = []
	trial = 0

p = eyes.open()
p.disable_actions()
p.set_sqr1_dc(0.01)
time.sleep(5)

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  # Some space at the top
g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)	# make plot objects using draw.disp
g.setWorld(MINX, MINY, MAXX, MAXY,_('V'),_('uA'))

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

l = Label(cf, text=_('Vgs='))
l.pack(side=LEFT, anchor = SW )
Bias =StringVar()
Bias.set('1.0')
e =Entry(cf, width=5, bg = 'white', textvariable = Bias)
e.pack(side = LEFT)
l = Label(cf, text='V')
l.pack(side=LEFT, anchor = SW )
b1 = Button(cf, text = _('START'), command = start)
b1.pack(side = LEFT, anchor = N)
b3 = Button(cf, text = _('SAVE to'), command = save)
b3.pack(side = LEFT, anchor = N)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('tran_ce.dat')
e1.pack(side = LEFT)

b5 = Button(cf, text = _('QUIT'), command = sys.exit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = clear)
b4.pack(side = RIGHT, anchor = N)
b5 = Button(cf, text = _('Grace'), command = xmgrace)
b5.pack(side = RIGHT, anchor = N)
#b5 = Button(cf, text = _('LINE'), command = load_line)
#b5.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP,  fill = BOTH, expand = 1)
msg = Label(mf,text=_('Message'), fg = 'blue')
msg.pack(side=LEFT)

#eyeplot.pop_image('pics/transistor-ce.png', _('Mosfet Id-Vds Char (NMOS)'))
root.title(_('EYES Junior: Mosfet Id-Vds characteristics'))
root.mainloop()

