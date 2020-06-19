# CSE2025-01 - 2019112130 Yangjin Cho 
# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.font import Font
import time
import random

# 창 크기를 위한 상수로 쓰기위한 전역 변수
w = 800 
h = 600 

# 게임을 시작했는지 안했는지 알려주는 전역 변수 - 엔터키를 눌러서 1이되면 게임 시작
gameState = 0
# 게임 Round 수를 위한 전역 변수
gameRound = 1
# 게임의 점수를 위한 전역 변수 
gameScore = 0

# 게임 진행 속도 (낮을수록 빠름)
gameSpeed = 30

# 정확도 측정을 위한 변수
shootBulletCounter = 0
enemyKillCounter = 0

# 콤보 측정을 위한 변수
comboCounter = 0
maxComboCounter = 0

# 게임의 스프라이트를 나타내는 클래스로 공통적으로 사용되는 변수와 메소드를 가지고 있다.
class Sprite :
    # 생성자		
    def __init__(self, image, x, y):
        self.img = image	# 스프라이트가 가지고 있는 이미지
        self.x = x		# 현재 위치의 x좌표
        self.y = y		# 현재 위치의 y좌표
        self.dx = 0		# 단위시간에 움직이는 x방향 거리
        self.dy = 0      # 단위시간에 움직이는 y방향 거리
                
    # 스프라이트의 가로 길이 반환		
    def getWidth(self) :
        return self.img.width()

    # 스프라이트의 세로 길이 반환		
    def  getHeight(self) :
        return self.img.height()

    # 스프라이트를 화면에 그리기
    def draw(self, g) :
        g.create_image(self.x, self.y, anchor=NW, image=self.img)

    # 스프라이트를 움직이는 메소드
    def move(self) :
        self.x += self.dx
        self.y += self.dy
    
    # dx를 설정하는 설정자 메소드 
    def  setDx(self, dx) :
        self.dx = dx

    # dy를 설정하는 설정자 메소드 
    def  setDy(self, dy) :
        self.dy = dy

    # dx를 반환하는 접근자 메소드 
    def  getDx(self) :
        return self.dx

    # dy를 반환하는 접근자 메소드 
    def  getDy(self) :
        return self.dy

    # x를 반환하는 접근자 메소드 
    def  getX(self) :
        return self.x

    # y를 반환하는 접근자 메소드 
    def  getY(self) :
        return self.y

    # 다른 스프라이트와의 충돌 여부를 계산한다. 충돌이면 true를 반환한다. 
    def  checkCollision(self, other) :
        p1x = self.x
        p1y = self.y
        p2x = self.x+self.getWidth()
        p2y = self.y+self.getHeight()
        p3x = other.x
        p3y = other.y
        p4x = other.x+other.getWidth()
        p4y = other.y+other.getHeight()

        overlapped = not( p4x < p2x or
            p3x > p2x or
            p2y < p3y or
            p1y > p4y)
        return overlapped

    # 충돌을 처리한다. 현재는 아무 일도 하지 않는다. 자식 클래스에서 오버라이드된다. 
    def  handleCollision(self, other) :
        pass

# 우리의 우주선을 나타내는 클래스
class StarShipSprite(Sprite):
    def __init__(self, game, image, x, y):
        super().__init__(image, x, y)
        self.game = game
        self.dx = 0
        self.dy = 0

    # 우주선을 움직인다. 만약 윈도우의 경계를 넘으려고 하면 움직이지 않는다.  
    def move(self):
        if ((self.dx < 0)  and (self.x < 10)) :
            return
        if ((self.dx > 0) and (self.x > 760)) :
            return
        super().move()
        self.dx = 0

    # 충돌을 처리한다. 외계인 우주선과 충돌하면 게임이 종료된다. 
    def handleCollision(self, other) :
        if  type(other) is AlienSprite :
            self.game.endGame()

# 외계인 우주선을 나타내는 클래스
class AlienSprite(Sprite):
    def __init__(self, game, image, x, y):
        super().__init__(image, x, y)
        self.game = game
        self.dx = -10		# x 방향으로만 움직인다. 

    # 외계인 우주선을 움직이는 메소드 
    # 윈도우에 경계에 도달하면 한칸 아래로 이동한다. 
    def move(self):
        if (((self.dx < 0) and (self.x < 10)) or ((self.dx > 0) and (self.x > 760))) :
            self.dx = -self.dx
            self.y += 108
            if (self.y >= 600) :	
                self.game.endGame()
        super().move()

# 포탄을 나타내는 클래스
class ShotSprite(Sprite):
    def __init__(self, game, image, x, y):
        super().__init__(image, x, y)
        self.game = game
        self.dy = -20

    # 화면을 벗어나면 객체를 리스트에서 삭제한다. 
    def move(self):
        super().move()
        global comboCounter
        if (self.y < -100) :
            self.game.removeSprite(self)
            comboCounter = 0

    # 충돌을 처리한다. 포탄과 외계인 우주선 객체를 모두 리스트에서 삭제한다. 
    def handleCollision(self, other) :
        if  type(other) is AlienSprite:
            global gameScore
            global enemyKillCounter
            global comboCounter
            enemyKillCounter += 1
            comboCounter += 1
            gameScore += 10
            # print("LOG: gameScore Changed: "+str(gameScore))
            self.game.removeSprite(self)
            self.game.removeSprite(other)
            
# 게임을 나타내는 클래스
class GalagaGame():

    # 왼쪽 화살표 키 이벤트를 처리하는 함수
    def keyLeft(self, event) :
        self.starship.setDx(-30)
        return

    # 오른쪽 화살표 키 이벤트를 처리하는 함수
    def keyRight(self, event) :
        self.starship.setDx(+30)
        return

    # 스페이스 키 이벤트를 처리하는 함수
    def keySpace(self, event) :
        self.fire()
        return

    # 게임에 필요한 스프라이트를 생성하는 메소드
    def initSprites(self) :
        # 새로운 라운드를 시작할때 스프라이트 클리어 
        self.sprites.clear() 
        global gameRound
        self.starship = StarShipSprite(self, self.shipImage, 370, 520)
        self.sprites.append(self.starship)
        # 게임 라운드 수에 따라 적의 수가 달라짐
        for x in range(0, 1+(gameRound)):
            purpleAlien = AlienSprite(self, self.purpleAlienImage, 600+(x*50), 3*36)
            blueAlien = AlienSprite(self, self.blueAlienImage, 600+(x * 50), 2*36)
            greenAlien = AlienSprite(self, self.greenAlienImage, 600+(x*50), 1*36)
            self.sprites.append(blueAlien)
            self.sprites.append(purpleAlien)
            self.sprites.append(greenAlien)

    # 생성자 메소드
    def __init__(self, master):
        global gameState
        master.bind("<Return>", self.menuStartGame)
        self.master = master
        self.sprites = []
        # 4:3 비율로 캔버스 만들기
        self.canvas = Canvas(master, width=800, height=600)
        self.canvas.pack()
        self.canvas.focus_set()
        # res 폴더 안의 이미지 파일을 사용합니다
        self.shotImage = PhotoImage(file="res\\laser.png")
        self.shipImage = PhotoImage(file="res\\ship.png")
        self.blueAlienImage = PhotoImage(file="res\\enemy2_1.png")
        self.purpleAlienImage = PhotoImage(file="res\\enemy1_1.png")
        self.greenAlienImage = PhotoImage(file="res\\enemy3_1.png")
        self.mysteryImage = PhotoImage(file="res\\mystery.png")
        self.alienDeadImage = PhotoImage(file="res\\explosionblue.png")  
        self.running = True
        master.bind("<Left>",  self.keyLeft)
        master.bind("<Right>", self.keyRight)
        master.bind("<space>", self.keySpace)
        self.initSprites()

    # 이 메소드를 호출하면 gameState를 바꿉니다
    def menuStartGame(self, sprite):
        global gameState
        gameState = 1
        self.running = True
        # print("LOG: Game State Changed to 1")

    # 게임을 시작하는 메소드 
    def startGame(self) :
        self.sprites.clear()
        initSprites()

    # 게임을 종료하는 메소드 
    def endGame(self) :
        self.running = False
        
    
    # 스프라이트를 리시트에서 삭제한다. 
    def removeSprite(self, sprite) :
        if( sprite in self.sprites):
            self.sprites.remove(sprite)
            del sprite

    # 포탄을 발사하는 메소드 
    def fire(self) :
        global shootBulletCounter 
        shootBulletCounter += 1
        shot = ShotSprite(self, self.shotImage, self.starship.getX() + 22,	self.starship.getY() - 0)
        self.sprites.append(shot)

    # 화면을 그리는 메소드 
    def paintMainMenu(self) :
        self.canvas.delete(ALL)
        # 게임 화면의 배경을 검은색으로 색칠합니다.
        self.canvas.create_rectangle(0, 0, 800, 600, fill="black")
        # 메인 화면에 사용될 폰트를 설정합니다.
        # 폰트패밀리는 Chiller로, macOS나 Linux에서는 별도로 설치해야 합니다.
        mainBigMenuFont = Font(family="Chiller", size=85, weight="bold")
        mainSmallMenuFont = Font(family="Chiller", size=35)
        # 메인화면에서 하얀색 점으로 별을 표현합니다. 주석처리를 풀면 적용됩니다.
        # for i in range(20):
        #     x = random.randint(0,w)
        #     y = random.randint(0,h)
        #     self.canvas.create_oval(x,y,x,y,width=0,fill="white")

        # 메인화면에 게임 타이틀을 그립니다.
        self.canvas.create_text(400,200,text="Space Pythonist", fill="red", font=mainBigMenuFont)
        self.canvas.create_text(400,370,text="- Press ENTER -", fill="white", font=mainSmallMenuFont)

    # 게임이 끝났을 때의 화면을 그립니다.
    def paintGameOver(self) :
        # 필요한 전역 변수를 선언합니다.
        global gameScore
        global gameRound
        global maxComboCounter
        global shootBulletCounter
        global enemyKillCounter

        # try문을 사용하여 만약에 사용자가 아무것도 하지 않고 게임 오버 되었을 경우를 예외처리합니다.
        try:
            accuracy = enemyKillCounter/shootBulletCounter
            if accuracy > 1:
                accuracy = 1 # 초반에 100프로를 넘기는 경우가 있음 (탄이 날라가고 적에게 맞기 전까지의 순간)
            accuracy = str(round(round(accuracy,3)*100))+'%'
        except ZeroDivisionError:
            accuracy = "No Bullet Fired"
        
        # Game Over 화면을 위해 화면 상의 모든 것을 지웁니다.
        self.canvas.delete(ALL)
        self.canvas.create_rectangle(0, 0, 800, 600, fill="black")
        # Game Over 화면에서 사용할 폰트를 지정합니다.
        mainBigMenuFont = Font(family="Chiller", size=100, weight="bold")
        mainSmallMenuFont = Font(family="Chiller", size=25)
        # 추가한 기능 - Game Over와 함께 게임 전적을 보여줍니다. 라운드 수, 점수, 최대 콤보, 명중률을 보여줍니다.
        self.canvas.create_text(400,200,text="Game Over", fill="red", font=mainBigMenuFont)
        self.canvas.create_text(400,300,text="Round: "+str(gameRound), fill="white", font=mainSmallMenuFont)
        self.canvas.create_text(400,343,text="Score: "+str(gameScore), fill="white", font=mainSmallMenuFont)
        self.canvas.create_text(400,386,text="Max Combo: "+str(maxComboCounter), fill="white", font=mainSmallMenuFont)
        self.canvas.create_text(400,429,text="Accuracy: "+str(accuracy), fill="white", font=mainSmallMenuFont)

    # 게임이 시작되었을 때의 화면을 그립니다.
    def paintGame(self,g):
        # 메인화면을 지우고 게임 화면을 그립니다.
        self.canvas.delete(ALL)
        # 바탕을 검은색으로 칠합니다.
        self.canvas.create_rectangle(0, 0, 800, 600, fill="black")
        # 라운드, 점수, 콤보수, 명중률을 보여주기 위한 칸을 그립니다. 
        self.canvas.create_rectangle(610,10,790,190, fill="red")
        self.canvas.create_rectangle(615,15,785,185, fill="black")
        # 하얀색 점을 랜덤으로 찍어서 마치 우주선이 우주를 날아다니는 듯한 느낌을 주었습니다.
        for i in range(20):
            x = random.randint(0,w)
            y = random.randint(0,h)
            self.canvas.create_oval(x,y,x,y,width=0,fill="white")
        # 추가한 기능 - 필요한 정보들을 실시간으로 업데이트합니다.
        self.updateAccuracy()
        self.updateCombo()
        self.updateScore()
        self.updateRound()
        self.canvas.update
        for sprite in self.sprites:
            sprite.draw(self.canvas)

    #  추가한 기능 - 정확도를 캔버스에 그려 표시함 
    def updateAccuracy(self):
        global shootBulletCounter
        global enemyKillCounter
        try:
            accuracy = enemyKillCounter/shootBulletCounter
            if accuracy > 1:
                accuracy = 1 # 초반에 100프로를 넘기는 경우가 있음 (탄이 날라가고 적에게 맞기 전까지의 순간)
            accuracy = str(round(round(accuracy,3)*100))+'%'
        except ZeroDivisionError:
            accuracy = "Ready"
        self.canvas.create_text(700,165,fill="white",font="Chiller 22 bold",text='Accuracy: '+accuracy)

    # 추가한 기능 - 콤보를 캔버스에 그려 표시함
    def updateCombo(self):
        global comboCounter
        global maxComboCounter
        if comboCounter>maxComboCounter:
            maxComboCounter = comboCounter
        self.canvas.create_text(700,121,fill="white",font="Chiller 22 bold",text ='Combo: '+str(comboCounter))

    # 추가한 기능 - 점수를 캔버스에 그려 표시함
    def updateScore(self):
        global gameScore
        self.canvas.create_text(700,78,fill="white",font="Chiller 22 bold",text="Score: "+str(gameScore))
    
    # 추가한 기능 - 게임 라운드를 캔버스에 그려 표시함
    def updateRound(self):
        global gameRound
        self.canvas.create_text(700,35,fill="white",font="Chiller 22 bold",text="Round: "+str(gameRound))

    def gameMenuLoop(self):
        self.paintMainMenu()

    def gameOverLoop(self):
        self.paintGameOver()

    # 게임 루프
    def  gameLoop(self) :
        global gameSpeed
        global gameState
        global gameRound
        global gameScore
        if gameState == 0:
            self.master.after(20, self.gameMenuLoop)

        elif gameState == 1:
            for sprite in self.sprites:
                sprite.move()
            # 스프라이트 리스트 안의 객체끼리의 충돌을 검사한다. 
            for  me in self.sprites: 
                for  other in self.sprites :
                    if me != other:
                        if (me.checkCollision(other)) :
                            me.handleCollision(other)
                            other.handleCollision(me)
            self.paintGame(self.canvas)

        # 모든 적이 죽었는지 확인합니다. 
        # self.sprites의 길이가 1이 되어야 하는 이유는 self.sprites 안에 플레이어의 우주선이 있기 때문입니다.
        if (self.running == True) and (len(self.sprites)==1):
            gameRound += 1 # 게임 라운드 변수에 1 더해줌 
            gameSpeed += 10 
            self.initSprites() # 스프라이트 다시 저장 
            self.master.after(gameSpeed+(gameRound-1)*5, self.gameLoop)
        if self.running:
            self.master.after(gameSpeed+(gameRound-1)*5, self.gameLoop)
        elif self.running == False:
            self.master.after(gameSpeed+(gameRound-1)*5, self.gameOverLoop)

root = Tk()
# 추가한 기능 - 게임 프로그램의 제목과 게임 아이콘 설정
root.title("Space Pythonist")
root.iconbitmap("res\\sp.ico")

# def screenshot ():
#     myScreenshot = pyautogui.screenshot()
#     file_path = filedialog.asksaveasfilename(defaulttextsion='.png')
#     myScreenshot.save(file_path)

# 추가한 기능 - 게임 종료 메뉴바
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Quit", command=quit)
# filemenu.add_command(label="Screenshot",command=screenshot)
menubar.add_cascade(label="Menu", underline=0, menu=filemenu)
root.config(menu=menubar)

# 추가한 기능 - 윈도우창의 사이즈 창 크기 조절 불가능 resizable(상하,좌우)
root.resizable(False, False)
# 스크린 가로 세로 길이 데이터를 저장
ws = root.winfo_screenwidth() 
hs = root.winfo_screenheight() 
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# 추가한 기능 - Tkinter 윈도우가 생성되는 위치를 고정 - 화면 한 가운데로
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
# 윈도우 g 생성
g = GalagaGame(root)
root.after(10, g.gameLoop())
root.mainloop()