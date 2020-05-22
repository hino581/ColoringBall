import tkinter
import math
import random

# 式設定
cos = math.cos
sin = math.sin
atan = math.atan2

# 基本設定
WIN_WIDTH = 600
WIN_HEIGHT = 600
WILD_SPEED = 10
MILD_SPEED = 10
CLEAR_COLOR = "green"
BOID_NUMBER = 25
FPS = 30
t = 0

class ChargeBar:
    def __init__(self):
        self.width = 20
        self.height = 80
        self.x = WIN_WIDTH/2
        self.y = WIN_HEIGHT/2
        self.point = 0
        self.vector = 5
    def charge(self):
        if (self.point > self.height or self.point+self.vector < 0):
            self.vector *= -1
        self.point += self.vector
    def draw(self, cav):
        self.charge()
        cav.delete("chargepoint")
        cav.create_rectangle(self.x-self.width/2, self.y-self.height/2, self.x+self.width/2, self.y+self.height/2, tag="chargebar", fill="white")
        cav.create_rectangle(self.x-self.width/2, WIN_HEIGHT/2+self.height/2-self.point, self.x+self.width/2, WIN_HEIGHT/2+self.height/2, tag="chargepoint", fill="red")

class Collision:
    def collision(self, obj):
        global t
        distance = ((self.x - obj.x)**2+(self.y - obj.y)**2)**(1/2)
        if (distance < (self.size + obj.size) / 2):
            self.vx -= obj.x - self.x
            self.vy -= obj.y - self.y
            if (type(self) == Ball and type(obj) == One and self.color == CLEAR_COLOR):
                obj.color = CLEAR_COLOR
            if (type(self) == Ball and type(obj) == Ball):
                if (self.v and obj.mode == "stop"):
                    vex,vey = self.x - obj.x, self.y - obj.y
                    if (vey == 0): vey = 1
                    theta = atan(vey,vex)
                    t = theta / self.av 
                    self.mode = "rotate"

class Ball(Collision):
    def __init__(self, coordinates, size, color, rotate=""):
        self.size = size
        self.av = 2 * math.pi / 80
        self.v = rotate
        start = [WIN_WIDTH/2, WIN_HEIGHT/2]
        self.x, self.y = start[0], start[1]
        self.vx, self.vy = 0, 0
        self.color = color
        self.mode = "stop"
        if (color == CLEAR_COLOR):
            self.mode = "rotate"

    def charge(self, event):
        if (self.mode == "rotate"):
            self.mode = "charge"
            self.charge = ChargeBar()
        else:
            pass

    def launcher(self, event):
        if (self.mode == "charge"):
            self.mode = "launcher"
            if (self.charge.point < 0):
                self.charge.point *= -1
            percent = self.charge.point / self.charge.height
            self.vx, self.vy = 1.5 * percent * (self.x - WIN_WIDTH/2), 1.5 * percent * (self.y - WIN_HEIGHT/2)
        else:
            pass

    def linear(self):
        speed = (self.vx**2 + self.vy**2)**(1/2)
        if (speed >= MILD_SPEED):
            self.vx *= MILD_SPEED / speed
            self.vy *= MILD_SPEED / speed
        self.x += self.vx
        self.y += self.vy
        
        if (self.x-self.size/2 < 0 and self.vx < 0 or self.x+self.size/2 > WIN_WIDTH and self.vx > 0):
            self.vx *= -1
        if (self.y-self.size/2 < 0 and self.vy < 0 or self.y+self.size/2 > WIN_HEIGHT and self.vy > 0):
            self.vy *= -1

    def rotate(self, obj=""):
        global t
        self.vx, self.vy = self.v*self.av*cos(self.av*t), self.v*self.av*sin(self.av*t)
        self.x = self.v * cos(self.av*t)+WIN_WIDTH/2
        self.y = self.v * sin(self.av*t)+WIN_HEIGHT/2
        t += 1

    def move(self):
        if (self.mode == "rotate"):
            self.rotate()
        elif (self.mode == "launcher"):
            self.linear()
    def draw(self, cav):
        target = "ball_" + self.color
        cav.delete(target)
        cav.create_oval(self.x-self.size/2, self.y-self.size/2, self.x+self.size/2, self.y+self.size/2, tag=target, fill=self.color)
        cav.create_oval(self.x-self.size/4, self.y-self.size/4, self.x+self.size/4, self.y+self.size/4, tag=target, fill="black")
        self.move()

class One(Collision):
    def __init__(self, coordinates, size, tag):
        self.x, self.y = coordinates[0], coordinates[1]
        self.size = size
        self.vx, self.vy = 0, 0
        self.tag = tag
        self.mode = "move"
        self.color = "blue"

    def move(self):
        self.x += self.vx
        self.y += self.vy

class Boid(Collision):
    def __init__(self, length):
        self.mode = "boid"
        self.value = []
        for i in range(length):
            x = random.random()*WIN_WIDTH
            y = random.random()*WIN_HEIGHT
            self.value.append(One([x,y], 20, i))

    def rule(self):
        for n, i in enumerate(self.value):
            speed = (i.vx**2 + i.vy**2)**(1/2)

            self.cohesion(n)
#            self.separation(n)
            self.alignment(n)

            if (speed >= WILD_SPEED):
                i.vx *= WILD_SPEED / speed
                i.vy *= WILD_SPEED / speed
            
            if (i.x < 0 and i.vx < 0 or i.x+i.size > WIN_WIDTH and i.vx > 0):
                i.vx *= -1
            if (i.y < 0 and i.vy < 0 or i.y+i.size > WIN_HEIGHT and i.vy > 0):
                i.vy *= -1
            i.move()

    def cohesion(self, i):
        center = [0,0]
        for j in range(len(self.value)):
            if j == i:
                continue
            center[0] += self.value[i].x
            center[1] += self.value[i].y
        
        center[0] /= len(self.value) - 1
        center[1] /= len(self.value) - 1

        self.value[i].vx += (center[0] - self.value[i].x) / 100
        self.value[i].vy += (center[0] - self.value[i].y) / 100
    
    def separation(self, i):
        for j in range(len(self.value)):
            if j == i:
                continue
            distance = ((self.value[i].x - self.value[j].x)**2+(self.value[i].y - self.value[j].y)**2)**(1/2)
            if (distance < 10):
                self.value[i].vx -= self.value[j].x - self.value[i].x
                self.value[i].vy -= self.value[j].y - self.value[i].y
    
    def alignment(self, i):
        ave = [0, 0]
        for j in range(len(self.value)):
            if j == i:
                continue
            ave[0] += self.value[j].vx
            ave[1] += self.value[j].vy

        ave[0] /= len(self.value) - 1
        ave[1] /= len(self.value) - 1

        self.value[i].vx += (ave[0] - self.value[i].vx) / 10
        self.value[i].vy += (ave[1] - self.value[i].vy) / 10

    def draw(self, cav):
        for i in self.value:
            target = "enemy" + str(i.tag)
            cav.delete(target)
            cav.create_oval(i.x-i.size/2, i.y-i.size/2, i.x+i.size/2, i.y+i.size/2, tag=target, fill=i.color)
        self.rule()

class Game:
    def __init__(self):
        self.win = tkinter.Tk()
        self.cav = tkinter.Canvas(self.win, width=WIN_WIDTH, height=WIN_HEIGHT)
        cav = self.cav
        cav.pack()
        cav.create_rectangle(0,0,WIN_WIDTH,WIN_HEIGHT,fill="black")
        self.draw = self.obj()
        self.cleartime = 0
        #-------------canvasにクリックイベントを関連付け------------------
        cav.bind("<Button-1>", self.draw[1].charge)
        cav.bind("<ButtonRelease-1>", self.draw[1].launcher)
        self.loop()
        self.win.mainloop()

    def loop(self):
        #-------------当たり判定------------------（Boidクラスインスタンスのパラメータvalueの中のOneクラスインスタンスをcollisionにすべて追加）
        collision = []
        clearflag = True
        for i in self.draw:
            if (type(i) == Boid):
                for j in i.value:
                    if (j.color != CLEAR_COLOR):
                        clearflag = False
                    collision.append(j)
                continue
            collision.append(i)
        for n1, obj1 in enumerate(collision):
            for n2, obj2 in enumerate(collision):
                if (n1 == n2):
                    continue
                obj1.collision(obj2)
        #-------------当たり判定ここまで------------------
        for obj in self.draw:
            if obj.mode != None and obj.mode == "charge":
                obj.charge.draw(self.cav)
            obj.draw(self.cav)
        if (clearflag):
            self.cav.delete("all")
            self.cav.create_rectangle(0, 0, WIN_WIDTH, WIN_HEIGHT, fill="black")
            self.cav.create_text(WIN_WIDTH/2, WIN_HEIGHT/2, fill="yellow", text="GameClear\n"+str(int(self.cleartime))+"秒でクリアしました",font=("System", 20))
        else:
            self.cleartime += FPS*(10**(-3))
            self.win.after(FPS, self.loop)

    def obj(self):
        res = []

        earth = Ball([0,0], 120, "brown")
        res.append(earth)

        ball = Ball([0,0], 30, CLEAR_COLOR, rotate=60+15+1)
        res.append(ball)

        boid = Boid(BOID_NUMBER)
        res.append(boid)

        return res

game = Game()