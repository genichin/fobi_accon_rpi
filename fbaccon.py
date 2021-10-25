import os
import time
import ble
import nfc
import threading
import queue
import time
import fba_common
import RPi.GPIO as GPIO
import pygame

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

message_queue = queue.Queue()

ble_thread = threading.Thread(target=ble.blescan_start, args=(message_queue,))
ble_thread.daemon = True 
ble_thread.start()

nfc_thread = threading.Thread(target=nfc.nfcscan_start, args=(message_queue,))
nfc_thread.daemon = True 
nfc_thread.start()

pygame.init()
pygame.display.set_caption('fobi accon') # 창 제목 설정
displaysurf = pygame.display.set_mode((320, 480), 0, 32) # 메인 디스플레이를 설정한다

font16 = pygame.font.Font("font.ttf", 16)
font24 = pygame.font.Font("font.ttf", 24)
font30 = pygame.font.Font("font.ttf", 30)
font40 = pygame.font.Font("font.ttf", 40)

bgimg = pygame.image.load('320x480.bmp')
bgimg_rect = bgimg.get_rect()

message_rect = pygame.Rect(10,160,300,160)
time_rect = pygame.Rect(0,0,320,100)
navi_rect = pygame.Rect(10,410,300,60)
inout_mode = 0
enable_bg = 1

inout_str = ['출근', '퇴근']
names = ['홍길동', '김철수', '이영희']

old_date_str = ""
old_time_str = ""
msg_text = ""
msg_text_time = time.time()
inout_change_time = time.time()
bg_onoff_time = time.time()

display_update = False

while True:
    try :
        evt, data = message_queue.get(timeout=1)
        print(evt)
        if evt == fba_common.EVENT_BLE_DETECTED :
            print("BLE :", data["value"])
            #msg_text = "BLE : " + data["value"].decode('utf-8')
            msg_text = names[data["value"][0] % 3] + ' ' + inout_str[inout_mode]
            msg_text_time = time.time()
            #GPIO.output(23, GPIO.HIGH)
            #time.sleep(0.2)
            #GPIO.output(23, GPIO.LOW)
            #displaysurf.fill((255,255,255)) # displaysurf를 하얀색으로 채운다
            #displaysurf.blit(pygame.font.SysFont("Eunjin", 70).render(data["value"], 1, (0,0,0)) , hellorect) # displaysurf의 hellorect의 위치에 helloworld를 뿌린다
            display_update = True
        elif evt == fba_common.EVENT_NFC_DETECTED :
            print("NFC :", data)
            #msg_text = "NFC : \n" + data.decode('utf-8')
            msg_text = names[data[0] % 3] + ' ' + inout_str[inout_mode]
            msg_text_time = time.time()
            #GPIO.output(23, GPIO.HIGH)
            #time.sleep(0.2)
            #GPIO.output(23, GPIO.LOW)
            #displaysurf.fill((255,255,255)) # displaysurf를 하얀색으로 채운다
            #displaysurf.blit(pygame.font.SysFont("Eunjin", 70).render(data, 1, (0,0,0)) , hellorect) # displaysurf의 hellorect의 위치에 helloworld를 뿌린다
            display_update = True
    except Exception as e:
        pass

    now = time.time()

    if now - inout_change_time > 5 :
        inout_mode = (inout_mode + 1)%2
        inout_change_time  = now
        display_update = True

    if now - bg_onoff_time > 7 :
        enable_bg = (enable_bg + 1)%2
        bg_onoff_time  = now
        display_update = True


    if msg_text != "" :
        if now - msg_text_time > 3 :
            msg_text = ""
            display_update = True
    
    new_date_str = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    if new_date_str != old_date_str :
        display_update = True
        old_date_str = new_date_str

    new_time_str = time.strftime('%I:%M', time.localtime(time.time()))
    if new_time_str != old_time_str :
        display_update = True
        old_time_str = new_time_str

    if display_update == True:
        if enable_bg == 1 :
            displaysurf.blit(bgimg, bgimg_rect)
        else :
            shape_surf = pygame.Surface(pygame.Rect(bgimg_rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (0,0,0,0), shape_surf.get_rect())
            displaysurf.blit(shape_surf, bgimg_rect)

        shape_surf = pygame.Surface(pygame.Rect(time_rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (0,0,0,128), shape_surf.get_rect())
        displaysurf.blit(shape_surf, time_rect)

        surface_obj = font16.render(old_date_str, 1, (255,255,255))
        rect_obj = surface_obj.get_rect()
        rect_obj.center = (160, 15)
        rect_obj.right = 310
        displaysurf.blit(surface_obj , rect_obj)

        surface_obj = font40.render(old_time_str, 1, (255,255,255))
        rect_obj = surface_obj.get_rect()
        rect_obj.center = (160, 60)
        displaysurf.blit(surface_obj , rect_obj)


        if msg_text != "" :
            shape_surf = pygame.Surface(pygame.Rect(message_rect).size, pygame.SRCALPHA)
            pygame.draw.rect(shape_surf, (255,255,255,128), shape_surf.get_rect(), border_radius=5)
            displaysurf.blit(shape_surf, message_rect)
            surface_obj = font30.render(msg_text, 1, (0,0,0))
            rect_obj = surface_obj.get_rect()
            rect_obj.center = (160, 240)
            displaysurf.blit(surface_obj , rect_obj)

        shape_surf = pygame.Surface(pygame.Rect(navi_rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (255,255,255,128), shape_surf.get_rect(), border_radius=5)
        displaysurf.blit(shape_surf, navi_rect)

        surface_obj = font30.render(inout_str[inout_mode], 1, (0,0,0))
        rect_obj = surface_obj.get_rect()
        rect_obj.center = (160, 440)
        displaysurf.blit(surface_obj , rect_obj)

        pygame.display.update() # 화면을 업데이트한다
        display_update = False