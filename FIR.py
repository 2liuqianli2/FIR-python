from constant import *
import pygame as py
import sys
from pygame.locals import *
import random



class GoBang:
    def __init__(self, ):
        self.map_size = line_number
        # map_size * map_size的二维列表，用于表示棋盘
        # 0 ~ 无棋子， 1 ~ 黑棋，-1 ~ 白棋
        self.map = [[0 for y in range(0, line_number)] for x in range(0, line_number)]
        # 走棋的历史记录，用于悔棋。它是一个list，它的成员是一个元组(棋子类型，map.x，map.y)
        self.his_stack = []

        self.status = 0
        self.winner = 0

        self.tip1=True
        self.top2=True

    def start_move(self):
        self.status = 1

    def get_last_move(self):
        return self.his_stack[-1]

    def get_winner(self):
        return self.winner

    def get_steps(self):
        return len(self.his_stack)

    # 判断输赢的算法: 只需要判断当前落子相关的四条直线（横、竖、左斜、右斜），是否形成5个连子。
    # 将直线上的落子(黑~ 1，白~ -1)，依次相加，连续的子绝对值之和达到5，即可判定为胜利
    def check_winner(self):
        tmp = 0
        last_step = self.his_stack[-1]
        # 竖向直线, x 固定
        for y in range(0, self.map_size):
            # 必须是连续的
            if y > 0 \
                    and self.map[last_step[1]][y] != self.map[last_step[1]][y - 1]:
                tmp = 0
            tmp += self.map[last_step[1]][y]
            if abs(tmp) >= 5:
                return last_step[0]

        # 横向直线, y 固定
        tmp = 0
        for x in range(0, self.map_size):
            # 必须是连续的
            if x > 0 \
                    and self.map[x][last_step[2]] != self.map[x - 1][last_step[2]]:
                tmp = 0
            tmp += self.map[x][last_step[2]]
            if abs(tmp) >= 5:
                return last_step[0]

        # 右斜直线，计算出左上角顶点的坐标。然后x,y都递增，到达最右下角顶点。
        tmp = 0
        min_dist = min(last_step[1], last_step[2])
        top_point = [last_step[1] - min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            # 不能超出棋盘边界
            if top_point[0] + incr > self.map_size - 1 \
                    or top_point[1] + incr > self.map_size - 1:
                break
            # 必须是连续的
            if incr > 0 \
                    and self.map[top_point[0] + incr][top_point[1] + incr] \
                    != self.map[top_point[0] + incr - 1][top_point[1] + incr - 1]:
                tmp = 0
            tmp += self.map[top_point[0] + incr][top_point[1] + incr]
            if abs(tmp) >= 5:
                return last_step[0]

        # 左斜直线，计算出右上角顶点的坐标。然后x递减、y递增，到达最左下角顶点。
        tmp = 0
        min_dist = min(self.map_size - 1 - last_step[1], last_step[2])
        top_point = [last_step[1] + min_dist, last_step[2] - min_dist]
        for incr in range(0, self.map_size):
            # 不能超出棋盘边界
            if top_point[0] - incr < 0 \
                    or top_point[1] + incr > self.map_size - 1:
                break
            # 必须是连续的
            if incr > 0 \
                    and self.map[top_point[0] - incr][top_point[1] + incr] \
                    != self.map[top_point[0] - incr + 1][top_point[1] + incr - 1]:
                tmp = 0
            tmp += self.map[top_point[0] - incr][top_point[1] + incr]
            if abs(tmp) >= 5:
                return last_step[0]

        return 0

    # 判断本局是否结束
    def check(self):
        # 所有步数已经走完
        if len(self.his_stack) >= self.map_size ** 2:
            return q_finish
        # 赢了
        winner = self.check_winner()
        if winner != 0:
            self.winner = winner
            return q_win
        # 未结束
        return q_ok

    # 走一步棋
    def move(self, x, y):
        if self.status != 1 and self.status != 2:
            return q_stat_err
        if self.map_size <= x or x < 0 \
                or self.map_size <= y or y < 0:
            return q_range_err
        if self.map[x][y] != 0:
            return q_pos_placed

        t = 1 if self.status == 1 else -1
        self.map[x][y] = t
        self.his_stack.append((t, x, y))

        # 判断是否结束
        ret = self.check()
        self.tip=False
        if self.is_finish(ret):
            if ret == q_win :
                self.set_status(3)
            else:
                self.set_status(4)
            return ret

        # 切换状态
        last_step = self.his_stack[-1]
        stat = 2 if last_step[0] == 1 else 1
        self.set_status(stat)
        return q_ok

    def set_status(self, stat):
        self.status = stat

    def is_finish(self, err_code):
        if err_code == q_finish  \
                or err_code == q_win :
            return True
        return False

    # 悔一步棋
    def rollback(self):
        if len(self.his_stack) == 0:
            return q_err
        step = self.his_stack.pop()
        self.map[step[1]][step[2]] = 0
        if self.top2:
            if len(self.his_stack) == 0:
                return q_err
            step = self.his_stack.pop()
            self.map[step[1]][step[2]] = 0

        # 刷新当前状态
        if step[0] == 1:  # 如果当前悔的是黑棋，那么状态切换为等待黑棋落子
            self.status = 1
        elif step[0] == -1:
            self.status = 2
        else:
            return q_err

        return q_ok

    # 获取当前状态
    # 0 ~ 未开局
    # 1 ~ 等待黑棋落子
    # 2 ~ 等待白棋落子
    # 3 ~ 结束（一方获胜）
    # 4 ~ 结束（棋盘走满）
    def get_status(self):
        return self.status

    def get_move_stack(self):
        return self.his_stack


class BigGoBang(GoBang):
    def __init__(self):
        self.size = line_number
        self.unit = size_box
        self.TITLE = '五子棋游戏'
        self.panel_width = 200  # 右侧面板宽度
        self.border_width = local_xy  # 预留宽度

        # 计算棋盘的有效范围
        self.range_x = [self.border_width, self.border_width + (self.size - 1) * self.unit]
        self.range_y = [self.border_width, self.border_width + (self.size - 1) * self.unit]

        # 计算状态面板的有效范围
        self.panel_x = [self.border_width + (self.size - 1) * self.unit, \
                        self.border_width + (self.size - 1) * self.unit + self.panel_width]
        self.panel_y = [self.border_width, self.border_width + (self.size - 1) * self.unit]

        # 计算窗口大小
        self.window_width = self.border_width * 2 \
                            + self.panel_width \
                            + (self.size - 1) * self.unit
        self.window_height = self.border_width * 2 \
                             + (self.size - 1) * self.unit

        # 父类初始化
        super(BigGoBang, self).__init__()
        # 初始化游戏
        self.game_init()

    # 绘制棋盘
    def draw_map(self):
        # 绘制棋盘
        pos_start = [self.border_width, self.border_width]

        s_font = py .font.SysFont('arial', 16)
        # 绘制行
        for item in range(0, self.size):
            py.draw.line(self.screen, b_qicolor ,
                             [pos_start[0], pos_start[1] + item * self.unit],
                             [pos_start[0] + (self.size - 1) * self.unit, pos_start[1] + item * self.unit],
                             1)
            s_surface = s_font.render(f'{item + 1}', True, b_qicolor )
            self.screen.blit(s_surface, [pos_start[0] - 30, pos_start[1] + item * self.unit - 10])

        # 绘制列
        for item in range(0, self.size):
            py.draw.line(self.screen, b_qicolor ,
                             [pos_start[0] + item * self.unit, pos_start[1]],
                             [pos_start[0] + item * self.unit, pos_start[1] + (self.size - 1) * self.unit],
                             1)
            s_surface = s_font.render(chr(ord('A') + item), True,b_qicolor )
            self.screen.blit(s_surface, [pos_start[0] + item * self.unit - 5, pos_start[1] - 30])

    # 绘制棋子
    def draw_chess(self):
        mst = self.get_move_stack()
        for item in mst:
            x = self.border_width + item[1] * self.unit
            y = self.border_width + item[2] * self.unit
            t_color =b_qicolor  if item[0] == 1 else w_qicolor
            py.draw.circle(self.screen, t_color, [x, y], int(self.unit / 2.5))

    # 全部重绘
    def redraw_all(self):
        # 重刷背景图
        background = py.image.load("source/背景.jpeg")
        self.screen.blit(background, (0, 0))
        # 绘制棋盘
        self.draw_map()
        # 绘制棋子
        self.draw_chess()
        # 绘制面板
        self.draw_panel()

    def game_init(self):
        # 初始化pygame
        py.init()
        # 设置窗口的大小，单位为像素
        icon = py.image.load("source/12.png")
        py.display.set_icon(icon)
        self.screen = py.display.set_mode((self.window_width, self.window_height))
        # 设置窗口标题
        py.display.set_caption(self.TITLE)
        # 设置背景颜色
        # self.screen.fill(WHITE)
        background = py.image.load("source/背景.jpeg")
        self.screen.blit(background,(0,0))

        # 加载音效文件
        self.sound_black = py.mixer.Sound('source/1.wav')
        self.sound_white = py.mixer.Sound('source/2.wav')
        self.sound_win = py.mixer.Sound('source/3.wav')
        self.sound_error = py.mixer.Sound('source/4.wav')
        self.sound_start = py.mixer.Sound('source/5.wav')

        # 绘制棋盘
        self.draw_map()

        # 绘制右侧的状态面板
        self.draw_panel()

    def draw_panel(self):
        # panel区域重绘，用白色矩形覆盖
        py.draw.rect(self.screen, w_qicolor ,
                         [self.panel_x[0] + 30, 0,
                          10000, 10000])

        self.panel_font = py.font.SysFont('simhei', 20)

        # 走棋状态
        stat = self.get_status()
        if stat == 0:
            stat_str = '点击开始按钮'
        elif stat == 1:
            stat_str = '等待黑棋落子..'
        elif stat == 2:
            stat_str = '等待白棋落子..'
        elif stat == 4:
            stat_str = '游戏结束！'
        elif stat == 3:
            winner = self.get_winner()
            if winner == 1:
                stat_str = '黑棋获胜！'
            else:
                stat_str = '白棋获胜！'
        else:
            stat_str = ''
        self.surface_stat = self.panel_font.render(stat_str, True, b_qicolor )
        self.screen.blit(self.surface_stat, [self.panel_x[0] + 50, self.panel_y[0] + 50])

        # 步数
        steps = self.get_steps()
        self.surface_steps = self.panel_font.render(f'步数: {steps}', True, b_qicolor )
        self.screen.blit(self.surface_steps, [self.panel_x[0] + 50, self.panel_y[0] + 150])

        # 新的一局
        offset_x = self.panel_x[0] + 50
        offset_y = self.panel_y[0] + 200
        btn_h = 50
        btn_w = 150
        btn_gap = 20
        btn_text_x = 35
        btn_text_y = 15
        self.new_startx = [offset_x, offset_x + btn_w]
        self.new_starty = [offset_y, offset_y + btn_h]
        py.draw.rect(self.screen, b_qicolor ,
                         [offset_x, offset_y,
                          btn_w, btn_h])
        self.surface_btn = self.panel_font.render(f'新开一局', True, w_qicolor )
        self.screen.blit(self.surface_btn, [offset_x + btn_text_x, offset_y + btn_text_y])

        # 退出游戏
        self.gamex = [offset_x, offset_x + btn_w]
        self.gamey = [offset_y + btn_h + btn_gap,
                                      offset_y + btn_h + btn_gap + btn_h]
        py.draw.rect(self.screen, b_qicolor ,
                         [offset_x, offset_y + btn_h + btn_gap,
                          btn_w, btn_h])
        self.surface_btn = self.panel_font.render(f'退出游戏', True, w_qicolor )
        self.screen.blit(self.surface_btn,
                         [offset_x + btn_text_x, offset_y + btn_h + btn_gap + btn_text_y])

        # 悔棋
        self.hqix = [offset_x, offset_x + btn_w]
        self.hqiy = [offset_y + (btn_h + btn_gap) * 2,
                               offset_y + (btn_h + btn_gap) * 2 + btn_h]
        py.draw.rect(self.screen, b_qicolor ,
                         [offset_x, offset_y + (btn_h + btn_gap) * 2,
                          btn_w, btn_h])
        self.surface_btn = self.panel_font.render(f'悔一步棋', True, w_qicolor )
        self.screen.blit(self.surface_btn,
                         [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 2 + btn_text_y])
        # 切换
        self.qiehx = [offset_x, offset_x + btn_w]
        self.qiehy = [offset_y + (btn_h + btn_gap) * 3,
                               offset_y + (btn_h + btn_gap) * 3 + btn_h]
        py.draw.rect(self.screen, b_qicolor ,
                         [offset_x, offset_y + (btn_h + btn_gap) * 3,
                          btn_w, btn_h])

        if self.top2:
            self.surface_btn = self.panel_font.render(f'人机大战', True, w_qicolor)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 3 + btn_text_y])
        else:
            self.surface_btn = self.panel_font.render(f'人人对战', True, w_qicolor)
            self.screen.blit(self.surface_btn,
                             [offset_x + btn_text_x, offset_y + (btn_h + btn_gap) * 3 + btn_text_y])
        py.display.update()

    def qiehuan(self):
        if self.top2 == True:
            self.top2=False
            # print(1)
            self.draw_panel()
            return self.top2
        else:
            self.top2 = True
            # print(2)
            self.draw_panel()
            return self.top2

    def do_move_people(self, pos):
        # 落子在棋盘之外无效
        if pos[0] < self.range_x[0] or pos[0] > self.range_x[1] \
                or pos[1] < self.range_y[0] or pos[1] > self.range_y[1]:
            self.sound_error.play()
            return q_err

        # 播放落子音效
        if self.get_status() == 1:
            self.sound_black.play()
        else:
            self.sound_white.play()
        # 判断当前落子的位置,需要吸附在最近的落棋点
        s_x = round((pos[0] - self.border_width) / self.unit)
        s_y = round((pos[1] - self.border_width) / self.unit)
        x = self.border_width + self.unit * s_x
        y = self.border_width + self.unit * s_y
        # 先move，再draw
        if self.tip1 :
            ret = self.move(s_x, s_y)
            if ret < 0:
                self.sound_error.play()
                return q_err

            # 播放落子音效
            if self.get_status() == 1:
                self.sound_black.play()
            else:
                self.sound_white.play()


            last_move = self.get_last_move()
            t_color = b_qicolor  if last_move[0] == 1 else w_qicolor
            py.draw.circle(self.screen, t_color, [x, y], int(self.unit / 2.5))

            # pygame.draw.circle(self.screen, BLACK, [x, y], int(self.unit / 2.5), 1)

            self.draw_panel()
            py.display.update()

            if self.get_status() >= 3:
                self.sound_win.play()
                return

            # tip2=True
            # if tip2:
            if self.top2:
                self.tip1 = False
                self.do_move_ai()
                py.time.wait(100)
                self.tip1 = True
        return q_ok


    def do_move_ai(self):
        # 落子在棋盘之外无效
        # if pos[0] < self.range_x[0] or pos[0] > self.range_x[1] \
        #         or pos[1] < self.range_y[0] or pos[1] > self.range_y[1]:
        #     self.sound_error.play()
        #     return q_err

        # 播放落子音效
        if self.get_status() == 1:
            self.sound_black.play()
        else:
            self.sound_white.play()
        # # 判断当前落子的位置,需要吸附在最近的落棋点
        # s_x = round((pos[0] - self.border_width) / self.unit)
        # s_y = round((pos[1] - self.border_width) / self.unit)
        #先move，再draw

        py.time.wait(300)
        ret = self.ai_move()
        # 播放落子音效
        if self.get_status() == 1:
            self.sound_black.play()
        else:
            self.sound_white.play()
        if ret < 0:
            self.sound_error.play()
            return q_err
        # draw
        pos = self.his_stack[-1]
        s_x=pos[1]
        s_y=pos[2]
        x = self.border_width + self.unit * s_x
        y = self.border_width + self.unit * s_y
        last_move = self.get_last_move()
        t_color = b_qicolor  if last_move[0] == 1 else w_qicolor
        py.draw.circle(self.screen, t_color, [x, y], int(self.unit / 2.5))
        self.draw_panel()
        py.display.update()
        # pygame.draw.circle(self.screen, BLACK, [x, y], int(self.unit / 2.5), 1)



        if self.get_status() >= 3:
            self.sound_win.play()

        return q_ok

    def do_rollback(self):
        if self.rollback() == q_ok :
            self.redraw_all()

    def do_new_start(self):
        self.__init__()
        self.sound_start.play()
        self.start()

    def do_btn(self, pos):
        # 是否点击了按钮
        if self.new_startx[0] < pos[0] < self.new_startx[1] \
                and self.new_starty[0] < pos[1] < self.new_starty[1]:
            self.do_new_start()
            return q_ok
        elif self.gamex[0] < pos[0] < self.gamex[1] \
                and self.gamey[0] < pos[1] < self.gamey[1]:
            sys.exit()
        elif self.hqix[0] < pos[0] < self.hqix[1] \
                and self.hqiy[0] < pos[1] < self.hqiy[1]:
            if self.get_status() < 3:
                self.do_rollback()
                return q_ok
            else :
                self.sound_error.play()
                return q_ok

        elif self.qiehx[0] < pos[0] < self.qiehx[1] \
                and self.qiehy[0] < pos[1] < self.qiehy[1] and len(self.his_stack) ==0 :
            self.qiehuan()
            return q_ok
        else:
            return q_err

    def ai_move(self):
        self.map      #1或者-1
        self.his_stack  #((-1,4,8))

        for i in range(19):
            count=0
            for j in range(19):
                if self.map[i][j]==0:
                    count = 0
                if self.map[i][j] == -1:
                    count +=-1
                    if count ==-3:
                        if self.map[i][j-3]==0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j-3] = t
                            self.his_stack.append((t, i, j-3))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                        elif self.map[i][j+1]==0 :
                            t = 1 if self.status == 1 else -1
                            self.map[i][j +1] = t
                            self.his_stack.append((t, i, j +1))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                    if count ==-4:
                        if self.map[i][j - 4] == 0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j - 4] = t
                            self.his_stack.append((t, i, j - 4))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                        elif self.map[i][j + 1] == 0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j + 1] = t
                            self.his_stack.append((t, i, j + 1))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok

        for j in range(19):
            count = 0
            for i in range(19):
                if self.map[i][j] == 0:
                    count = 0
                if self.map[i][j] == -1:
                        count += -1
                        if count == -3:
                            if self.map[i-3][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i-3][j ] = t
                                self.his_stack.append((t, i-3, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                            elif self.map[i+1][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i+1][j ] = t
                                self.his_stack.append((t, i+1, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                        if count == -4:
                            if self.map[i-4][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i-4][j ] = t
                                self.his_stack.append((t, i-4, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                            elif self.map[i+1][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i+1][j ] = t
                                self.his_stack.append((t, i+1, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok

        for i in range(19):
            count=0
            for j in range(19):
                if self.map[i][j]==0:
                    count = 0
                if self.map[i][j] == 1:
                    count +=1
                    if count ==3:
                        if self.map[i][j-3]==0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j-3] = t
                            self.his_stack.append((t, i, j-3))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                        elif self.map[i][j+1]==0 :
                            t = 1 if self.status == 1 else -1
                            self.map[i][j +1] = t
                            self.his_stack.append((t, i, j +1))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                    if count ==4:
                        if self.map[i][j - 4] == 0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j - 4] = t
                            self.his_stack.append((t, i, j - 4))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok
                        elif self.map[i][j + 1] == 0:
                            t = 1 if self.status == 1 else -1
                            self.map[i][j + 1] = t
                            self.his_stack.append((t, i, j + 1))
                            # print(x, y)
                            # 判断是否结束
                            ret = self.check()
                            if self.is_finish(ret):
                                if ret == q_win:
                                    self.set_status(3)
                                else:
                                    self.set_status(4)
                                return ret
                            # 切换状态
                            last_step = self.his_stack[-1]
                            stat = 2 if last_step[0] == 1 else 1
                            self.set_status(stat)
                            return q_ok

        for j in range(19):
            count = 0
            for i in range(19):
                if self.map[i][j] == 0:
                    count = 0
                if self.map[i][j] == 1:
                        count += 1
                        if count == 3:
                            if self.map[i-3][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i-3][j ] = t
                                self.his_stack.append((t, i-3, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                            elif self.map[i+1][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i+1][j ] = t
                                self.his_stack.append((t, i+1, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                        if count == 4:
                            if self.map[i-4][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i-4][j ] = t
                                self.his_stack.append((t, i-4, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok
                            elif self.map[i+1][j ] == 0:
                                t = 1 if self.status == 1 else -1
                                self.map[i+1][j ] = t
                                self.his_stack.append((t, i+1, j ))
                                # print(x, y)
                                # 判断是否结束
                                ret = self.check()
                                if self.is_finish(ret):
                                    if ret == q_win:
                                        self.set_status(3)
                                    else:
                                        self.set_status(4)
                                    return ret
                                # 切换状态
                                last_step = self.his_stack[-1]
                                stat = 2 if last_step[0] == 1 else 1
                                self.set_status(stat)
                                return q_ok


        pos=self.his_stack[-1]
        x=pos[1]
        y=pos[2]
        #
        # while self.map[x][y]==1 and 0<x<line_number and 0<y<line_number:
        #     x +=1
        #     y +=1
        #     if self.map[x][y] == -1:
        #         break
        #     if self.map[x][y]!=0 :
        #         continue
        #
        #     # time.sleep(100)
        #     t = 1 if self.status == 1 else -1
        #     self.map[x][y] = t
        #     self.his_stack.append((t, x, y))
        #     print(x,y)
        #     # 判断是否结束
        #     ret = self.check()
        #     if self.is_finish(ret):
        #         if ret == q_win:
        #             self.set_status(3)
        #         else:
        #             self.set_status(4)
        #         return ret
        #     #切换状态
        #     last_step = self.his_stack[-1]
        #     stat = 2 if last_step[0] == 1 else 1
        #     self.set_status(stat)
        #     return q_ok
        # return q_ok
        flag=True
        while (flag):
            m = random.randint(1, 9)
            # line_number边界
            # 右下
            x = pos[1]
            y = pos[2]
            if m == 1:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    x += 1
                    y += 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok

                # 右
                x = pos[1]
                y = pos[2]
                if m == 2:
                    while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                        x += 1
                        if self.map[x][y] == -1:
                            break
                        if self.map[x][y] != 0:
                            continue

                        t = 1 if self.status == 1 else -1
                        self.map[x][y] = t
                        self.his_stack.append((t, x, y))
                        flag = False
                        # 判断是否结束
                        ret = self.check()
                        if self.is_finish(ret):
                            if ret == q_win:
                                self.set_status(3)
                            else:
                                self.set_status(4)
                            return ret

                        # 切换状态
                        last_step = self.his_stack[-1]
                        stat = 2 if last_step[0] == 1 else 1
                        self.set_status(stat)
                        self.tip = True
                        return q_ok

            # 右上角
            x = pos[1]
            y = pos[2]
            if m == 3:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    x += 1
                    y -= 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok

            # 上
            x = pos[1]
            y = pos[2]
            if m == 4:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    y -= 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok

            # 左上
            x = pos[1]
            y = pos[2]
            if m == 5:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    x -= 1
                    y -= 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok
            # 左
            x = pos[1]
            y = pos[2]
            if m == 6:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    x -= 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok
            # 左下
            x = pos[1]
            y = pos[2]
            if m == 7:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    x -= 1
                    y += 1
                    if self.map[x][y] == -1:
                        break
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok
            # 下
            x = pos[1]
            y = pos[2]
            if m == 8:
                while self.map[x][y] == 1 and 0 < x < line_number - 1 and 0 < y < line_number - 1:
                    y -= 1
                    if self.map[x][y] == -1:
                        break
                    if self.map[x][y] != 0:
                        continue

                    t = 1 if self.status == 1 else -1
                    self.map[x][y] = t
                    self.his_stack.append((t, x, y))
                    flag = False
                    # 判断是否结束
                    ret = self.check()
                    if self.is_finish(ret):
                        if ret == q_win:
                            self.set_status(3)
                        else:
                            self.set_status(4)
                        return ret

                    # 切换状态
                    last_step = self.his_stack[-1]
                    stat = 2 if last_step[0] == 1 else 1
                    self.set_status(stat)
                    self.tip = True
                    return q_ok

    def start(self):
        self.start_move()
        self.draw_panel()
        # 程序主循环
        while True:
            # 获取事件
            for event in py.event.get():
                # 判断事件是否为退出事件
                if event.type == QUIT:
                    # 退出pygame
                    py.quit()
                    # 退出系统
                    sys.exit()
                # 落子事件
                if event.type == MOUSEBUTTONDOWN:
                    if self.do_btn(event.pos) < 0:
                        # 非按钮事件，则处理走棋
                        self.do_move_people(event.pos)

            # 绘制屏幕内容
            py.display.update()


if __name__ == '__main__':
    i = BigGoBang()
    i.start()
