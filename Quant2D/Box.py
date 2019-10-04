import numpy as np

import wavef
import potentials

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty,ListProperty,NumericProperty,StringProperty
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle,Color,Ellipse
from kivy.clock import Clock


class main(BoxLayout):
    
    N=100
    dx=0.05
    dt=0.01
    ntime=100
    L=N*dx
    
    mass = 1.
    charge = 1.
    x0 = NumericProperty()
    y0 = NumericProperty()    
    
    xx,yy = np.meshgrid(np.arange(-L/2,L/2,dx),np.arange(-L/2,L/2,dx),sparse=True)
    
    potentials = ListProperty()
    potsave = []
    particles = []
    init_conds = []
    
    plot_texture = ObjectProperty()
    
    
    def __init__(self, **kwargs):
        super(main, self).__init__(**kwargs)
        self.pot = wavef.Phi()
        self.wav = wavef.Phi()
        
        self.set_texture()
        self.time = 0.
        self.T = 100
        self.speed = 0.3
     #   self.change_speed()
        self.running = False
        
    def set_texture(self):
        self.n = 100
        self.im = np.zeros((self.n,self.n),dtype=np.uint8)
        self.plot_texture = Texture.create(size=self.im.shape,colorfmt='luminance',bufferfmt='uint')
        self.plotwave_texture = Texture.create(size=self.im.shape,colorfmt='luminance',bufferfmt='uint')
        
    def background(self):
        self.im = np.zeros((self.n,self.n))
        if(self.pot.functions.size == 0):
            self.im = np.uint8(self.im)
        else:
            self.im = self.pot.val(self.xx,self.yy)
            self.im = self.im + np.abs(self.im.min())
            self.im = np.uint8(255.*(self.im/self.im.max()))

    def update_texture(self):
        with self.plotbox.canvas:
            cx = self.plotbox.pos[0]
            cy = self.plotbox.pos[1]
            w = self.plotbox.size[0]
            h = self.plotbox.size[1]
            b = min(w,h)
            
            self.plot_texture.blit_buffer(self.im.reshape(self.im.size),colorfmt='luminance')
            Color(1.0,1.0,1.0)
            Rectangle(texture = self.plot_texture, pos = (cx,cy),size = (b,b))

        
    def update_parameters(self,touch):
        w = self.plotbox.size[0]
        h = self.plotbox.size[1]
        b = min(w,h)
        scale = b/200.
        x = (touch.pos[0] - b/2.)/scale
        y = (touch.pos[1] - b/2.)/scale

        if(self.menu.current_tab.text == 'Potentials'):
            self.param0slider.value = x
            self.param1slider.value = y
        if(self.menu.current_tab.text == 'Particles'):
            self.x0slider.value = x
            self.y0slider.value = y
              
    def add_pot_list(self):
        if(self.potmenu.current_tab.text == 'Oscilador'):
            self.potentials.append('Oscilador: x0 = {}, y0 = {}, k = {}'.format(round(self.param0slider.value,3),round(self.param1slider.value,3),round(self.param2oslider.value,2)))
   #         self.potentialsave.append('Oscilador:x0 = {}, y0 = {}, k = {}'.format(round(self.param0slider.value,2),round(self.param1slider.value,2),round(self.param2oslider.value,2)))
            self.pot.add_function(potentials.osc,[self.param0slider.value,self.param1slider.value,self.param2oslider.value])
        elif(self.potmenu.current_tab.text == 'Gaussian'):
            self.potentials.append('Gaussian: x0 = {}, y0 = {}, V0 = {}, Sigma = {}'.format(round(self.param0slider.value,3),round(self.param1slider.value,3),round(self.param2gslider.value,2),round(self.param3gslider.value,2)))
   #         self.potentialsave.append('Gaussian:x0 = {}, y0 = {}, V0 = {}, Sigma = {}'.format(round(self.param0slider.value,2),round(self.param1slider.value,2),round(self.param2gslider.value,2),round(self.param3gslider.value,2)))
            self.pot.add_function(potentials.gauss,[self.param0slider.value,self.param1slider.value,self.param2gslider.value,self.param3gslider.value])
        
        self.background()
        self.update_texture()

        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def reset_pot_list(self):
        self.pot.clear()
        self.potentials = []
        self.potentialsave =[]
        self.plotbox.canvas.clear()
        self.background()
        
        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
    
    def background_main(self):
        self.im = np.zeros((self.n,self.n))
        if(self.wav.functions.size == 0):
            self.im = np.uint8(self.im)
        else:               
            self.inwavef = self.wav.val(self.xx,self.yy) #Complex array, value of initial wavef
            self.im = wavef.Wave.Probability(self,self.inwavef) #Float array, probability from initial wavef
            self.im = self.im + np.abs(self.im.min())
            self.im = np.uint8(255.*(self.im/self.im.max()))
    
    def update_texture_main(self):
        with self.wavebox.canvas:
            cx = self.wavebox.pos[0]
            cy = self.wavebox.pos[1]
            w = self.wavebox.size[0]
            h = self.wavebox.size[1]
            b = min(w,h)
            
            self.plotwave_texture.blit_buffer(self.im.reshape(self.im.size),colorfmt='luminance')
            Color(1.0,1.0,1.0)
            Rectangle(texture = self.plotwave_texture, pos = (cx,cy),size = (b,b))
    
    def add_wave_list(self):
        if(self.partmenu.current_tab.text == 'Eig. Osci.'):
         #   self.particlestrings.append('Eig.Osci.: x0 = {}, y0 = {}, k = {}, a = {}, b={}'.format(round(self.x0slider.value,2),round(self.y0slider.value,2),round(self.kslider.value,2),round(self.aslider.value,2),round(self.bslider.value,2)))
         #   self.particlesave.append('Eig.Osci.: x0 = {}, y0 = {}, k = {}, a = {}, b={}'.format(round(self.x0slider.value,2),round(self.y0slider.value,2),round(self.kslider.value,2),round(self.aslider.value,2),round(self.bslider.value,2)))
         #   self.particles.append(wavef.Wave(self.pot,wavef.InitWavef.OsciEigen([self.xx,self.yy],[self.x0slider.value,self.y0slider.value,self.kslider.value,self.aslider.value,self.bslider.value])))
            self.init_conds.append(wavef.InitWavef.OsciEigen([self.xx,self.yy],[self.x0slider.value,self.y0slider.value,self.kslider.value,self.aslider.value,self.bslider.value]))
            self.wav.add_function(wavef.InitWavef.OsciEigen,[self.x0slider.value,self.y0slider.value,self.kslider.value,self.aslider.value,self.bslider.value])
            
        self.background_main()
        self.update_texture_main()
        
        
        with self.statuslabel.canvas:
            Color = (1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def reset_wave_list(self):
        self.particlestrings = []
        self.particlesave = []
        self.particles = []
        self.init_conds = []
        self.wavebox.canvas.clear()
        self.wav.clear()
      #  self.background()
        
        with self.statuslabel.canvas:
            Color(1,0,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)

    def compute(self):
        with self.statuslabel.canvas:
            Color(0.5,0.5,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
        
        self.initwave = wavef.Wave(self.pot.val(self.xx,self.yy),self.wav.val(self.xx,self.yy))

        self.probability = self.initwave.ProbEvolution() #wavef.Wave.ProbEvolution(self.pot.val,self.wav.val)
       # print(self.probability[:,1,1])
       # print('ok')
            
        with self.statuslabel.canvas:
            Color(0,1,0)
            Rectangle(pos=self.statuslabel.pos,size=self.statuslabel.size)
            
    def play(self):
        self.timer = Clock.schedule_interval(self.animate,0.04) #0.04=interval
        self.running = True
    
    def pause(self):
        if(self.running==True):
            self.timer.cancel()
        else:
            pass
    '''        
    def change_speed(self):
        sl = [1,2,5,10]
        if(self.speedindex == len(sl)-1):
            self.speedindex = 0
        else:
            self.speedindex += 1
        self.speed = sl[self.speedindex]
        self.speedbutton.text = str(self.speed)+'x'
    '''
    def stop(self):
        self.pause()
        self.time = 0
        self.plotbox.canvas.clear()
        self.wavebox.canvas.clear()
        self.update_texture()
    
 #   def save(self):
 #       savedata = np.array([self.pot.functions,self.pot.dfunctionsx,self.pot.dfunctionsy,self.potentialsave,self.particles,self.init_conds,self.particlesave])
 #       with open('save.dat','wb') as file:
 #           pickle.dump(savedata,file)
 #       
 #   def load(self):
 #       with open('save.dat','rb') as file:
 #           savedata = pickle.load(file)
 #       
 #       self.pot.functions = savedata[0]
 #       self.pot.dfunctionsx = savedata[1]
 #       self.pot.dfunctionsy = savedata[2]
 #       self.potentials = savedata[3]
 #       self.particles = savedata[4]
 #       self.init_conds = savedata[5]
 #       self.particlestrings = savedata[6]
 #       
 #       self.background()
 #       self.update_texture()
    def animate(self,interval):
        cx = self.wavebox.pos[0]
        cy = self.wavebox.pos[1]
        w = self.wavebox.size[0]
        h = self.wavebox.size[1]
        b = min(w,h)
        
        dt=0.01
        
        t = self.time % (self.T*dt) # T*dt=Tmax
        t = int(t*self.T)
        
        self.im = self.probability[t,:,:]
        
        self.im = self.im + np.abs(self.im.min())
        self.im = np.uint8(255.*(self.im/self.im.max()))
            
        with self.wavebox.canvas:
            self.plotwave_texture.blit_buffer(self.im.reshape(self.im.size),colorfmt='luminance')
            Color(1.0,1.0,1.0)
            Rectangle(texture = self.plotwave_texture, pos = (cx,cy),size = (b,b))
            
        self.wavebox.canvas.clear()
        self.update_texture_main()
       
        self.time += interval*self.speed
        if(self.time >= self.T*dt):
            self.time = 0.
        
        
        '''
        # create a 64x64 texture, defaults to rgba / ubyte
        texture = Texture.create(size=(64, 64))
        
        # create 64x64 rgb tab, and fill with values from 0 to 255
        # we'll have a gradient from black to white
        size = 64 * 64 * 3
        buf = [int(x * 255 / size) for x in range(size)]
        
        # then, convert the array to a ubyte string
        buf = b''.join(map(chr, buf))
        
        # then blit the buffer
        texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
        
        # that's all ! you can use it in your graphics now :)
        # if self is a widget, you can do this
        with self.canvas:
            Rectangle(texture=texture, pos=self.pos, size=(64, 64))
        
                ---------
        
        counter=0
        while (counter <= int(self.T/self.dt)):
            self.im = self.im[counter,:,:]
            with self.wavebox.canvas:
                self.plotwave_texture.blit_buffer(self.im.reshape(self.im.size),colorfmt='luminance')
                Color(1.0,1.0,1.0)
                Rectangle(texture = self.plotwave_texture, pos = (cx,cy),size = (b,b))
            
            self.time += interval*self.speed
            if(self.time >= self.T):
                self.time = 0.
        '''    
        '''
        w = self.wavebox.size[0]
        h = self.wavebox.size[1]
        b = min(w,h)
     #   scalew = b/200.
     #   scaleh = b/200.
        self.wavebox.canvas.clear()
        self.update_texture_main()
        with self.wavebox.canvas:
                Ellipse(pos=(p.trax(self.time)*scalew+w/2.-5.,p.tray(self.time)*scaleh+h/2.-5.),size=(10,10))
        
        self.time += interval*self.speed
        if(self.time >= self.T):
            self.time = 0.
        '''
            
class BoxApp(App):

    def build(self):
        return main()


if __name__ == '__main__':
    BoxApp().run()