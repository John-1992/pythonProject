#! /usr/bin/env python
# encoding=utf-8

'''
项目分析：
-构成
	-蛇Snake
	-实物Food
	-世界World
-蛇和食物属于整个世界
	class world:
		self.snake
		self.food
	-上面代码不太友好
	-我们用另外一个思路来分析
-我们的分析思路：
	-食物是一个独立的事物
	-蛇也是一个独立的事物
	-世界也是，但世界负责显示
'''

import random
import time
import threading
from tkinter import *
import queue


class Food():
    '''
    功能：
            1.出现在画面的某一个地方
            2.一旦被吃则增加蛇的分数
    '''

    def __init__(self, queue):
        '''
        自动产生一个食物
        '''
        self.queue = queue
        self.new_food()

    def new_food(self):

        '''
        功能：产生一个食物
                产生一个食物的过程也就是随机产生一个食物坐标的过程
        '''
        while True:
        	# 注意横坐标产生的位置
        	x = random.randrange(10,490,10)
        	# 同理产生y坐标
        	y = random.randrange(10,290,10)
        	if((x,y) not in getattr(Snake,'snakePoints')):
            		break
        # 需要注意的是，我们的正规游戏屏幕一般不需要把他设置成正方形
        self.position = x, y  # position存放食物的位置
        # 队列，就是一个不能随意访问内部元素，只能从头弹出一个元素，并只能从队尾追加一个元素的list
        # 把一个食物产生的消息放入队列
        # 消息的格式，自己定义
        # 我的定义是：消息是一个dict，k代表消息类型，v代表此类型的数据
        # queue.put方法中有两个参数，第一个为item必填，第二个为block，默认为1
        self.queue.put({"food": self.position})


class Snake(threading.Thread):
    '''
    蛇的功能：
            1.蛇能动，由我们上下左右按键控制
            2.蛇每次动都需要重新计算蛇头的位置
            3.检测游戏是否完事的功能
    '''
    random_direction = random.choice(['Up','Down', 'Left','Right'])
    random_x = random.randrange(50,450,10)
    random_y = random.randrange(50,250,10)
    if(random_direction == 'Up'):
    	snakePoints = [(random_x, random_y+10), (random_x, random_y+10), (random_x, random_y+10), (random_x, random_y)]
    elif(random_direction == 'Down'):
    	snakePoints = [(random_x, random_y-10), (random_x, random_y-10), (random_x, random_y-10), (random_x, random_y)]
    elif(random_direction == 'Left'):
    	snakePoints = [(random_x+10, random_y), (random_x+10, random_y), (random_x+10, random_y), (random_x, random_y)]
    else:
    	snakePoints = [(random_x-10, random_y), (random_x-10, random_y), (random_x-10, random_y), (random_x, random_y)]

    # auto_direction = random.choice(random_direction)
    # snakePoints = [(490, 50), (480, 50), (470, 50), (460, 50)]
    def __init__(self, world, queue):
        threading.Thread.__init__(self)
        self.world = world
        self.queue = queue
        if(Snake.random_direction == 'Up'):
        	self.direction = random.choice(['Up', 'Left','Right'])
        elif(Snake.random_direction == 'Down'):
        	self.direction = random.choice(['Down', 'Left','Right'])
        elif(Snake.random_direction == 'Left'):
        	self.direction = random.choice(['Up', 'Left','Down'])
        else:
        	self.direction = random.choice(['Up', 'Down','Right'])
        # self.direction = "Up"
        self.points_earned = 0  # 游戏分数
        self.food = Food(self.queue)
        self.snake_points = Snake.snakePoints  # 蛇身各点
        self.start()

    def run(self):
        '''
        一旦启用多线程，调用此函数
        需要蛇一直在跑
        '''
        if self.world.is_game_over:
            self._delete()
        while not self.world.is_game_over:
            self.queue.put({"move": self.snake_points})
            if self.points_earned < 5:
                time.sleep(0.3)
            elif 5 <= self.points_earned < 10:
                time.sleep(0.2)
            elif 10 <= self.points_earned < 15:
                time.sleep(0.15)
            elif 15 <= self.points_earned < 20:
                time.sleep(0.1)
            elif 20 <= self.points_earned < 30:
                time.sleep(0.05)
            elif 30 <= self.points_earned < 40:
                time.sleep(0.03)
            else:
                time.sleep(0.01)
            self.move()

    def move(self):
        '''
        负责蛇的移动：
                1.重新计算蛇头的坐标
                2.当蛇头跟食物相遇，则加分，重新生成食物，通知world，加分
                3.否则，蛇需要动
        '''
        new_snake_point = self.cal_new_position()  # 重新计算蛇头位置
        # 蛇头位置跟食物位置相同
        if self.food.position == new_snake_point:
            self.points_earned += 1
            self.queue.put({"points_earned": self.points_earned})
            self.food.new_food()  # 旧的食物被吃掉产生新的食物
            self.snake_points.append(new_snake_point)
        else:
            # 需要注意蛇的信息的保存方式
            # 每次移动是删除蛇的最前位置，并在后面追加
            self.snake_points.pop(0)
            # 判断程序是否退出，因为新的蛇可能撞墙
            self.check_game_over(new_snake_point)
            self.snake_points.append(new_snake_point)

    def cal_new_position(self):
        '''
        计算新的蛇头位置
        '''
        last_x, last_y = self.snake_points[-1]
        if self.direction == "Up":  # direction负责存储蛇移动的方向
            new_snake_point = last_x, last_y - 10  # 每次移动的跨度是10像素
        elif self.direction == "Down":
            new_snake_point = last_x, last_y + 10
        elif self.direction == "Left":
            new_snake_point = last_x - 10, last_y
        else:
            # self.direction == "Right":
            new_snake_point = last_x + 10, last_y
        return(new_snake_point)

    def key_pressed(self, event):
        # keysym是按键名称
        self.direction = event.keysym

    def check_game_over(self, snake_point):
        '''
        判断的依据是蛇是否撞墙
        把蛇头的坐标拿出来跟墙判断
        '''
        x, y = snake_point[0], snake_point[1]
        if not 0 < x < 500 or not 0 < y < 300 or snake_point in self.snake_points:
            self.queue.put({"game_over": True})


class World(Tk):
    '''
    用来模拟整个游戏画板
    '''

    def __init__(self, queue):
        Tk.__init__(self)
        font1 = ('微软雅黑', 10, 'bold')
        font2 = ('微软雅黑', 10, 'bold', 'underline')
        self.queue = queue
        self.is_game_over = False
        # 定义画板
        self.canvas = Canvas(self, width=500, height=300, bg='#a9dc76')
        self.canvas.pack()

        # 画出蛇和食物
        self.snake = self.canvas.create_line(
            (0, 0), (0, 0), fill='#ad80fe', width=10)
        self.food = self.canvas.create_rectangle(
            0, 0, 0, 0, outline="#ad80fe", width=10, tags="food")
        self.points_earned = self.canvas.create_text(
            450, 20, font=font2, fill='#ffd866', text='SCORE: 0', tags="points")

        # 退出和重玩按钮
        self.frame_button = Frame(width=500, height=40, bg='#a9dc76')
        self.qb = Button(self.frame_button, text='Just Quit', width=30, bg="#33a3dc", fg="#c1c0B7",
            			activebackground="#ad80fe", activeforeground="#ff6188", font=font1, command=self.destroy)
        self.rb = Button(self.frame_button, text='Try Again', width=30, bg="#33a3dc", fg="#c1c0B7",
                    	activebackground="#ad80fe", activeforeground="#a9dc76", font=font1, command=self.again)

        self.queue_handler()

    def queue_handler(self):
        try:
            # 需要不断从消息队列拿到消息，所以使用死循环
            while True:
                task = self.queue.get(block=False)
                if task.get("game_over"):
                    self.game_over()
                if task.get('move'):
                    points = [x for point in task["move"] for x in point]
                    # 重新绘制蛇
                    self.canvas.coords(self.snake, *points)
                # 同样道理，还需要处理食物、得分
                if task.get('food'):
                    self.canvas.coords(self.food, *task['food'], *task['food'])
                if task.get('points_earned'):
                    self.canvas.itemconfigure(
                        self.points_earned, text='SCORE: {}'.format(task['points_earned']))
        except queue.Empty:  # 爆出队列为空异常
            if not self.is_game_over:
                # after的含义是，在多少毫秒后调用后面的函数
                self.canvas.after(100, self.queue_handler)

    def again(self):
        # self.qb.pack_forget()
        # self.rb.pack_forget()
        self.frame_button.pack_forget()
        # 清空画布
        self.canvas.delete(ALL)
        self.queue.queue.clear()
        self.is_game_over = False
        Snake.random_direction = random.choice(['Up', 'Down', 'Left','Right'])
        random_x = random.randrange(50,450,10)
        random_y = random.randrange(50,250,10)
        if(Snake.random_direction == 'Up'):
            	Snake.snakePoints = [(random_x, random_y+10), (random_x, random_y+10), (random_x, random_y+10), (random_x, random_y)]
        elif(Snake.random_direction == 'Down'):
        	Snake.snakePoints = [(random_x, random_y-10), (random_x, random_y-10), (random_x, random_y-10), (random_x, random_y)]
        elif(Snake.random_direction == 'Left'):
        	Snake.snakePoints = [(random_x+10, random_y), (random_x+10, random_y), (random_x+10, random_y), (random_x, random_y)]
        else:
        	Snake.snakePoints = [(random_x-10, random_y), (random_x-10, random_y), (random_x-10, random_y), (random_x, random_y)]

	    # Snake.auto_direction = random.choice(random_direction)
        # Snake.snakePoints = [(490, 50), (480, 50), (470, 50), (460, 50)]
        snake = Snake(self, self.queue)
        self.canvas.pack()

        # 按键绑定
        self.bind('<Key-Left>', snake.key_pressed)
        self.bind('<Key-Right>', snake.key_pressed)
        self.bind('<Key-Up>', snake.key_pressed)
        self.bind('<Key-Down>', snake.key_pressed)

        # 画出蛇和食物
        self.snake = self.canvas.create_line(
            (0, 0), (0, 0), fill='#ad80fe', width=10)
        self.food = self.canvas.create_rectangle(
            0, 0, 0, 0, outline='#ad80fe', width=10)
        self.points_earned = self.canvas.create_text(450, 20, font=(
            '微软雅黑', 10, 'bold', 'underline'), fill='#ffd866', text='SCORE: 0')

        self.queue_handler()

    def game_over(self):
        '''
        游戏结束，清理现场
        '''
        self.is_game_over = True
        self.over = self.canvas.create_text(250, 150, font=(
            '微软雅黑', 40, 'bold', 'italic'), fill='#ff6188', text="Game Over!!", tags="over")
        self.frame_button.pack()
        self.qb.grid(row=0, column=0)
        self.rb.grid(row=0, column=1)


if __name__ == "__main__":
    q = queue.Queue()
    world = World(q)
    world.title("疯狂的贪吃蛇@_@    	[Press ↑ ↓ ← → to play the game.]")
    snake = Snake(world, q)

    world.bind('<Key-Left>', snake.key_pressed)
    # 同样绑定右、上、下键
    world.bind('<Key-Right>', snake.key_pressed)
    world.bind('<Key-Up>', snake.key_pressed)
    world.bind('<Key-Down>', snake.key_pressed)

    world.mainloop()  # 消息循环
