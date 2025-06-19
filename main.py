import pymem
import pymem.process
import pygame
import sys
import offsets as offset
import math
import os
import keyboard
import win32gui
import win32con
import win32api
import time


PrimaryColor = (41, 36, 56)
SecondaryColor = (241, 85, 86) 


is_menu_active = False


PROCESS_NAME = "ac_client.exe"
HEALTH_TEXT_OFFSET = 0x0017E0A8
HEALTH_OFFSET = 0x0018B0B8

ARMOR_TEXT_OFFSET = 0x0018AC00
ARMOR_OFFSET = 0x0018B0B8

ASSAULT_RIFLE_AMMO_OFFSET = 0x0017E0A8
PISTOL_AMMO_OFFSET = 0x0017E0A8
SMG_AMMO_OFFSET = 0x00195404
AWP_AMMO_OFFSET = 0x0017E0A8
SHOTGUN_AMMO_OFFSET = 0x0017E0A8
CARBINE_AMMO_OFFSET = 0x0017E0A8
DUAL_PISTOL_AMMO_OFFSET = 0x0017E0A8

GRENADES_OFFSET = 0x0017E0A8

TRANSPARENT_COLOR = (0, 0, 0)

def get_ac_handle():
    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "AssaultCube" in title:
                extra.append(hwnd)
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None
def make_window_transparent(hwnd):
    extended_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    extended_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, extended_style)
    win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*TRANSPARENT_COLOR), 0, win32con.LWA_COLORKEY)
class Entity():
    def __init__(self):
        self.base_address = None
        self.feet = None
        self.head = None
        self.view = None
        self.health = None
        self.team = None
        self.dead = None
        self.name = None
        self.mag = None
        self.view_angles = viewAngles()

class viewAngles():
    def init__(self):
        self.x = None
        self.y = None

class viewMatrix():
    def __init__(self):
        self.m11 = None
        self.m12 = None
        self.m13 = None
        self.m14 = None
        self.m21 = None
        self.m22 = None
        self.m23 = None
        self.m24 = None
        self.m31 = None
        self.m32 = None
        self.m33 = None
        self.m34 = None
        self.m41 = None
        self.m42 = None
        self.m43 = None
        self.m44 = None


def CalcRect(feet, head):
    rectx = head[0] - (feet[1] -head[1])/ 4
    recty = head[1]

    rectw = (feet[1] - head[1])/2
    recth = feet[1] - head[1]

    return (rectx, recty, rectw, recth)


def get_process():
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        return pm
    except Exception as e:

        return None

def get_base_address(pm):
    try:
        module = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME)
        return module.lpBaseOfDll
    except Exception as e:

        return None

def read_value(pm, address):
    try:
        value = pm.read_int(address)
        return value
    except Exception as e:
        pass


def write_value(pm, address, new_value):
    try:
        pm.write_int(address, new_value)
    except Exception as e:
        pass

def follow_pointer_chain(pm, base, offsets):
    addr = pm.read_int(base)
    for offset in offsets[:-1]:
        addr = pm.read_int(addr + offset)
    final_address = addr + offsets[-1]
    return final_address



pm = get_process()
if pm:
    base_address = get_base_address(pm)
    


def ReadEntity(index):
    enemy = Entity()

    entity_list_ptr = pm.read_int(offset.EntityList)

    entity_ptr = pm.read_int(entity_list_ptr + index * 4)
    if entity_ptr:
        enemy.base_address = entity_ptr
        enemy.head = [
            pm.read_float(entity_ptr + 0x4),
            pm.read_float(entity_ptr + 0x8),
            pm.read_float(entity_ptr + 0xC)
        ]
        enemy.name = pm.read_string(entity_ptr + offset.vName)

    return enemy

def CalcMag(localplayer, destEnt):
    return math.sqrt(math.pow(destEnt.feet[0]-localplayer.feet[0], 2)
                    + math.pow(destEnt.feet[1]-localplayer.feet[1], 2)
                    + math.pow(destEnt.feet[2]-localplayer.feet[2], 2))


def ReadLocalPlayer():
    localplayer = Entity()
    lc = pm.read_int(offset.vlocalplayer)
    localplayer.base_address = lc
    localplayer.view_angles.x = pm.read_float(lc + offset.vAngles)
    localplayer.view_angles.y = pm.read_float(lc + offset.vAngles + 0x4)
    localplayer.name = pm.read_string(lc + offset.vName)
    localplayer.health = pm.read_int(lc + offset.vHealth)
    localplayer.dead = pm.read_int(lc + offset.vDead)
    localplayer.team = pm.read_int(lc + offset.vTeam)
    localplayer.feet = [pm.read_float(lc + offset.vFeet), pm.read_float(lc + offset.vFeet + 0x4), pm.read_float(lc + offset.vFeet + 0x8)]
    localplayer.head = [pm.read_float(lc + offset.vHead), pm.read_float(lc + offset.vHead + 0x4), pm.read_float(lc + offset.vHead + 0x8)]
    return localplayer


def ReadMatrix():
    viewM = viewMatrix()

    
    viewM.m11 = pm.read_float(base_address + offset.viewMatrix + 0x0)
    viewM.m12 = pm.read_float(base_address + offset.viewMatrix + 0x4)
    viewM.m13 = pm.read_float(base_address + offset.viewMatrix + 0x8)
    viewM.m14 = pm.read_float(base_address + offset.viewMatrix + 0xC)
    viewM.m21 = pm.read_float(base_address + offset.viewMatrix + 0x10)
    viewM.m22 = pm.read_float(base_address + offset.viewMatrix + 0x14)
    viewM.m23 = pm.read_float(base_address + offset.viewMatrix + 0x18)
    viewM.m24 = pm.read_float(base_address + offset.viewMatrix + 0x1C)
    viewM.m31 = pm.read_float(base_address + offset.viewMatrix + 0x20)
    viewM.m32 = pm.read_float(base_address + offset.viewMatrix + 0x24)
    viewM.m33 = pm.read_float(base_address + offset.viewMatrix + 0x28)
    viewM.m34 = pm.read_float(base_address + offset.viewMatrix + 0x2C)
    viewM.m41 = pm.read_float(base_address + offset.viewMatrix + 0x30)
    viewM.m42 = pm.read_float(base_address + offset.viewMatrix + 0x34)
    viewM.m43 = pm.read_float(base_address + offset.viewMatrix + 0x38)
    viewM.m44 = pm.read_float(base_address + offset.viewMatrix + 0x3C)

    return viewM

def WorldToScreen(mtx, pos, width, height):
    screenW = (mtx.m14 * pos[0]) + (mtx.m24 * pos[1]) + (mtx.m34 * pos[2]) + mtx.m44
    if screenW > 0.001:
        screenX = (mtx.m11 * pos[0]) + (mtx.m21 * pos[1]) + (mtx.m31 * pos[2]) + mtx.m41
        screenY = (mtx.m12 * pos[0]) + (mtx.m22 * pos[1]) + (mtx.m32 * pos[2]) + mtx.m42

        camX = width / 2.0
        camY = height / 2.0

        X = camX + (camX * screenX / screenW)
        Y = camY - (camY * screenY / screenW)


        return (int(X), int(Y))
    else:
        return (-99, -99)


class Checkbox:
    def __init__(self, x, y, size, id, text="", color_inactive=(29, 25, 39), color_active=SecondaryColor, border_color=(16, 14, 22)):
        self.rect = pygame.Rect(x + 20, y + 25, size, size)
        self.frame = pygame.Rect(x, y, 400, 100)
        self.id = id
        self.text = text
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.border_color = border_color
        self.active = False


        self.font = pygame.font.SysFont('centurygothic', 24, bold=True)

    def draw(self, surface):
        if cursor == self.id:
            pygame.draw.rect(surface, (29, 25, 39), self.frame)
        else:
            pygame.draw.rect(surface, PrimaryColor, self.frame)

        pygame.draw.rect(surface, self.color_active if self.active else self.color_inactive, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 5)

        if self.text:
            text_surface = self.font.render(self.text, True, SecondaryColor)
            text_rect = text_surface.get_rect()
            text_rect.topleft = (self.rect.right + 10, self.rect.top+10)
            surface.blit(text_surface, text_rect)

            

class Button:
    def __init__(self, rect, text, onclick, font, color=(200,200,200), text_color=(0,0,0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.onclick = onclick
        self.font = font
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.onclick()


def Suicide():
    print('placeholder')


def calcDist(localplayer, destEnt):
    return math.sqrt(math.pow(destEnt.feet[0]-localplayer.feet[0], 2)
                    + math.pow(destEnt.feet[1]-localplayer.feet[1], 2))

def calcAngles(localplayer, destEnt):
    deltaX = destEnt.head[0] - localplayer.head[0]
    deltaY = destEnt.head[1] - localplayer.head[1]
    deltaZ = destEnt.head[2] - localplayer.head[2]
    dist = calcDist(localplayer, destEnt)

    x = float(math.atan2(deltaY, deltaX) * 180 / math.pi) + 90
    y = float(math.atan2(deltaZ, dist) * 180 / math.pi)
    return (x,y)


def Aim(ent, vec2):
    pm.write_float(ent.base_address + offset.vAngles, vec2[0])
    pm.write_float(ent.base_address + offset.vAngles + 0x4, vec2[1])

    
    


osc_value = 1
osc_increasing = True




ac_hwnd = get_ac_handle()
if not ac_hwnd:
    print("AssaultCube not found.")
left, top, right, bottom = win32gui.GetWindowRect(ac_hwnd)
width, height = right - left, bottom - top

pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = f"{left},{top}"
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
pygame.display.set_caption("Overlay")
hwnd = pygame.display.get_wm_info()["window"]
make_window_transparent(hwnd)
clock = pygame.time.Clock()
drawing = False
last_pos = None

options = []

Health_checkbox = Checkbox(7, 235, 50, 1, "Health")
Armor_checkbox  = Checkbox(7, 335, 50, 2, "Armor")
Ammo_checkbox = Checkbox(7, 435, 50, 3, "Ammo")
Grenades_checkbox = Checkbox(7, 535, 50, 4, "Grenades")
Randomize_checkbox = Checkbox(7, 635, 50, 5, "Fun Mode")
RapidFire_checkbox = Checkbox(7, 735, 50, 6, "Rapid Fire")
NoRecoil_checkbox = Checkbox(7, 835, 50, 7, "No Recoil")
Aimbot_checkbox = Checkbox(7, 935, 50, 8, "Aimbot (press z)")
ESP_checkbox = Checkbox(407, 235, 50, 9, "ESP")
Traces_checkbox = Checkbox(407, 335, 50, 10, "Traces")
FriendlyFire_checkbox = Checkbox(407, 435, 50, 11, "Friendly Fire")


options.append(Health_checkbox)
options.append(Armor_checkbox)
options.append(Ammo_checkbox)
options.append(Grenades_checkbox)
options.append(Randomize_checkbox)
options.append(RapidFire_checkbox)
options.append(NoRecoil_checkbox)
options.append(Aimbot_checkbox)
options.append(ESP_checkbox)
options.append(Traces_checkbox)
options.append(FriendlyFire_checkbox)

right_shift_pressed = False
uparrow = False
downarrow = False
enterbtn = False
leftarrow = False
rightarrow = False

cursor = 1

arrowSolid = pygame.image.load("assets/arrowSolid.png")
arrowOutline = pygame.image.load("assets/arrowOutline.png")
enterSolid = pygame.image.load("assets/enterSolid.png")
enterOutline = pygame.image.load("assets/enterOutline.png")

discord = pygame.image.load("assets/discord.png")
github = pygame.image.load("assets/github.png")


upArrow_image = pygame.transform.rotate(arrowOutline, 180)
downArrow_image = pygame.transform.rotate(arrowOutline, 0)
leftArrow_image = pygame.transform.rotate(arrowOutline, 90)
rightArrow_image = pygame.transform.rotate(arrowOutline, 270)

upArrow_image_solid = pygame.transform.rotate(arrowSolid, 180)
downArrow_image_solid = pygame.transform.rotate(arrowSolid, 0)
leftArrow_image_solid = pygame.transform.rotate(arrowSolid, 90)
rightArrow_image_solid = pygame.transform.rotate(arrowSolid, 270)

font = pygame.font.SysFont('centurygothic', 24, bold=True)

contact_surface = font.render("C O N T A C T", True, SecondaryColor)


discord_surface = font.render("catab2050", True, SecondaryColor)


github_surface = font.render("catab60", True, SecondaryColor)



class AnimatedStrip:
    def __init__(self, image_paths, position=(0, 0), size=(800, 200), frame_delay=2):
        self.images = [pygame.image.load(path).convert_alpha() for path in image_paths]
        self.num_frames = len(self.images)
        self.frame_delay = frame_delay
        self.frame_index = 0
        self.k = 0
        self.rect = pygame.Rect(position, size)

    def update(self):
        self.k += 1
        if self.k % self.frame_delay == 0:
            self.frame_index = (self.frame_index + 1) % self.num_frames

    def draw(self, surface):
        frame = self.images[self.frame_index]
        frame = pygame.transform.scale(frame, self.rect.size)
        surface.blit(frame, self.rect.topleft)


logo_paths = [f"assets/logo/{i}.png" for i in range(30)] 
anim_logo = AnimatedStrip(logo_paths, (7,30))

while True:

    if win32gui.IsIconic(ac_hwnd) or win32gui.GetForegroundWindow() != ac_hwnd:
        screen.fill(TRANSPARENT_COLOR)
        pygame.display.update()
        time.sleep(0.1)
        continue

    left, top, right, bottom = win32gui.GetWindowRect(ac_hwnd)
    width, height = right - left, bottom - top

    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, left, top, width, height, win32con.SWP_SHOWWINDOW)

    screen.fill(TRANSPARENT_COLOR)


    LiveEnemy = []
    entList = []

    seen_ptrs = set()
    for i in range(1, 32):
        try:
            entity_list_ptr = pm.read_int(offset.EntityList)
            entity_ptr = pm.read_int(entity_list_ptr + i * 4)
            if not entity_ptr or entity_ptr in seen_ptrs:
                continue
            seen_ptrs.add(entity_ptr)
            enemy = Entity()
            enemy.base_address = entity_ptr
            enemy.head = [
                pm.read_float(entity_ptr + 0x4),
                pm.read_float(entity_ptr + 0x8),
                pm.read_float(entity_ptr + 0xC)
            ]
            enemy.name = pm.read_string(entity_ptr + offset.vName)
            enemy.health = pm.read_int(entity_ptr + offset.vHealth)
            enemy.dead = pm.read_int(entity_ptr + offset.vDead)
            enemy.team = pm.read_int(entity_ptr + offset.vTeam)
            enemy.feet = [
                pm.read_float(entity_ptr + offset.vFeet),
                pm.read_float(entity_ptr + offset.vFeet + 0x4),
                pm.read_float(entity_ptr + offset.vFeet + 0x8)
            ]

            if not enemy.name or enemy.name.strip() == "":
                continue
            entList.append(enemy)
        except Exception as e:
            pass



    localplayer = ReadLocalPlayer()
    for i, ent in enumerate(entList):
        ent.mag = CalcMag(localplayer, ent)
        if ent.health > 0 and ent.health <= 100:
            LiveEnemy.append(ent)
    
    LiveEnemy.sort(key=lambda x: x.mag)
    if Aimbot_checkbox.active:
        if keyboard.is_pressed('z'):
            if len(LiveEnemy) > 0:

                for i in LiveEnemy:
                    if not FriendlyFire_checkbox.active:
                        if i.team != localplayer.team:
                            
                            vec2 = calcAngles(localplayer, i)

                            Aim(localplayer, vec2)
                            break
                    else:
                        vec2 = calcAngles(localplayer, i)

                        Aim(localplayer, vec2)
                        break
        
    
    







    if osc_increasing:
        osc_value += 123
        if osc_value >= 876:
            osc_increasing = False
    else:
        osc_value -= 123
        if osc_value <= 223:
            osc_increasing = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True
            last_pos = pygame.mouse.get_pos()
        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            last_pos = None
    if drawing and last_pos:
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 0, 0), last_pos, mouse_pos, 1)
        last_pos = mouse_pos









    if ESP_checkbox.active:
        for i in LiveEnemy:
            wtsFeet = WorldToScreen(ReadMatrix(), i.feet, width, height)
            wtsHead = WorldToScreen(ReadMatrix(), i.head, width, height)
            
            ftt = CalcRect(wtsFeet, wtsHead)
            value = max(0, min(100, i.health))
            bar_x = ftt[0] + ftt[2] + 2
            bar_y = ftt[1]
            bar_width = 5
            bar_height = ftt[3]
            fill_height = int(bar_height * (value / 100.0))
            fill_y = bar_y + (bar_height - fill_height)
            r = int(255 * (1 - value / 100.0))
            g = int(255 * (value / 100.0))
            color = (r, g, 0)
            pygame.draw.rect(screen, color, (bar_x, fill_y, bar_width, fill_height))
    
    

            if wtsFeet[0] > 0:
                if localplayer.team == i.team:
                    if Traces_checkbox.active:
                        pygame.draw.line(screen, (92,207,255), (width//2, height), wtsFeet)
                    pygame.draw.rect(screen, (92,207,255), ftt, 1)

                    pygame.draw.rect(screen, (0,0,0), (ftt[0]+ftt[2]+2, ftt[1], 5, ftt[3]))
                    pygame.draw.rect(screen, color, (bar_x, fill_y, bar_width, fill_height))



                    
                else:
                    if Traces_checkbox.active:
                        pygame.draw.line(screen, (225,95,75), (width//2, height), wtsFeet)
                    pygame.draw.rect(screen, (225,95,75), CalcRect(wtsFeet, wtsHead), 1)

                    pygame.draw.rect(screen, (0,0,0), (ftt[0]+ftt[2]+2, ftt[1], 5, ftt[3]))
                    pygame.draw.rect(screen, color, (bar_x, fill_y, bar_width, fill_height))











    if is_menu_active:
        pygame.draw.rect(screen, PrimaryColor, (7,30,800, height-35))

        anim_logo.update()
        anim_logo.draw(screen)



        
        screen.blit(contact_surface, (425, 815))

        screen.blit(discord, (425, 890-25))
        screen.blit(github, (425, 950))


        screen.blit(discord_surface, (515, 890-10))
        screen.blit(github_surface, (515, 950+10))


        Health_checkbox.draw(screen)
        Armor_checkbox.draw(screen)
        Ammo_checkbox.draw(screen)

        Grenades_checkbox.draw(screen)
        Randomize_checkbox.draw(screen)
        RapidFire_checkbox.draw(screen)
        NoRecoil_checkbox.draw(screen)
        Aimbot_checkbox.draw(screen)
        ESP_checkbox.draw(screen)
        Traces_checkbox.draw(screen)
        FriendlyFire_checkbox.draw(screen)



    if keyboard.is_pressed('right shift'):
        if not right_shift_pressed:

            if is_menu_active:
                is_menu_active = False
            else:
                is_menu_active = True

            right_shift_pressed = True
    else:
        right_shift_pressed = False


    
    if keyboard.is_pressed("up arrow"):
        if is_menu_active:
            if not uparrow:
                if cursor > 1:
                    cursor = cursor - 1
                uparrow = True
            screen.blit(upArrow_image_solid, (400 + 200 -100, 600)) 
    else:
        if is_menu_active:
            uparrow = False
            screen.blit(upArrow_image, (400 + 200 -100, 600))





    if keyboard.is_pressed("left arrow"):
        if is_menu_active:
            if not leftarrow:
                if cursor == 9:
                    cursor = 1
                if cursor == 10:
                    cursor = 2
                if cursor == 11:
                    cursor = 3
                leftarrow = True
            screen.blit(rightArrow_image_solid, (400 + 200 -70-100, 670))
    else:
        if is_menu_active:
            leftarrow = False
            screen.blit(rightArrow_image, (400 + 200 -70-100, 670))
            



    
    if keyboard.is_pressed("right arrow"):
        if is_menu_active:
            if not rightarrow:
                if cursor == 1:
                    cursor = 9
                if cursor == 2:
                    cursor = 10
                if cursor == 3:
                    cursor = 11
                rightarrow = True
            screen.blit(leftArrow_image_solid, (400 + 200 +70-100, 670))
    else:
        if is_menu_active:
            rightarrow = False
            screen.blit(leftArrow_image, (400 + 200 +70-100, 670))



    if keyboard.is_pressed("enter"):
        if is_menu_active:
            if not enterbtn:
                for i in options:
                    if i.id == cursor:
                        if i.active == True:
                            i.active = False
                        else:
                            i.active = True
                enterbtn = True
            screen.blit(enterSolid, (667-13,600))
    else:
        if is_menu_active:
            enterbtn = False
            screen.blit(enterOutline, (667-13,600))



    if keyboard.is_pressed("down arrow"):
        if is_menu_active:
            if not downarrow:
                if cursor < len(options):
                    cursor = cursor + 1
                downarrow = True
            screen.blit(downArrow_image_solid, (400 + 200 -100, 670))
    else:
        if is_menu_active:
            downarrow = False
            screen.blit(downArrow_image, (400 + 200 -100, 670))
        

    
    pygame.display.flip()

    if Health_checkbox.active:
        if base_address:

            health_text_address = base_address + HEALTH_TEXT_OFFSET
            health_text_address = pm.read_int(health_text_address)
            health_text_address = health_text_address + 0xEC

            health_address = base_address + HEALTH_OFFSET
            health_address = follow_pointer_chain(pm, health_address, [0x0, 0x408])

            if Randomize_checkbox.active:
                pm.write_int(health_text_address, osc_value)
            else:
                pm.write_int(health_text_address, 999)
            pm.write_int(health_address, 999)
            

    if Armor_checkbox.active:
        if base_address:
            armor_text_address = base_address + ARMOR_TEXT_OFFSET
            armor_text_address = pm.read_int(armor_text_address)
            armor_text_address = armor_text_address + 0xF0

            armor_address = base_address + ARMOR_OFFSET
            armor_address = follow_pointer_chain(pm, armor_address, [0x40C])


            if Randomize_checkbox.active:
                pm.write_int(armor_text_address, osc_value)
            else:
                pm.write_int(armor_text_address, 999)
            pm.write_int(armor_address, 999)




    if Ammo_checkbox.active:
        if base_address:
            ar_ammo_address = base_address + ASSAULT_RIFLE_AMMO_OFFSET
            ar_ammo_address = pm.read_int(ar_ammo_address)
            ar_ammo_address = ar_ammo_address + 0x140

    
            p_ammo_address = base_address + PISTOL_AMMO_OFFSET
            p_ammo_address = pm.read_int(p_ammo_address)
            p_ammo_address = p_ammo_address + 0x12C

            smg_ammo_address = base_address + SMG_AMMO_OFFSET
            smg_ammo_address = pm.read_int(smg_ammo_address)
            smg_ammo_address = smg_ammo_address + 0x138

            

            awp_ammo_address = base_address + AWP_AMMO_OFFSET
            awp_ammo_address = pm.read_int(awp_ammo_address)
            awp_ammo_address = awp_ammo_address + 0x13C

            shotgun_ammo_address = base_address + SHOTGUN_AMMO_OFFSET
            shotgun_ammo_address = pm.read_int(shotgun_ammo_address)
            shotgun_ammo_address = shotgun_ammo_address + 0x134

            carbine_ammo_address = base_address + CARBINE_AMMO_OFFSET
            carbine_ammo_address = pm.read_int(carbine_ammo_address)
            carbine_ammo_address = carbine_ammo_address + 0x130

            dual_pistol_ammo_address = base_address + DUAL_PISTOL_AMMO_OFFSET
            dual_pistol_ammo_address = pm.read_int(dual_pistol_ammo_address)
            dual_pistol_ammo_address = dual_pistol_ammo_address + 0x148



        




            if Randomize_checkbox.active:
                pm.write_int(ar_ammo_address, osc_value)
                pm.write_int(p_ammo_address, osc_value)
                pm.write_int(smg_ammo_address, osc_value)
                pm.write_int(awp_ammo_address, osc_value)
                pm.write_int(shotgun_ammo_address, osc_value)
                pm.write_int(carbine_ammo_address, osc_value)
                pm.write_int(dual_pistol_ammo_address, osc_value)
            else:
                pm.write_int(ar_ammo_address, 999)
                pm.write_int(p_ammo_address, 999)
                pm.write_int(smg_ammo_address, 999)
                pm.write_int(awp_ammo_address, 999)
                pm.write_int(shotgun_ammo_address, 999)
                pm.write_int(carbine_ammo_address, 999)
                pm.write_int(dual_pistol_ammo_address, 999)

    if Grenades_checkbox.active:
        if base_address:
            grenades_address = base_address + GRENADES_OFFSET
            grenades_address = pm.read_int(grenades_address)
            grenades_address = grenades_address + 0x144

            if Randomize_checkbox.active:
                pm.write_int(grenades_address, osc_value)
            else:
                pm.write_int(grenades_address, 999)

    if RapidFire_checkbox.active:
        if base_address:
            ar_fire = base_address + 0x0018AC00
            ar_fire = pm.read_int(ar_fire)
            ar_fire = ar_fire + 0x164
            pm.write_int(ar_fire, 0)

            smg_fire = base_address + 0x0017E0A8
            smg_fire = pm.read_int(smg_fire)
            smg_fire = smg_fire + 0x15C
            pm.write_int(smg_fire, 0)

            awp_fire = base_address + 0x0017E0A8
            awp_fire = pm.read_int(awp_fire)
            awp_fire = awp_fire + 0x160
            pm.write_int(awp_fire, 0)

            shotgun_fire = base_address + 0x0017E0A8
            shotgun_fire = pm.read_int(shotgun_fire)
            shotgun_fire = shotgun_fire + 0x158
            pm.write_int(shotgun_fire, 0)

            carbine_fire = base_address + 0x0017E0A8
            carbine_fire = pm.read_int(carbine_fire)
            carbine_fire = carbine_fire + 0x154
            pm.write_int(carbine_fire, 0)


            dual_pistol_fire = base_address + 0x0017E0A8
            dual_pistol_fire = pm.read_int(dual_pistol_fire)
            dual_pistol_fire = dual_pistol_fire + 0x16C
            pm.write_int(dual_pistol_fire, 0)


    if NoRecoil_checkbox.active:
        if base_address:
            recoil_address = base_address + 0x18AC00
            recoil_address = pm.read_int(recoil_address)
            recoil_address = recoil_address + 0x368
            recoil_address = pm.read_int(recoil_address)
            recoil_address = recoil_address + 0xC
            recoil_address = pm.read_int(recoil_address)
            recoil_address = recoil_address + 0x5E
            pm.write_int(recoil_address, 0)

            






    pygame.display.update()
    clock.tick(60)








