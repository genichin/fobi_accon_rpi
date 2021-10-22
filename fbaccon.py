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
pygame.display.set_caption('Hello, world!') # 창 제목 설정
displaysurf = pygame.display.set_mode((600, 400), 0, 32) # 메인 디스플레이를 설정한다
clock = pygame.time.Clock() # 시간 설정

font24 = pygame.font.Font("font.ttf", 24)
font30 = pygame.font.Font("font.ttf", 30)
font40 = pygame.font.Font("font.ttf", 40)

#gulimfont = pygame.font.SysFont('DejaVuSerif', 70) # 서체 설정
gulimfont = pygame.font.SysFont(None, 70) # 서체 설정
helloworld = gulimfont.render('Hello, world!', 1, (0,0,0)) 
# .render() 함수에 내용과 안티앨리어싱, 색을 전달하여 글자 이미지 생성
hellorect = helloworld.get_rect() # 생성한 이미지의 rect 객체를 가져온다
hellorect.center = (600 / 2, 400 / 2) # 해당 rect의 중앙을 화면 중앙에 맞춘다
clock_font = pygame.font.SysFont(None, 24) # 서체 설정
clock_rect = pygame.Rect(0,0,240,40)
bgimg = pygame.image.load('320x480.bmp')
bgimg_rect = bgimg.get_rect()

'''
while True: # 아래의 코드를 무한 반복한다.
    displaysurf.fill((255,255,255)) # displaysurf를 하얀색으로 채운다
    displaysurf.blit(helloworld, hellorect) # displaysurf의 hellorect의 위치에 helloworld를 뿌린다
    
    pygame.display.update() # 화면을 업데이트한다
    clock.tick(30) # 화면 표시 회수 설정만큼 루프의 간격을 둔다
'''

old_time_str = ""
msg_text = ""
msg_text_time = time.time()

display_update = False

while True:
    try :
        evt, data = message_queue.get(timeout=1)
        print(evt)
        if evt == fba_common.EVENT_BLE_DETECTED :
            print("BLE :", data["value"])
            msg_text = "BLE : " + data["value"].decode('utf-8')
            msg_text_time = time.time()
            #GPIO.output(23, GPIO.HIGH)
            #time.sleep(0.2)
            #GPIO.output(23, GPIO.LOW)
            #displaysurf.fill((255,255,255)) # displaysurf를 하얀색으로 채운다
            #displaysurf.blit(pygame.font.SysFont("Eunjin", 70).render(data["value"], 1, (0,0,0)) , hellorect) # displaysurf의 hellorect의 위치에 helloworld를 뿌린다
            display_update = True
        elif evt == fba_common.EVENT_NFC_DETECTED :
            print("NFC :", data)
            msg_text = "NFC : \n" + data.decode('utf-8')
            msg_text_time = time.time()
            #GPIO.output(23, GPIO.HIGH)
            #time.sleep(0.2)
            #GPIO.output(23, GPIO.LOW)
            #displaysurf.fill((255,255,255)) # displaysurf를 하얀색으로 채운다
            #displaysurf.blit(pygame.font.SysFont("Eunjin", 70).render(data, 1, (0,0,0)) , hellorect) # displaysurf의 hellorect의 위치에 helloworld를 뿌린다
            display_update = True
    except Exception as e:
        pass

    if msg_text != "" :
        if time.time() - msg_text_time > 3 :
            msg_text = ""
            display_update = True
    
    new_time_str = time.strftime('%c', time.localtime(time.time()))
    if new_time_str != old_time_str :
        display_update = True
        old_time_str = new_time_str

    if display_update == True:
        displaysurf.blit(bgimg, bgimg_rect)

        surface_obj = font24.render(old_time_str, 1, (255,255,255))
        rect_obj = surface_obj.get_rect()
        rect_obj.center = (160, 15)
        displaysurf.blit(surface_obj , rect_obj)

        if msg_text != "" :
            surface_obj = font30.render(msg_text, 1, (255,255,255))
            rect_obj = surface_obj.get_rect()
            rect_obj.center = (160, 240)
            displaysurf.blit(surface_obj , rect_obj)

        surface_obj = font40.render("퇴근", 1, (255,255,255))
        rect_obj = surface_obj.get_rect()
        rect_obj.center = (160, 450)
        displaysurf.blit(surface_obj , rect_obj)

        pygame.display.update() # 화면을 업데이트한다
        display_update = False