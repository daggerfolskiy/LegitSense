import os, sys, time, math, struct, json, random, tempfile, colorsys
from multiprocessing import Lock, Process, Manager, freeze_support
import ctypes
from ctypes import wintypes
import requests, psutil, glfw, imgui, pyautogui, numpy as np
import OpenGL.GL as gl
from PIL import ImageGrab
from scipy.signal import convolve2d
from pypresence import Presence
from imgui.integrations.glfw import GlfwRenderer
import win32api, win32con, win32gui
from win32gui import FindWindow
from fonts import weapon_bytes, verdana_bytes, font_awesome

PROCESS_ALL_ACCESS = 0x1F0FFF
TH32CS_SNAPMODULE = 0x00000008
MAX_MODULE_NAME32 = 255


bone_ids = {
    "head": 6,
    "neck": 5,
    "spine": 4,
    "pelvis": 0,
    "left_shoulder": 13,
    "left_elbow": 14,
    "left_wrist": 15,
    "right_shoulder": 9,
    "right_elbow": 10,
    "right_wrist": 11,
    "left_hip": 25,
    "left_knee": 26,
    "left_ankle": 27,
    "right_hip": 22,
    "right_knee": 23,
    "right_ankle": 24,
}
bone_connections = [
    ("head", "neck"),
    ("neck", "spine"),
    ("spine", "pelvis"),
    ("pelvis", "left_hip"),
    ("left_hip", "left_knee"),
    ("left_knee", "left_ankle"),
    ("pelvis", "right_hip"),
    ("right_hip", "right_knee"),
    ("right_knee", "right_ankle"),
    ("neck", "left_shoulder"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("neck", "right_shoulder"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
]

offsets = requests.get('https://raw.githubusercontent.com/daggerfolskiy/LegitSenseOffsets/refs/heads/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/daggerfolskiy/LegitSenseOffsets/refs/heads/main/output/client_dll.json').json()

#with open('output/offsets.json', 'r') as file:
#    offsets = json.load(file)
#
#with open('output/client_dll.json', 'r') as file:
#    client_dll = json.load(file)

dwEntityList = offsets['client.dll']['dwEntityList']
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
dwLocalPlayerController = offsets['client.dll']['dwLocalPlayerController']
dwViewMatrix = offsets['client.dll']['dwViewMatrix']
dwPlantedC4 = offsets['client.dll']['dwPlantedC4']
dwViewAngles = offsets['client.dll']['dwViewAngles']
dwSensitivity = offsets['client.dll']['dwSensitivity']
dwSensitivity_sensitivity = offsets['client.dll']['dwSensitivity_sensitivity']
m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']
m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']
m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']
m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']
m_iszPlayerName = client_dll['client.dll']['classes']['CBasePlayerController']['fields']['m_iszPlayerName']
m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_pClippingWeapon']
m_bGunGameImmunity = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_bGunGameImmunity']
m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']
m_ArmorValue = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_ArmorValue']
m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
m_vecOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecOrigin']
m_flTimerLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flTimerLength']
m_flDefuseLength = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flDefuseLength']
m_bBeingDefused = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBeingDefused']
m_bSpottedByMask = client_dll['client.dll']['classes']['EntitySpottedState_t']['fields']['m_bSpottedByMask']
m_bSpotted = client_dll['client.dll']['classes']['EntitySpottedState_t']['fields']['m_bSpotted']
m_entitySpottedState = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_entitySpottedState']
m_angEyeAngles = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_angEyeAngles']
m_fFlags = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_fFlags']
m_pCameraServices = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_pCameraServices']
m_iIDEntIndex = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_iIDEntIndex']
m_vecVelocity = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_vecVelocity']
m_aimPunchAngle = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_aimPunchAngle']
m_vOldOrigin = client_dll['client.dll']['classes']['C_BasePlayerPawn']['fields']['m_vOldOrigin']
m_iShotsFired = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_iShotsFired']
m_nBombSite = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_nBombSite']
m_flFlashDuration = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_flFlashDuration']

def make_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass
make_dpi_aware()
WINDOW_WIDTH, WINDOW_HEIGHT = win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

def wait_cs2():
    while True:
        time.sleep(1)
        try:
            idprocess = GetProcessIdByName("cs2.exe")
            client = GetModuleBaseAddress(idprocess, "client.dll")
            return True
        except:
            pass

def descritptor():
    idprocess = GetProcessIdByName("cs2.exe")
    client = GetModuleBaseAddress(idprocess, "client.dll")
    pm = Memory(idprocess)
    return client, pm

def offsets_mem(pm, client):
    view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
    local_player_pawn_addr = pm.read_longlong(client + dwLocalPlayerPawn)
    local_player_team = pm.read_int(local_player_pawn_addr + m_iTeamNum)
    entity_list = pm.read_longlong(client + dwEntityList)
    entity_ptr = pm.read_longlong(entity_list + 0x10)

    return view_matrix, local_player_pawn_addr, local_player_team, entity_list, entity_ptr

    
def client_mem(pm, i, entity_ptr, entity_list, local_player_pawn_addr, local_player_team):
    entity_controller = pm.read_longlong(entity_ptr + 0x70 * (i & 0x1FF))
    if entity_controller == 0:
        return
    entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
    if entity_controller_pawn == 0:
        return
    entity_list_pawn = pm.read_longlong(entity_list + 0x8 * ((entity_controller_pawn & 0x7FFF) >> 0x9) + 0x10)
    if entity_list_pawn == 0:
        return
    entity_pawn_addr = pm.read_longlong(entity_list_pawn + 0x70 * (entity_controller_pawn & 0x1FF))
    if entity_pawn_addr == 0 or entity_pawn_addr == local_player_pawn_addr:
        return
    entity_team = pm.read_int(entity_pawn_addr + m_iTeamNum)
    #if entity_team == local_player_team:
    #    return
    entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
    if entity_hp <= 0:
        return
    entity_alive = pm.read_int(entity_pawn_addr + m_lifeState)
    if entity_alive != 256:
        return
    spotted = pm.read_bool(entity_pawn_addr + m_entitySpottedState + m_bSpottedByMask)
    
    return entity_team, local_player_team, entity_pawn_addr, entity_controller, spotted

def esp_dweapon(pm, i, entity_list, view_matrix, width, height):
    itementitylistentry = pm.read_longlong(entity_list + 8 * ((i & 0x7FFF) >> 9) + 16)
    if not itementitylistentry:
        return
    itementity = pm.read_longlong(itementitylistentry + 112 * (i & 0x1FF))
    if not itementity:
        return
    itementitynode = pm.read_longlong(itementity + m_pGameSceneNode)
    itementityorigin = read_vec3(pm, itementitynode + m_vecOrigin)
    weaponowner = pm.read_longlong(itementity + 0x440)
    if not weaponowner:
        return

    weaponsc = w2s(view_matrix, itementityorigin[0], itementityorigin[1], itementityorigin[2], width, height)
    if not weaponsc:
        return
    iteminfo = pm.read_longlong(itementity + 0x10)
    itemtypeptr = pm.read_longlong(iteminfo + 0x20)
    if itementityorigin[0]:
        type = pm.read_string(itemtypeptr, 128)
        weapons = get_weapon_type(type)
        return weaponsc, weapons

def esp_line(pm, entity_pawn_addr, view_matrix, width, height):
    game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
    data = pm.read_bytes(bone_matrix + 6 * 0x20, 3 * 4)
    headX, headY, headZ = struct.unpack('fff', data)
    headZ += 8
    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
    leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
    bottom_left_x = head_pos[0] - (head_pos[0] - leg_pos[0]) // 2
    bottom_y = leg_pos[1]

    return bottom_left_x, bottom_y, bone_matrix, headX, headY, headZ, head_pos

def esp_aim(pm, entity_pawn_addr, view_matrix, width, height, bone_id=6):
    game_scene = pm.read_longlong(entity_pawn_addr + m_pGameSceneNode)
    bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)
    data = pm.read_bytes(bone_matrix + bone_id * 0x20, 3 * 4)
    headX, headY, headZ = struct.unpack('fff', data)
    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
    leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
    deltaZ = abs(head_pos[1] - leg_pos[1])
    return head_pos, leg_pos, deltaZ

def read_vec2(pm, address):
    data = pm.read_bytes(address, 8)
    vec2 = struct.unpack('2f', data)
    return vec2

def read_vec3(pm, address):
    data = pm.read_bytes(address, 12)
    vec3 = struct.unpack('3f', data)
    return vec3

def esp_head_line(pm, entity_pawn_addr, bone_matrix, view_matrix, lenght, width, height):
    data = pm.read_bytes(bone_matrix + 6 * 0x20, 3 * 4)
    headX, headY, headZ = struct.unpack('fff', data)
    head_pos = w2s(view_matrix, headX, headY, headZ, width, height)
    firstX = head_pos[0]
    firstY = head_pos[1]
    vec2eye = read_vec2(pm, entity_pawn_addr + m_angEyeAngles)
    line_length = math.cos(vec2eye[0] * math.pi / 180) * lenght
    temp_x = headX + math.cos(vec2eye[1] * math.pi / 180) * line_length
    temp_y = headY + math.sin(vec2eye[1] * math.pi / 180) * line_length
    temp_z = headZ - math.sin(vec2eye[0] * math.pi / 180 ) * lenght
    end_point = w2s(view_matrix, temp_x, temp_y, temp_z, width, height)
    return firstX, firstY, end_point 

def esp_box(pm, bone_matrix, view_matrix, headX, headY, head_pos, width, height):
    legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
    leg_pos = w2s(view_matrix, headX, headY, legZ, width, height)
    deltaZ = abs(head_pos[1] - leg_pos[1])
    leftX = head_pos[0] - deltaZ // 4
    rightX = head_pos[0] + deltaZ // 4

    return leftX, leg_pos, rightX, deltaZ

def esp_headbox(pm, bone_matrix, view_matrix, rightX, leftX, window_width, window_height):
    data = pm.read_bytes(bone_matrix + 6 * 0x20, 3 * 4)
    boneX, boneY, boneZ = struct.unpack('fff', data)
    rhead_pos = w2s(view_matrix, boneX, boneY, boneZ, window_width, window_height)
    head_hitbox_size = (rightX - leftX) / 4.5
    head_hitbox_radius = head_hitbox_size * 2 ** 0.5 / 2
    head_hitbox_x = rhead_pos[0] 
    head_hitbox_y = rhead_pos[1]

    return head_hitbox_x, head_hitbox_y, head_hitbox_radius

def esp_bone(pm, bone_matrix, view_matrix, window_width, window_height):
    bone_positions = {}
    for bone_name, bone_id in bone_ids.items():
        data = pm.read_bytes(bone_matrix + bone_id * 0x20, 3 * 4)
        boneX, boneY, boneZ = struct.unpack('fff', data)
        bone_pos = w2s(view_matrix, boneX, boneY, boneZ, window_width, window_height)
        if bone_pos[0] != -999 and bone_pos[1] != -999:
            bone_positions[bone_name] = bone_pos

    return bone_connections, bone_positions

def esp_nickname(pm, entity_controller):
    player_name = pm.read_string(entity_controller + m_iszPlayerName, 32)

    return player_name

def esp_weapon(pm, entity_pawn_addr):
    weapon_pointer = pm.read_longlong(entity_pawn_addr + m_pClippingWeapon)
    weapon_index = pm.read_int(weapon_pointer + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
    weapon_name = get_weapon_name(weapon_index)
    weapon_icon = get_weapon_icon(weapon_name)

    return weapon_icon

def esp_immunity(pm, entity_pawn_addr):
    immunity = pm.read_int(entity_pawn_addr + m_bGunGameImmunity)
    if (immunity == 257 or immunity == 1):
        return True
    return

def esp_hp(pm, entity_pawn_addr, deltaZ, head_pos, leftX):
    entity_hp = pm.read_int(entity_pawn_addr + m_iHealth)
    #print(entity_hp)
    max_hp = 100
    hp_percentage = min(1.0, max(0.0, entity_hp / max_hp))
    hp_bar_width = 2
    hp_bar_height = deltaZ
    hp_bar_x_left = leftX - hp_bar_width
    hp_bar_y_top = head_pos[1]
    current_hp_height = hp_bar_height * hp_percentage
    hp_bar_y_bottom = hp_bar_y_top + hp_bar_height - current_hp_height

    return hp_bar_x_left, hp_bar_y_top, hp_bar_y_bottom, current_hp_height

def esp_br(pm, entity_pawn_addr, deltaZ, head_pos, rightX, leftX, leg_pos):
    armor_hp = pm.read_int(entity_pawn_addr + m_ArmorValue)
    max_armor_hp = 100
    armor_hp_percentage = min(1.0, max(0.0, armor_hp / max_armor_hp))
    armor_bar_height = 2  # Height of the armor bar
    armor_bar_width = rightX - leftX  # Width of the armor bar
    armor_bar_x_left = leftX
    armor_bar_y_top = leg_pos[1] + 2  # 2 pixels below the bottom of the enemy box
    current_armor_width = armor_bar_width * armor_hp_percentage
    armor_bar_x_right = rightX

    return armor_bar_x_left, armor_bar_y_top, armor_bar_x_right, current_armor_width

class csBomb:
    BombPlantedTime = 0
    BombDefusedTime = 0
    
    @staticmethod
    def getC4BaseClass(pm, client):
        PlantedC4Class = pm.read_longlong(client + dwPlantedC4)
        return pm.read_longlong(PlantedC4Class)
    
    @staticmethod
    def getPositionWTS(pm, client, view_matrix, window_width, window_height):
        base_class = csBomb.getC4BaseClass(pm, client)
        if not base_class:
            return None
            
        C4Node = pm.read_longlong(base_class + m_pGameSceneNode)
        if not C4Node:
            return None
            
        c4_pos = (
            pm.read_float(C4Node + m_vecAbsOrigin),
            pm.read_float(C4Node + m_vecAbsOrigin + 0x4),
            pm.read_float(C4Node + m_vecAbsOrigin + 0x8)
        )
        
        return w2s(view_matrix, *c4_pos, window_width, window_height)
    
    @staticmethod
    def getSite(pm, client):
        base_class = csBomb.getC4BaseClass(pm, client)
        if not base_class:
            return None
            
        Site = pm.read_int(base_class + m_nBombSite)
        return "A" if (Site != 1) else "B"
    
    @staticmethod
    def isPlanted(pm, client):
        BombIsPlanted = pm.read_bool(client + dwPlantedC4 - 0x8)

        if BombIsPlanted:
            if csBomb.BombPlantedTime == 0:
                csBomb.BombPlantedTime = time.time()
        else:
            csBomb.BombPlantedTime = 0

        return BombIsPlanted
    
    @staticmethod
    def isBeingDefused(pm, client):
        base_class = csBomb.getC4BaseClass(pm, client)
        if not base_class:
            return False
            
        BombIsDefused = pm.read_bool(base_class + m_bBeingDefused)

        if BombIsDefused:
            if csBomb.BombDefusedTime == 0:
                csBomb.BombDefusedTime = time.time()
        else:
            csBomb.BombDefusedTime = 0

        return BombIsDefused
    
    @staticmethod
    def getDefuseLength(pm, client):
        base_class = csBomb.getC4BaseClass(pm, client)
        if not base_class:
            return 0.0
        return pm.read_float(base_class + m_flDefuseLength)
    
    @staticmethod
    def getTimerLength(pm, client):
        base_class = csBomb.getC4BaseClass(pm, client)
        if not base_class:
            return 0.0
        return pm.read_float(base_class + m_flTimerLength)
    
    @staticmethod
    def getBombTime(pm, client):
        if csBomb.BombPlantedTime == 0:
            return 0.0
            
        timer_length = csBomb.getTimerLength(pm, client)
        bomb_time = timer_length - (time.time() - csBomb.BombPlantedTime)
        return max(0.0, bomb_time)
    
    @staticmethod
    def getDefuseTime(pm, client):
        if not csBomb.isBeingDefused(pm, client) or csBomb.BombDefusedTime == 0:
            return 0.0
            
        defuse_length = csBomb.getDefuseLength(pm, client)
        defuse_time = defuse_length - (time.time() - csBomb.BombDefusedTime)
        return max(0.0, defuse_time)
    
class Config:
    class RCS:
        old_punch_x = 0.0
        old_punch_y = 0.0

def no_recoil(pm, client, local_player_addr):
    aim_punch_x = pm.read_float(local_player_addr + m_aimPunchAngle)
    aim_punch_y = pm.read_float(local_player_addr + m_aimPunchAngle + 0x4)
    shots_fired = pm.read_int(local_player_addr + m_iShotsFired)

    if shots_fired > 1:
        delta_x = (aim_punch_x - Config.RCS.old_punch_x) * -1.0
        delta_y = (aim_punch_y - Config.RCS.old_punch_y) * -1.0
        sens_ptr = pm.read_longlong(client + dwSensitivity)
        sensitivity = pm.read_float(sens_ptr + dwSensitivity_sensitivity)
        mouse_x = int((delta_y * 2.0 / sensitivity) / -0.022)
        mouse_y = int((delta_x * 2.0 / sensitivity) / 0.022)

    Config.RCS.old_punch_x = aim_punch_x
    Config.RCS.old_punch_y = aim_punch_y

    return mouse_x, mouse_y

class ProcessManager:
    def __init__(self):
        self.process_id = None
        self.process_handle = None
        self.client_module = None
        self.server_module = None
        self.hwnd = None

    @staticmethod
    def get_process_id(process_name):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == process_name:
                return proc.info['pid']
        return None

    def connect(self, process_name, window_title):
        self.process_id = self.get_process_id(process_name)
        if not self.process_id:
            return False
            
        self.hwnd = FindWindow("SDL_app", window_title)
        self.process_handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_ALL_ACCESS, 
            False, 
            self.process_id
        )
        self.client_module = self.get_module_address("client.dll")
        self.server_module = self.get_module_address("server.dll")
        
        return self.process_handle is not None

    def get_module_address(self, module_name):
        h_snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot(
            TH32CS_SNAPMODULE, 
            self.process_id
        )
        
        class ModuleEntry32(ctypes.Structure):
            _fields_ = [
                ('dwSize', wintypes.DWORD),
                ('th32ModuleID', wintypes.DWORD),
                ('th32ProcessID', wintypes.DWORD),
                ('GlblcntUsage', wintypes.DWORD),
                ('ProccntUsage', wintypes.DWORD),
                ('modBaseAddr', ctypes.POINTER(wintypes.BYTE)),
                ('modBaseSize', wintypes.DWORD),
                ('hModule', wintypes.HMODULE),
                ('szModule', ctypes.c_char * (MAX_MODULE_NAME32 + 1)),
                ('szExePath', ctypes.c_char * 260)
            ]
            
        entry = ModuleEntry32()
        entry.dwSize = ctypes.sizeof(ModuleEntry32)
        
        if ctypes.windll.kernel32.Module32First(h_snapshot, ctypes.byref(entry)):
            while True:
                if module_name.encode() == entry.szModule:
                    ctypes.windll.kernel32.CloseHandle(h_snapshot)
                    return entry.hModule
                if not ctypes.windll.kernel32.Module32Next(h_snapshot, ctypes.byref(entry)):
                    break
                    
        ctypes.windll.kernel32.CloseHandle(h_snapshot)
        return 0

class MemoryReader:
    def __init__(self, process_handle):
        self.process_handle = process_handle
        
    def read(self, address, c_type):
        buffer = c_type()
        bytes_read = ctypes.c_size_t()
        
        ctypes.windll.kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            ctypes.byref(buffer),
            ctypes.sizeof(buffer),
            ctypes.byref(bytes_read)
        )
        
        return buffer.value if bytes_read.value == ctypes.sizeof(buffer) else None

    def read_bytes(self, address, size):
        buffer = (ctypes.c_byte * size)()
        bytes_read = ctypes.c_size_t()
        
        ctypes.windll.kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(bytes_read)
        )
        
        return bytes(buffer) if bytes_read.value == size else None
    
    def read_int(self, address):
        return self.read(address, ctypes.c_int)
        
    def read_float(self, address):
        return self.read(address, ctypes.c_float)
        
    def read_longlong(self, address):
        return self.read(address, ctypes.c_longlong)
        
    def read_bool(self, address):
        return self.read(address, ctypes.c_bool)
        
    def read_short(self, address):
        return self.read(address, ctypes.c_short)
        
    def read_string(self, address, max_length):
        buffer = ctypes.create_string_buffer(max_length)
        bytes_read = ctypes.c_size_t()
        
        ctypes.windll.kernel32.ReadProcessMemory(
            self.process_handle,
            ctypes.c_void_p(address),
            buffer,
            max_length,
            ctypes.byref(bytes_read)
        )
        
        return buffer.value.decode('utf-8', 'ignore') if bytes_read.value > 0 else ""

manager = ProcessManager()
memory = None

def initialize(process_name, window_title):
    global memory
    if manager.connect(process_name, window_title):
        memory = MemoryReader(manager.process_handle)
    return memory is not None

def GetProcessIdByName(process_name):
    return ProcessManager.get_process_id(process_name)

def GetModuleBaseAddress(pid, module_name):
    temp_manager = ProcessManager()
    temp_manager.process_id = pid
    return temp_manager.get_module_address(module_name)

def Memory(pid):
    handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    return MemoryReader(handle) if handle else None

weapon_font = None
verdana_font = None

def create_window():
    global weapon_font, verdana_font
    font_paths = []
    
    if not glfw.init():
        sys.exit(1)

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    glfw.window_hint(glfw.FLOATING, glfw.TRUE)
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.MAXIMIZED, glfw.TRUE)
    glfw.window_hint(glfw.FOCUS_ON_SHOW, glfw.FALSE)
    
    glfw.window_hint(glfw.MOUSE_PASSTHROUGH, glfw.TRUE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "LegitSense", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    hwnd = glfw.get_win32_window(window)

    class MARGINS(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)]

    margins = MARGINS(-1, -1, -1, -1)
    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, 
                           ex_style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOOLWINDOW)
    
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

    imgui.create_context()
    impl = GlfwRenderer(window)

    io = imgui.get_io()

    try:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as weapon_file:
            weapon_file.write(weapon_bytes)
            weapon_path = weapon_file.name
            font_paths.append(weapon_path)
        weapon_font = io.fonts.add_font_from_file_ttf(weapon_path, 10)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as verdana_file:
            verdana_file.write(verdana_bytes)
            verdana_path = verdana_file.name
            font_paths.append(verdana_path)
            
        ranges = imgui.core.GlyphRanges([
            0x0020, 0x00FF, 0x0400, 0x04FF, 0x0370, 0x03FF,
            0x0600, 0x06FF, 0x0900, 0x097F, 0x4E00, 0x9FFF,
            0x3040, 0x309F, 0x30A0, 0x30FF, 0xAC00, 0xD7AF,
            0xE000, 0xEFFF, 0
        ])
        
        verdana_font = io.fonts.add_font_from_file_ttf(verdana_path, 17, glyph_ranges=ranges)
    except Exception as e:
        print(f"font loading error: {e}")

    impl.refresh_font_texture()
    
    return window, impl, hwnd, font_paths
def render_loop(draw_func):
    window, impl, hwnd, font_paths = create_window()
    frame_times = []

    try:
        while not glfw.window_should_close(window):
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
            )

            start_time = time.time()
            glfw.poll_events()
            impl.process_inputs()
            imgui.new_frame()
            draw_watermark()
            imgui.set_next_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            imgui.set_next_window_position(0, 0)
            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
            imgui.begin(
                "overlay",
                flags=imgui.WINDOW_NO_TITLE_BAR |
                imgui.WINDOW_NO_RESIZE |
                imgui.WINDOW_NO_SCROLLBAR |
                imgui.WINDOW_NO_COLLAPSE |
                imgui.WINDOW_NO_BACKGROUND |
                imgui.WINDOW_NO_MOVE
            )
            imgui.pop_style_var()
            draw_list = imgui.get_window_draw_list()
            
            draw_func(draw_list)
            
            frame_time = time.time() - start_time
            frame_times.append(frame_time)
            if len(frame_times) > 60:
                frame_times.pop(0)
            fps = len(frame_times) / sum(frame_times) if sum(frame_times) != 0 else 0
            #draw_text(draw_list, 3, 3, f"FPS: {int(fps * 2)}", (255, 255, 255, 255))
            
            imgui.end()
            imgui.end_frame()
            gl.glClearColor(0.0, 0.0, 0.0, 0.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)
    finally:
        impl.shutdown()
        glfw.terminate()
        for path in font_paths:
            if os.path.exists(path):
                os.remove(path)

last_fps_update = 0
display_fps = 0
def draw_watermark():
    global last_fps_update, display_fps

    fps = int(imgui.get_io().framerate)
    current_time = time.strftime("%H:%M:%S")
    current_time_now = time.time()
    if current_time_now - last_fps_update > 1.5:
        display_fps = int(imgui.get_io().framerate)
        last_fps_update = current_time_now
    
    text = f"LegitSense | FPS: {display_fps} | {current_time}"
    
    font_scale = 1
    margin = 20.0
    padding_x = 10.0
    padding_y = 5.0
    line_width = 2.0
    
    speed = 0.1 
    t = time.time() * speed
    rgb = colorsys.hsv_to_rgb(t % 1.0, 0.8, 1.0) # Saturation 0.8, Value 1.0 для яркости
    
    # Цвета (ABGR формат для imgui.get_color_u32_rgba обычно требует 0-1 float)
    accent_color = imgui.get_color_u32_rgba(rgb[0], rgb[1], rgb[2], 1.0)
    bg_color = imgui.get_color_u32_rgba(0.06, 0.06, 0.06, 0.90) # Темно-серый фон
    text_color = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0) # Белый текст
    
    draw_list = imgui.get_foreground_draw_list()
    
    old_scale = imgui.get_io().font_global_scale
    imgui.get_io().font_global_scale = font_scale
    
    tw, th = imgui.calc_text_size(text)
    box_w = tw + (padding_x * 2)
    box_h = th + (padding_y * 2)
    
    sw = imgui.get_io().display_size.x
    x1 = sw - box_w - margin
    y1 = margin
    x2 = x1 + box_w
    y2 = y1 + box_h
    
    draw_list.add_rect_filled(x1, y1, x2, y2, bg_color, 0.0)
    
    draw_list.add_rect_filled(x1, y1, x2, y1 + line_width, accent_color, 0.0, imgui.DRAW_CORNER_TOP)

    draw_list.add_text(x1 + padding_x, y1 + padding_y, text_color, text)
    
    imgui.get_io().font_global_scale = old_scale

def draw_circle_outline(draw_list, x, y, radius, color, px_size):
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_circle(x, y, radius, imgui_color, 0, px_size)

def draw_circle(draw_list, x, y, radius, color):
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_circle_filled(x, y, radius, imgui_color)

def draw_line(draw_list, x, y, x1, y1, color, px_size):
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_line(x, y, x1, y1, imgui_color, px_size)

def draw_box(draw_list, x, y, x1, y1, color, px_size):
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_line(x, y, x1, y, imgui_color, px_size)
    draw_list.add_line(x, y, x, y1, imgui_color, px_size)
    draw_list.add_line(x1, y, x1, y1, imgui_color, px_size)
    draw_list.add_line(x, y1, x1, y1, imgui_color, px_size)

def draw_filled_box(draw_list, x, y, x1, y1, color):
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_rect_filled(x, y, x1, y1, imgui_color)

def draw_corners(draw_list, x, y, x1, y1, color, px_size, percentage=0.2):
    imgui_color = imgui.get_color_u32_rgba(*color)
    width = x1 - x
    short_width = width * percentage
    short_height = -(width * percentage)
    draw_list.add_line(x, y, x + short_width, y, imgui_color, px_size)
    draw_list.add_line(x, y, x, y + short_height, imgui_color, px_size)
    draw_list.add_line(x1, y, x1 - short_width, y, imgui_color, px_size)
    draw_list.add_line(x1, y1, x1, y1 - short_height, imgui_color, px_size)
    draw_list.add_line(x, y1, x + short_width, y1, imgui_color, px_size)
    draw_list.add_line(x, y1, x, y1 - short_height, imgui_color, px_size)
    draw_list.add_line(x1, y, x1, y + short_height, imgui_color, px_size)
    draw_list.add_line(x1, y1, x1 - short_width, y1, imgui_color, px_size)

def draw_text(draw_list, x, y, text, color):
    global verdana_font
    if not verdana_font: return
    imgui.push_font(verdana_font)
    shadow_x, shadow_y = x + 1, y + 1
    imgui_shadow_color = imgui.get_color_u32_rgba(*(0, 0, 0, 1))
    draw_list.add_text(shadow_x, shadow_y, imgui_shadow_color, text)
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_text(x, y, imgui_color, text)
    imgui.pop_font()

def draw_nickname(draw_list, text, head_pos, rightX, leftX, color):
    global verdana_font
    if not verdana_font: return
    imgui.push_font(verdana_font)
    text_size = imgui.calc_text_size(text)
    text_width = text_size.x
    text_height = text_size.y
    x = (rightX + leftX - text_width) / 2
    y = head_pos[1] - text_height - 5
    shadow_x, shadow_y = x + 1, y + 1
    imgui_shadow_color = imgui.get_color_u32_rgba(*(0, 0, 0, 1))
    draw_list.add_text(shadow_x, shadow_y, imgui_shadow_color, text)
    imgui_color = imgui.get_color_u32_rgba(*color)
    draw_list.add_text(x, y, imgui_color, text)
    imgui.pop_font()

def draw_weapon(draw_list, weapon_icon, leg_pos, rightX, leftX, color):
    if weapon_icon:
        global weapon_font
        if not weapon_font: return
        imgui.push_font(weapon_font)
        text_size = imgui.calc_text_size(weapon_icon)
        text_width = text_size.x
        text_height = text_size.y / 2.5
        x = (rightX + leftX - text_width) / 2
        y = leg_pos[1] + text_height
        shadow_x, shadow_y = x + 1, y + 1
        imgui_shadow_color = imgui.get_color_u32_rgba(*(0, 0, 0, 1))
        draw_list.add_text(shadow_x, shadow_y, imgui_shadow_color, weapon_icon)
        imgui_color = imgui.get_color_u32_rgba(*color)
        draw_list.add_text(x, y, imgui_color, weapon_icon)
        imgui.pop_font()

def angle_to_direction(pitch: float, yaw: float) -> tuple:
    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)
    cos_pitch = math.cos(pitch_rad)
    return (
        math.cos(yaw_rad) * cos_pitch,
        math.sin(yaw_rad) * cos_pitch,
        -math.sin(pitch_rad)
    )

def point_along_direction(start: tuple, direction: tuple, distance: float) -> tuple:
    return (
        start[0] + direction[0] * distance,
        start[1] + direction[1] * distance,
        start[2] + direction[2] * distance
    )

def w2s(mtx, posx, posy, posz, width, height):
    screenW = (mtx[12] * posx) + (mtx[13] * posy) + (mtx[14] * posz) + mtx[15]
    if screenW > 0.001:
        screenX = (mtx[0] * posx) + (mtx[1] * posy) + (mtx[2] * posz) + mtx[3]
        screenY = (mtx[4] * posx) + (mtx[5] * posy) + (mtx[6] * posz) + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW)
        y = camY - (camY * screenY / screenW)
        return [int(x), int(y)]
    return [-999, -999]

weapons_type = {
    "weapon_ak47": "AK-47",
    "weapon_m4a1": "M4A1",
    "weapon_awp": "AWP",
    "weapon_elite": "Elite",
    "weapon_famas": "Famas",
    "weapon_flashbang": "Flashbang",
    "weapon_g3sg1": "G3SG1",
    "weapon_galilar": "Galil AR",
    "weapon_healthshot": "Health Shot",
    "weapon_hegrenade": "HE Grenade",
    "weapon_incgrenade": "Incendiary Grenade",
    "weapon_m249": "M249",
    "weapon_m4a1_silencer": "M4A1-S",
    "weapon_mac10": "MAC-10",
    "weapon_mag7": "MAG-7",
    "weapon_molotov": "Molotov",
    "weapon_mp5sd": "MP5-SD",
    "weapon_mp7": "MP7",
    "weapon_mp9": "MP9",
    "weapon_negev": "Negev",
    "weapon_nova": "Nova",
    "weapon_p90": "P90",
    "weapon_sawedoff": "Sawed-Off",
    "weapon_scar20": "SCAR-20",
    "weapon_sg556": "SG 553",
    "weapon_smokegrenade": "Smoke Grenade",
    "weapon_ssg08": "SSG 08",
    "weapon_tagrenade": "TA Grenade",
    "weapon_taser": "Taser",
    "weapon_ump45": "UMP-45",
    "weapon_xm1014": "XM1014",
    "weapon_aug": "AUG",
    "weapon_bizon": "PP-Bizon",
    "weapon_decoy": "Decoy Grenade",
    "weapon_fiveseven": "Five-Seven",
    "weapon_hkp2000": "P2000",
    "weapon_usp_silencer": "USP-S",
    "weapon_p250": "P250",
    "weapon_tec9": "Tec-9",
    "weapon_cz75a": "CZ75-Auto",
    "weapon_deagle": "Desert Eagle",
    "weapon_revolver": "R8 Revolver",
    "weapon_glock": "Glock-18"
}

def get_weapon_type(item_identifier):
    return weapons_type.get(item_identifier, "unknown")

def get_weapon_name(weapon_id):
    if weapon_id > 262100:
        weapon_id = weapon_id - 262144
    weapon_name = {
        1: 'deagle', 2: 'elite', 3: 'fiveseven', 4: 'glock', 7: 'ak47', 8: 'aug', 9: 'awp',
        10: 'famas', 11: 'g3sg1', 13: 'galil', 14: 'm249', 16: 'm4a1', 17: 'mac10', 19: 'p90',
        23: 'ump45', 24: 'ump45', 25: 'xm1014', 26: 'bizon', 27: 'mag7', 28: 'negev', 29: 'sawedoff', 30: 'tec9',
        31: 'taser', 32: 'hkp2000', 33: 'mp7', 34: 'mp9', 35: 'nova', 36: 'p250', 38: 'scar20',
        39: 'sg556', 40: 'ssg08', 42: 'knife_ct', 43: 'flashbang', 44: 'hegrenade', 45: 'smokegrenade',
        46: 'molotov', 47: 'decoy', 48: 'incgrenade', 49: 'c4', 57: 'deagle', 59: 'knife_t', 60: 'm4a1_silencer',
        61: 'usp_silencer', 63: 'cz75a', 64: 'revolver', 500: 'bayonet', 505: 'knife_flip',
        506: 'knife_gut', 507: 'knife_karambit', 508: 'knife_m9_bayonet', 509: 'knife_tactical',
        512: 'knife_falchion', 514: 'knife_survival_bowie', 515: 'knife_butterfly', 516: 'knife_push',
        526: 'knife_kukri'
    }
    return weapon_name.get(weapon_id, None)

def get_weapon_icon(weapon_name):
    if weapon_name:
        weapon_icons_dict = {
            'knife_ct': ']', 'knife_t': '[', 'deagle': 'A', 'elite': 'B', 'fiveseven': 'C',
            'glock': 'D', 'revolver': 'J', 'hkp2000': 'E', 'p250': 'F', 'usp_silencer': 'G',
            'tec9': 'H', 'cz75a': 'I', 'mac10': 'K', 'ump45': 'L', 'bizon': 'M', 'mp7': 'N',
            'mp9': 'P', 'p90': 'O', 'galil': 'Q', 'famas': 'R', 'm4a1_silencer': 'T', 'm4a1': 'S',
            'aug': 'U', 'sg556': 'V', 'ak47': 'W', 'g3sg1': 'X', 'scar20': 'Y', 'awp': 'Z',
            'ssg08': 'a', 'xm1014': 'b', 'sawedoff': 'c', 'mag7': 'd', 'nova': 'e', 'negev': 'f',
            'm249': 'g', 'taser': 'h', 'flashbang': 'i', 'hegrenade': 'j', 'smokegrenade': 'k',
            'molotov': 'l', 'decoy': 'm', 'incgrenade': 'n', 'c4': 'o', 'mp5': 'z',
        }
        return weapon_icons_dict.get(weapon_name, None)
    return None

def get_window_handle():
    hwnd = win32gui.FindWindow(None, 'Counter-Strike 2')
    if hwnd:
        return hwnd
    return

def is_cs2_window_active():
    hwnd = get_window_handle()
    foreground_hwnd = win32gui.GetForegroundWindow()
    if hwnd == foreground_hwnd:
        return True
    return

win32_key_map = {
    "NONE": 0,
    "MOUSE1": win32con.VK_LBUTTON,
    "MOUSE2": win32con.VK_RBUTTON,
    "MOUSE3": win32con.VK_MBUTTON,
    "MOUSE4": win32con.VK_XBUTTON1,
    "MOUSE5": win32con.VK_XBUTTON2,
    "LSHIFT": win32con.VK_LSHIFT,
    "RSHIFT": win32con.VK_RSHIFT,
    "INSERT": win32con.VK_INSERT,
    "LCTRL": win32con.VK_LCONTROL,
    "RCTRL": win32con.VK_RCONTROL,
    "LALT": win32con.VK_LMENU,
    "RALT": win32con.VK_RMENU,
    "SPACE": win32con.VK_SPACE,
    "ENTER": win32con.VK_RETURN,
    "ESCAPE": win32con.VK_ESCAPE,
    "TAB": win32con.VK_TAB,
    "UP": win32con.VK_UP,
    "DOWN": win32con.VK_DOWN,
    "LEFT": win32con.VK_LEFT,
    "RIGHT": win32con.VK_RIGHT,
    "F1": win32con.VK_F1, "F2": win32con.VK_F2, "F3": win32con.VK_F3,
    "F4": win32con.VK_F4, "F5": win32con.VK_F5, "F6": win32con.VK_F6,
    "F7": win32con.VK_F7, "F8": win32con.VK_F8, "F9": win32con.VK_F9,
    "F10": win32con.VK_F10, "F11": win32con.VK_F11, "F12": win32con.VK_F12,
    "A": ord('A'), "B": ord('B'), "C": ord('C'), "D": ord('D'), "E": ord('E'),
    "F": ord('F'), "G": ord('G'), "H": ord('H'), "I": ord('I'), "J": ord('J'),
    "K": ord('K'), "L": ord('L'), "M": ord('M'), "N": ord('N'), "O": ord('O'),
    "P": ord('P'), "Q": ord('Q'), "R": ord('R'), "S": ord('S'), "T": ord('T'),
    "U": ord('U'), "V": ord('V'), "W": ord('W'), "X": ord('X'), "Y": ord('Y'),
    "Z": ord('Z'),
    "0": ord('0'), "1": ord('1'), "2": ord('2'), "3": ord('3'), "4": ord('4'),
    "5": ord('5'), "6": ord('6'), "7": ord('7'), "8": ord('8'), "9": ord('9'),
}


color_accent = (0.55, 0.00, 0.55, 1.00)
color_bg_dark = (0.08, 0.08, 0.08, 1.00)
color_item_bg = (0.15, 0.15, 0.15, 1.00)
color_text = (0.90, 0.90, 0.90, 1.00)
color_border = (0.25, 0.25, 0.25, 0.50)

def setup_imgui_style():
    global color_accent, color_bg_dark, color_item_bg, color_text, color_border
    style = imgui.get_style()
    style.window_rounding = 3
    style.frame_rounding = 3
    style.grab_rounding = 3
    style.scrollbar_rounding = 3
    style.window_padding = (8, 8)
    style.frame_padding = (6, 4)
    style.item_spacing = (8, 6)
    style.scrollbar_size = 10

    colors = style.colors
    colors[imgui.COLOR_WINDOW_BACKGROUND] = color_bg_dark
    colors[imgui.COLOR_BORDER] = color_border
    colors[imgui.COLOR_FRAME_BACKGROUND] = color_item_bg
    colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = (0.20, 0.20, 0.20, 1.0)
    colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = (0.25, 0.25, 0.25, 1.0)
    colors[imgui.COLOR_CHECK_MARK] = color_accent
    colors[imgui.COLOR_SLIDER_GRAB] = color_accent
    colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = (0.70, 0.00, 0.55, 1.0)
    colors[imgui.COLOR_HEADER] = color_accent
    colors[imgui.COLOR_HEADER_HOVERED] = (0.65, 0.00, 0.55, 1.0)
    colors[imgui.COLOR_HEADER_ACTIVE] = (0.50, 0.00, 0.55, 1.0)
    colors[imgui.COLOR_SCROLLBAR_BACKGROUND] = (0.10, 0.10, 0.10, 1.0)
    colors[imgui.COLOR_SCROLLBAR_GRAB] = color_item_bg
    colors[imgui.COLOR_TEXT] = color_text
    colors[imgui.COLOR_TEXT_DISABLED] = (0.50, 0.50, 0.50, 1.0)
    colors[imgui.COLOR_BUTTON] = color_accent
    colors[imgui.COLOR_BUTTON_HOVERED] = (0.65, 0.00, 0.55, 1.0)
    colors[imgui.COLOR_BUTTON_ACTIVE] = (0.50, 0.00, 0.55, 1.0)

def custom_tab_bar(tabs, current_tab, width, icon_font, main_font, tab_animations):
    global color_accent
    imgui.begin_child("##tabbar", width, 0, border=False)

    for i, tab in enumerate(tabs):
        button_height = 90
        pos = imgui.get_cursor_pos()
        is_selected = (current_tab == i)
        anim = tab_animations[i]

        if imgui.invisible_button(f"##tab_{i}", width, button_height):
            current_tab = i

        draw_list = imgui.get_window_draw_list()
        if anim > 0.001:
            col = list(color_accent)
            col[3] *= anim
            draw_list.add_rect_filled(
                *imgui.get_item_rect_min(), *imgui.get_item_rect_max(),
                imgui.get_color_u32_rgba(*col)
            )
        if imgui.is_item_hovered() and not is_selected:
            draw_list.add_rect_filled(
                *imgui.get_item_rect_min(), *imgui.get_item_rect_max(),
                imgui.get_color_u32_rgba(0.2, 0.2, 0.2, 0.3)
            )
        imgui.push_font(icon_font)
        icon_size = imgui.calc_text_size(tab["icon"])
        imgui.set_cursor_pos((
            pos[0] + (width - icon_size.x) * 0.5,
            pos[1] + 20
        ))
        imgui.text(tab["icon"])
        imgui.pop_font()
        
        imgui.push_font(main_font)
        text_width = imgui.calc_text_size(tab["name"]).x
        imgui.set_cursor_pos((
            pos[0] + (width - text_width) * 0.5,
            pos[1] + button_height - imgui.get_text_line_height() - 20
        ))
        imgui.text(tab["name"])
        imgui.pop_font()

        imgui.set_cursor_pos((pos[0], pos[1] + button_height))

    imgui.end_child()
    return current_tab

def section_header(label, font):
    global color_accent
    imgui.push_font(font)
    imgui.push_style_color(imgui.COLOR_TEXT, *color_accent)
    imgui.text(label.upper())
    imgui.pop_style_color()
    imgui.separator()
    imgui.pop_font()

def custom_checkbox(label, state, font):
    imgui.push_font(font)
    imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 3)
    changed, state = imgui.checkbox(f"##{label}", state)
    imgui.same_line()
    imgui.text(label)
    imgui.pop_style_var()
    imgui.pop_font()
    return changed, state

def custom_slider_float(label, value, v_min, v_max, format="%.2f", font=None):
    global color_accent, color_item_bg
    if font: imgui.push_font(font)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, *color_item_bg)
    imgui.push_style_color(imgui.COLOR_SLIDER_GRAB, *color_accent)
    changed, value = imgui.slider_float(f"##{label}", value, v_min, v_max, format=format)
    imgui.pop_style_color(2)
    imgui.same_line()
    imgui.text(label)
    if font: imgui.pop_font()
    return changed, value

def custom_combo(label, current_item, items, font):
    global color_accent, color_item_bg
    imgui.push_font(font)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, *color_item_bg)
    imgui.push_style_color(imgui.COLOR_HEADER, *color_accent)
    imgui.push_style_color(imgui.COLOR_BUTTON, *color_item_bg)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, *color_item_bg)
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, *color_item_bg)
    
    new_item = None
    if imgui.begin_combo(f"##{label}", items[current_item] if items and 0 <= current_item < len(items) else ""):
        for i, item in enumerate(items):
            is_selected = (i == current_item)
            if imgui.selectable(item, is_selected)[0]:
                new_item = i
            if is_selected:
                imgui.set_item_default_focus()
        imgui.end_combo()
    
    imgui.same_line()
    imgui.text(label)
    imgui.pop_style_color(5)
    imgui.pop_font()
    return new_item

def color_cube(label, color, font):
    global color_item_bg
    imgui.push_font(font)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, *color_item_bg)
    flags = (
        imgui.COLOR_EDIT_ALPHA_BAR | 
        imgui.COLOR_EDIT_ALPHA_PREVIEW |
        imgui.COLOR_EDIT_NO_INPUTS
    )
    changed, new_color = imgui.color_edit4(f"##{label}", *color, flags=flags)
    
    imgui.same_line()
    imgui.text(label)
    imgui.pop_style_color()
    imgui.pop_font()
    return changed, new_color

def draw_esp_preview(settings, font):
    draw_list = imgui.get_window_draw_list()
    pos = imgui.get_cursor_screen_pos()
    size = imgui.get_content_region_available()
    
    center_x = pos.x + size.x * 0.5
    center_y = pos.y + size.y * 0.5
    
    box_w = size.x * 0.6
    box_h = box_w * 2.0
    
    x1, y1 = center_x - box_w / 2, center_y - box_h / 2
    x2, y2 = center_x + box_w / 2, center_y + box_h / 2
    
    head = (center_x, y1 + box_h * 0.1)
    neck = (center_x, y1 + box_h * 0.2)
    l_shoulder = (center_x - box_w * 0.3, y1 + box_h * 0.25)
    r_shoulder = (center_x + box_w * 0.3, y1 + box_h * 0.25)
    l_elbow = (center_x - box_w * 0.4, y1 + box_h * 0.4)
    r_elbow = (center_x + box_w * 0.4, y1 + box_h * 0.4)
    spine = (center_x, y1 + box_h * 0.45)
    l_hip = (center_x - box_w * 0.2, y1 + box_h * 0.5)
    r_hip = (center_x + box_w * 0.2, y1 + box_h * 0.5)
    l_knee = (center_x - box_w * 0.22, y1 + box_h * 0.75)
    r_knee = (center_x + box_w * 0.22, y1 + box_h * 0.75)
    l_foot = (center_x - box_w * 0.2, y2)
    r_foot = (center_x + box_w * 0.2, y2)
    connections = [
    (neck, l_shoulder), (neck, r_shoulder), (l_shoulder, l_elbow), (r_shoulder, r_elbow),
    (neck, spine), (spine, l_hip), (spine, r_hip), (l_hip, l_knee), (r_hip, r_knee),
    (l_knee, l_foot), (r_knee, r_foot)
    ]

    if settings.get("esp_filled_box"):
        draw_list.add_rect_filled(x1, y1, x2, y2, imgui.get_color_u32_rgba(*settings.get("esp_box_fill_spotted_color")))
        
    if settings.get("esp_box"):
        draw_list.add_rect(x1, y1, x2, y2, imgui.get_color_u32_rgba(*settings.get("esp_box_border_color")), thickness=1.0)
        
    if settings.get("esp_skeleton"):
        col = imgui.get_color_u32_rgba(*settings.get("esp_skeleton_color"))
        for p1, p2 in connections:
            draw_list.add_line(p1[0], p1[1], p2[0], p2[1], col, 1.0)

    if settings.get("esp_corners"):
        corner_len = box_w * 0.3
        col = imgui.get_color_u32_rgba(*settings.get("esp_enemy_color"))
        draw_list.add_line(x1, y1, x1 + corner_len, y1, col, 1.0); draw_list.add_line(x1, y1, x1, y1 + corner_len, col, 1.0)
        draw_list.add_line(x2, y1, x2 - corner_len, y1, col, 1.0); draw_list.add_line(x2, y1, x2, y1 + corner_len, col, 1.0)
        draw_list.add_line(x1, y2, x1 + corner_len, y2, col, 1.0); draw_list.add_line(x1, y2, x1, y2 - corner_len, col, 1.0)
        draw_list.add_line(x2, y2, x2 - corner_len, y2, col, 1.0); draw_list.add_line(x2, y2, x2, y2 - corner_len, col, 1.0)
        
    if settings.get("esp_health_bar"):
        hb_x = x1 - 6
        draw_list.add_line(hb_x, y1, hb_x, y2, imgui.get_color_u32_rgba(*settings.get("esp_health_bar_bg_color")), 2.0)
        draw_list.add_line(hb_x, y1, hb_x, y2, imgui.get_color_u32_rgba(*settings.get("esp_health_bar_color")), 2.0)
        
    if settings.get("esp_armor_bar"):
        ab_y = y2 + 4
        draw_list.add_line(x1, ab_y, x2, ab_y, imgui.get_color_u32_rgba(*settings.get("esp_health_bar_bg_color")), 2.0)
        draw_list.add_line(x1, ab_y, x2, ab_y, imgui.get_color_u32_rgba(*settings.get("esp_armor_bar_color")), 2.0)
        
    if settings.get("esp_head_dot"):
        draw_list.add_circle_filled(head[0], head[1], 15, imgui.get_color_u32_rgba(*settings.get("esp_head_dot_color")))
    
    imgui.push_font(font)
    if settings.get("esp_names"):
        name_text = "Player"
        name_w, _ = imgui.calc_text_size(name_text)
        draw_list.add_text(center_x - name_w / 2, y1 - 20, imgui.get_color_u32_rgba(*settings.get("esp_name_color")), name_text)
        
    if settings.get("esp_weapons"):
        wep_text = "Weapon"
        wep_w, _ = imgui.calc_text_size(wep_text)
        draw_list.add_text(center_x - wep_w / 2, y2 + 8, imgui.get_color_u32_rgba(*settings.get("esp_weapon_color")), wep_text)
    imgui.pop_font()

def custom_button(label, font):
    imgui.push_font(font)
    clicked = imgui.button(label)
    imgui.pop_font()
    return clicked

def custom_text_input(label, value, buffer_length, font):
    imgui.push_font(font)
    imgui.text(label)
    imgui.same_line()
    changed, new_value = imgui.input_text(f"##{label}", value, buffer_length)
    imgui.pop_font()
    return changed, new_value

key_map = {
    "NONE": 0, "MOUSE1": glfw.MOUSE_BUTTON_1, "MOUSE2": glfw.MOUSE_BUTTON_2, "MOUSE3": glfw.MOUSE_BUTTON_3,
    "MOUSE4": glfw.MOUSE_BUTTON_4, "MOUSE5": glfw.MOUSE_BUTTON_5, "MOUSEWHEEL_UP": -1, "MOUSEWHEEL_DOWN": -2,
    "LSHIFT": glfw.KEY_LEFT_SHIFT, "RSHIFT": glfw.KEY_RIGHT_SHIFT, "LCTRL": glfw.KEY_LEFT_CONTROL,
    "RCTRL": glfw.KEY_RIGHT_CONTROL, "LALT": glfw.KEY_LEFT_ALT, "RALT": glfw.KEY_RIGHT_ALT,
    "SPACE": glfw.KEY_SPACE, "ENTER": glfw.KEY_ENTER, "ESCAPE": glfw.KEY_ESCAPE, "TAB": glfw.KEY_TAB,
    "UP": glfw.KEY_UP, "DOWN": glfw.KEY_DOWN, "LEFT": glfw.KEY_LEFT, "RIGHT": glfw.KEY_RIGHT,
    "F1": glfw.KEY_F1, "F2": glfw.KEY_F2, "F3": glfw.KEY_F3, "F4": glfw.KEY_F4, "F5": glfw.KEY_F5,
    "F6": glfw.KEY_F6, "F7": glfw.KEY_F7, "F8": glfw.KEY_F8, "F9": glfw.KEY_F9, "F10": glfw.KEY_F10,
    "F11": glfw.KEY_F11, "F12": glfw.KEY_F12, "A": glfw.KEY_A, "B": glfw.KEY_B, "C": glfw.KEY_C,
    "D": glfw.KEY_D, "E": glfw.KEY_E, "F": glfw.KEY_F, "G": glfw.KEY_G, "H": glfw.KEY_H, "I": glfw.KEY_I,
    "J": glfw.KEY_J, "K": glfw.KEY_K, "L": glfw.KEY_L, "M": glfw.KEY_M, "N": glfw.KEY_N, "O": glfw.KEY_O,
    "P": glfw.KEY_P, "Q": glfw.KEY_Q, "R": glfw.KEY_R, "S": glfw.KEY_S, "T": glfw.KEY_T, "U": glfw.KEY_U,
    "V": glfw.KEY_V, "W": glfw.KEY_W, "X": glfw.KEY_X, "Y": glfw.KEY_Y, "Z": glfw.KEY_Z, "0": glfw.KEY_0,
    "1": glfw.KEY_1, "2": glfw.KEY_2, "3": glfw.KEY_3, "4": glfw.KEY_4, "5": glfw.KEY_5, "6": glfw.KEY_6,
    "7": glfw.KEY_7, "8": glfw.KEY_8, "9": glfw.KEY_9,
}

code_to_name = {v: k for k, v in key_map.items()}

def key_bind(label, current_key, font):
    global color_accent
    imgui.push_font(font)
    
    popup_id = f"Set Key##{label}"
    is_binding = imgui.is_popup_open(popup_id)
    new_key_value = None
    
    imgui.push_style_color(imgui.COLOR_BUTTON, *color_accent)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, *(0.65, 0.00, 0.55, 1.0))
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, *(0.50, 0.00, 0.55, 1.0))
    
    btn_text = "..." if is_binding else (current_key if current_key != "NONE" else "bind")
    
    if imgui.button(f"{btn_text}##{label}"):
        imgui.open_popup(popup_id)

    if imgui.is_item_hovered() and not is_binding:
        imgui.set_tooltip("Click to bind\nRight-click to clear")
        if imgui.is_mouse_clicked(1):
            new_key_value = "NONE"

    if imgui.begin_popup(popup_id):
        imgui.text("Press any key...")
        imgui.separator()
        imgui.text("[DEL] or [Right-Click] to clear")
        
        io = imgui.get_io()
        
        if imgui.is_key_pressed(glfw.KEY_DELETE):
            new_key_value = "NONE"
            imgui.close_current_popup()
        
        if io.mouse_wheel < 0:
            new_key_value = "MOUSEWHEEL_DOWN"
            imgui.close_current_popup()
        elif io.mouse_wheel > 0:
            new_key_value = "MOUSEWHEEL_UP"
            imgui.close_current_popup()
        
        for i in range(5):
            if imgui.is_mouse_clicked(i):
                new_key_value = f"MOUSE{i+1}"
                imgui.close_current_popup()
                break
        
        if new_key_value is None:
            for code, name in code_to_name.items():
                if code > 0 and imgui.is_key_pressed(code):
                    new_key_value = name
                    imgui.close_current_popup()
                    break
        
        imgui.end_popup()
    
    imgui.same_line()
    imgui.text(label)
    imgui.pop_style_color(3)
    imgui.pop_font()
    
    return new_key_value


class Aimbot:
    def __init__(self, settings):
        self.settings = settings
        self.locked_target = None
        self.was_key_pressed = False
        self.stop_radius = 1.5
        self.client, self.pm = descritptor()

    def _espim(self):
        target_list = []
        try:
            view_matrix, local_player_pawn_addr, local_player_team, entity_list, entity_ptr = offsets_mem(self.pm, self.client)
            if local_player_team == 0 or entity_ptr == 0:
                return target_list
        except Exception:
            return target_list

        aim_attack_all = self.settings.get('aim_attack_all', False)
        aim_bone_selection = self.settings.get('aim_bone', 0)
        # Map combo box index to bone ID: 0=Head(6), 1=Body(4)
        bone_id = 6 if aim_bone_selection == 0 else 4

        for i in range(1, 65):
            try:
                client_m = client_mem(self.pm, i, entity_ptr, entity_list, local_player_pawn_addr, local_player_team)
                if client_m:
                    entity_team, _, entity_pawn_addr, _, _ = client_m
                    if entity_team != local_player_team or aim_attack_all:
                        immunity = esp_immunity(self.pm, entity_pawn_addr)
                        if immunity in (257, 1) and entity_team == local_player_team:
                            continue

                        head_pos, leg_pos, deltaZ = esp_aim(self.pm, entity_pawn_addr, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT, bone_id)
                        if head_pos[0] != -999 and head_pos[1] != -999 and head_pos[1] > 0:
                            target_list.append({
                                'pos': head_pos, 'pawn_addr': entity_pawn_addr, 'deltaZ': deltaZ
                            })
            except Exception:
                continue
        return target_list

    def _find_best_target(self, target_list, aim_fov):
        center_x, center_y = WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2
        best_target = None
        max_deltaZ = -float('inf')
        fov_pixel_radius = (min(WINDOW_WIDTH, WINDOW_HEIGHT) / 2.0) * (aim_fov / 100.0)

        for target in target_list:
            dist_2d_from_crosshair = math.hypot(target['pos'][0] - center_x, target['pos'][1] - center_y)
            if dist_2d_from_crosshair < fov_pixel_radius:
                if target['deltaZ'] > max_deltaZ:
                    max_deltaZ = target['deltaZ']
                    best_target = target
        return best_target

    def run(self):
        while True:
            try:
                s_cache = {
                    'aimbot_enable': self.settings.get('aimbot_enable'), 'aimbot_key': self.settings.get('aimbot_key'),
                    'aim_attack_all': self.settings.get('aim_attack_all'),
                    'aimbot_fov': self.settings.get('aimbot_fov'), 'aimbot_speed': self.settings.get('aimbot_speed'),
                    'aimbot_ease_out': self.settings.get('aimbot_ease_out'),
                    'aimbot_overshoot_chance': self.settings.get('aimbot_overshoot_chance'),
                    'aimbot_overshoot_strength': self.settings.get('aimbot_overshoot_strength'),
                    'aimbot_smooth': self.settings.get('aimbot_smooth'),
                    'aimbot_smooth_intensity': self.settings.get('aimbot_smooth_intensity'),
                }

                if not is_cs2_window_active() or not s_cache['aimbot_enable']:
                    time.sleep(0.1)
                    continue

                key_code = win32_key_map.get(s_cache['aimbot_key'], 0)
                is_key_pressed = win32api.GetAsyncKeyState(key_code) & 0x8000 if key_code > 0 else False
                
                if not is_key_pressed:
                    if self.was_key_pressed:
                        self.locked_target = None
                        self.was_key_pressed = False
                    time.sleep(0.01)
                    continue
                
                self.was_key_pressed = True

                all_targets = self._espim()
                
                if not all_targets:
                    if self.locked_target: self.locked_target = None
                    time.sleep(0.01)
                    continue
                
                if self.locked_target:
                    target_still_valid = any(t['pawn_addr'] == self.locked_target['pawn_addr'] for t in all_targets)
                    if not target_still_valid:
                        self.locked_target = None

                if not self.locked_target:
                    self.locked_target = self._find_best_target(all_targets, s_cache['aimbot_fov'])
                    if not self.locked_target:
                        time.sleep(0.01)
                        continue

                current_target_data = next((t for t in all_targets if t['pawn_addr'] == self.locked_target['pawn_addr']), None)
                if current_target_data:
                    current_x, current_y = win32api.GetCursorPos()
                    target_x, target_y = int(current_target_data['pos'][0]), int(current_target_data['pos'][1])
                    
                    dx = target_x - current_x
                    dy = target_y - current_y
                    distance = math.hypot(dx, dy)

                    if distance <= self.stop_radius:
                        time.sleep(0.001)
                        continue

                    speed_factor = s_cache['aimbot_speed'] * (distance ** s_cache['aimbot_ease_out'])
                    speed_factor = min(distance, speed_factor)
                    move_x = (dx / distance) * speed_factor if distance > 1 else dx
                    move_y = (dy / distance) * speed_factor if distance > 1 else dy

                    # Apply smooth human-like deviations
                    if s_cache['aimbot_smooth'] > 0:
                        smooth_strength = s_cache['aimbot_smooth'] * s_cache['aimbot_smooth_intensity']
                        # Add circular/human-like movement pattern
                        time_factor = time.time() * 2.0  # Frequency of deviation
                        deviation_x = math.sin(time_factor) * smooth_strength * (distance / 100.0)
                        deviation_y = math.cos(time_factor * 0.7) * smooth_strength * (distance / 100.0)
                        
                        # Add some random micro-movements
                        deviation_x += random.uniform(-smooth_strength * 0.3, smooth_strength * 0.3)
                        deviation_y += random.uniform(-smooth_strength * 0.3, smooth_strength * 0.3)
                        
                        # Reduce deviation as we get closer to target
                        distance_factor = min(1.0, distance / 200.0)
                        move_x += deviation_x * distance_factor
                        move_y += deviation_y * distance_factor

                    if random.random() < s_cache['aimbot_overshoot_chance']:
                        strength = s_cache['aimbot_overshoot_strength']
                        overshoot_x = (dx / distance) * strength * random.uniform(0.4, 1.0)
                        overshoot_y = (dy / distance) * strength * random.uniform(0.4, 1.0)
                        overshoot_x += (-dy / distance) * strength * random.uniform(-0.5, 0.5)
                        overshoot_y += (dx / distance) * strength * random.uniform(-0.5, 0.5)
                        move_x += overshoot_x
                        move_y += overshoot_y

                    final_move_x, final_move_y = int(round(move_x)), int(round(move_y))
                    if final_move_x != 0 or final_move_y != 0:
                        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, final_move_x, final_move_y, 0, 0)
                
                time.sleep(0.001)
            except Exception as e:
                time.sleep(1)

def aimbot(s):
    aimbot_instance = Aimbot(s)
    aimbot_instance.run()

def find_button():
    screenshot = ImageGrab.grab()
    img = np.array(screenshot)
    color_match = np.all(img == (54, 183, 82), axis=-1).astype(int)
    kernel = np.ones((10, 10))
    convolution = convolve2d(color_match, kernel, mode='valid')
    y_coords, x_coords = np.where(convolution == 10**2)
    if len(y_coords) > 0:
        x = x_coords[0] + 10 // 2
        y = y_coords[0] + 10 // 2
        return (x, y)
    return None

def auto_accept(settings):
    while True:
        if not settings.get("autoaccept_enable", True):
            time.sleep(1)
            continue
            
        button_pos = find_button()
        if button_pos:
            x, y = button_pos
            pyautogui.moveTo(x, y)
            pyautogui.click()
            
            screen_width, screen_height = pyautogui.size()
            pyautogui.moveTo(screen_width / 2, screen_height / 2)
            
            time.sleep(3)
        else:
            time.sleep(0.5)

client, pm = descritptor()

def forcejump():
    hwnd = win32gui.FindWindow(None, 'Counter-Strike 2')
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_SPACE, 0)
    time.sleep(0.05)
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, win32con.VK_SPACE, 0)

def bunnyhop(settings):
    while True:
        try:
            s_cache = {
                'bunnyhop_enable': settings.get('bunnyhop_enable'),
                'bunnyhop_key': settings.get('bunnyhop_key')
            }
            if not s_cache['bunnyhop_enable'] or not is_cs2_window_active():
                time.sleep(0.1)
                continue
                
            key_code = win32_key_map.get(s_cache['bunnyhop_key'], 0)
            if win32api.GetAsyncKeyState(key_code) & 0x8000:
                view_matrix, local_player_pawn_addr, local_player_team, entity_list, entity_ptr = offsets_mem(pm, client)
                PlayerMoveFlag = pm.read_int(local_player_pawn_addr + m_fFlags)
                if (PlayerMoveFlag == 65665 or PlayerMoveFlag == 65667):
                    forcejump()
        except:
            time.sleep(0.03)
        time.sleep(0.001)


icons = {
    "ESP": "\uF06E", "AIMBOT": "\uF05B", "TRIGGER": "\uF0E7",
    "VISUALS": "\uF042", "MISC": "\uF013", "CONFIGS": "\uF07C"
}

config_tabs = [
    {
        "name": "ESP", "icon": icons["ESP"],
        "elements": [
            {"type": "checkbox", "label": "Enable ESP", "name": "esp_enable", "default": True},
            {"type": "checkbox", "label": "ESP Box", "name": "esp_box", "default": True},
            {"type": "checkbox", "label": "Filled Box", "name": "esp_filled_box", "default": True, "dependencies": [("esp_box", True)]},
            {"type": "checkbox", "label": "Corners", "name": "esp_corners", "default": True},
            {"type": "checkbox", "label": "Skeleton", "name": "esp_skeleton", "default": True},
            {"type": "checkbox", "label": "Names", "name": "esp_names", "default": True},
            {"type": "checkbox", "label": "Weapons", "name": "esp_weapons", "default": True},
            {"type": "checkbox", "label": "Health Bar", "name": "esp_health_bar", "default": True},
            {"type": "checkbox", "label": "Armor Bar", "name": "esp_armor_bar", "default": True},
            {"type": "checkbox", "label": "Head Dot", "name": "esp_head_dot", "default": True},
            {"type": "checkbox", "label": "Snap Lines", "name": "esp_snap_lines", "default": False},
            {"type": "checkbox", "label": "Eye Lines", "name": "esp_eye_lines", "default": True},
            {"type": "checkbox", "label": "Bomb Info", "name": "esp_bomb", "default": True},
            {"type": "checkbox", "label": "Dropped Weapons", "name": "esp_dropped_weapons", "default": False},
        ]
    },
    {
        "name": "VISUALS", "icon": icons["VISUALS"],
        "elements": [
            {"type": "color", "label": "Ally Color", "name": "esp_ally_color"},
            {"type": "color", "label": "Enemy Color", "name": "esp_enemy_color"},
            {"type": "color", "label": "Ally Snapline", "name": "esp_ally_snapline_color"},
            {"type": "color", "label": "Enemy Snapline", "name": "esp_enemy_snapline_color"},
            {"type": "color", "label": "Box Border", "name": "esp_box_border_color"},
            {"type": "color", "label": "Fill Normal", "name": "esp_box_fill_normal_color"},
            {"type": "color", "label": "Fill Spotted", "name": "esp_box_fill_spotted_color"},
            {"type": "color", "label": "Fill Immune", "name": "esp_box_fill_immune_color"},
            {"type": "color", "label": "Health Bar", "name": "esp_health_bar_color"},
            {"type": "color", "label": "Health Bar BG", "name": "esp_health_bar_bg_color"},
            {"type": "color", "label": "Armor Bar", "name": "esp_armor_bar_color"},
            {"type": "color", "label": "Head Dot", "name": "esp_head_dot_color"},
            {"type": "color", "label": "Skeleton", "name": "esp_skeleton_color"},
            {"type": "color", "label": "Name", "name": "esp_name_color"},
            {"type": "color", "label": "Weapon", "name": "esp_weapon_color"},
            {"type": "color", "label": "Eye Line", "name": "esp_eye_line_color"},
            {"type": "color", "label": "Bomb Timer", "name": "esp_bomb_color"},
            {"type": "color", "label": "Bomb Defusing", "name": "esp_bomb_defusing_color"},
            {"type": "color", "label": "Dropped Weapon", "name": "esp_dropped_weapon_color"},
            {"type": "color", "label": "FOV Circle", "name": "esp_fov_color"},
            {"type": "color", "label": "Crosshair", "name": "esp_crosshair_color"},
        ]
    },
    {
        "name": "AIMBOT", "icon": icons["AIMBOT"],
        "elements": [
            {"type": "checkbox", "label": "Enable Aimbot", "name": "aimbot_enable", "default": False},
            {"type": "bind", "label": "Aimbot Key", "name": "aimbot_key"},
            {"type": "combo", "label": "Aim Bone", "name": "aim_bone", "items": ["Head", "Body"], "default": 0},
            {"type": "checkbox", "label": "Attack All", "name": "aim_attack_all", "default": False},
            {"type": "checkbox", "label": "Draw FOV", "name": "draw_fov", "default": True},
            {"type": "slider", "label": "FOV", "name": "aimbot_fov", "min": 1.0, "max": 100.0, "default": 40.0, "format": "%.1f"},
            {"type": "slider", "label": "Speed", "name": "aimbot_speed", "min": 0.1, "max": 10.0, "default": 1.6, "format": "%.2f"},
            {"type": "slider", "label": "Smooth", "name": "aimbot_smooth", "min": 0.0, "max": 5.0, "default": 1.0, "format": "%.1f"},
            {"type": "slider", "label": "Smooth Intensity", "name": "aimbot_smooth_intensity", "min": 0.1, "max": 2.0, "default": 1.0, "format": "%.2f"},
            {"type": "slider", "label": "Ease Out Power", "name": "aimbot_ease_out", "min": 0.1, "max": 1.0, "default": 0.85, "format": "%.2f"},
            {"type": "slider", "label": "Overshoot Chance", "name": "aimbot_overshoot_chance", "min": 0.0, "max": 1.0, "default": 0.3, "format": "%.2f"},
            {"type": "slider", "label": "Overshoot Strength", "name": "aimbot_overshoot_strength", "min": 0.0, "max": 10.0, "default": 3.5, "format": "%.1f"},
        ]
    },
    {
        "name": "TRIGGER", "icon": icons["TRIGGER"],
        "elements": [
            {"type": "checkbox", "label": "Enable Trigger", "name": "trigger_enable", "default": False},
            {"type": "bind", "label": "Trigger Key", "name": "trigger_key"},
            {"type": "checkbox", "label": "Attack All", "name": "trigger_attack_all", "default": False},
            {"type": "checkbox", "label": "Flash Check", "name": "trigger_flash_check", "default": True},
            {"type": "slider", "label": "Delay", "name": "trigger_delay", "min": 0.0, "max": 0.5, "format": "%.3f s"},
        ]
    },
    {
        "name": "MISC", "icon": icons["MISC"],
        "elements": [
            {"type": "bind", "label": "Menu Key", "name": "menu_key"},
            {"type": "checkbox", "label": "Discord Rich Presence", "name": "DiscordRPC" },
            {"type": "checkbox", "label": "Bunny Hop", "name": "bunnyhop_enable", "default": True},
            {"type": "bind", "label": "BHop Key", "name": "bunnyhop_key"},
            {"type": "checkbox", "label": "Draw Crosshair", "name": "draw_crosshair", "default": True},
            {"type": "checkbox", "label": "Auto Accept Match", "name": "autoaccept_enable", "default": True},
            {"type": "checkbox", "label": "No Recoil", "name": "norecoil_enable", "default": False},
            {"type": "slider", "label": "Recoil X", "name": "norecoil_x", "min": 0.0, "max": 2.0, "default": 1.0, "format": "%.2f"},
            {"type": "slider", "label": "Recoil Y", "name": "norecoil_y", "min": 0.0, "max": 2.0, "default": 1.0, "format": "%.2f"},
        ]
    },
    {
        "name": "CONFIGS", "icon": icons["CONFIGS"],
        "elements": [
            {"type": "text_input", "label": "Config Name", "name": "config_filename"},
            {"type": "button", "label": "Save Config", "name": "config_save"},
            {"type": "combo", "label": "Load Config", "name": "config_profile", "items": ["Loading..."]},
            {"type": "button", "label": "Load Selected", "name": "config_load"},
            {"type": "button", "label": "Refresh List", "name": "config_refresh"},
        ]
    }
]

class Settings:
    def __init__(self, manager):
        self._lock = Lock()
        self.config_dir = "configs"
        self._data = manager.dict({
            "menu_key": 0xA1,
            "esp_enable": True, "esp_box": True, "esp_filled_box": True, "esp_corners": True,
            "esp_skeleton": True, "esp_names": True, "esp_weapons": True, "esp_health_bar": True,
            "esp_armor_bar": True, "esp_head_dot": True, "esp_snap_lines": False, "esp_eye_lines": True,
            "esp_bomb": True, "esp_dropped_weapons": False,
            "esp_ally_color": (0.0, 1.0, 0.0, 0.8), "esp_enemy_color": (1.0, 0.0, 0.0, 0.8),
            "esp_ally_snapline_color": (0.0, 1.0, 0.0, 0.5), "esp_enemy_snapline_color": (1.0, 0.0, 0.0, 0.5),
            "esp_box_border_color": (0.1, 0.1, 0.1, 0.8),
            "esp_box_fill_normal_color": (0.23, 0.2, 0.19, 0.4), "esp_box_fill_spotted_color": (0.23, 0.3, 0.19, 0.4),
            "esp_box_fill_immune_color": (0.83, 0.3, 0.19, 0.4),
            "esp_health_bar_color": (1.0, 0.0, 0.0, 0.9), "esp_health_bar_bg_color": (0.0, 0.0, 0.0, 0.7),
            "esp_armor_bar_color": (0.05, 0.27, 0.56, 0.9), "esp_head_dot_color": (1.0, 0.0, 0.0, 0.7),
            "esp_skeleton_color": (1.0, 1.0, 1.0, 1.0), "esp_name_color": (1.0, 1.0, 1.0, 1.0),
            "esp_weapon_color": (1.0, 1.0, 1.0, 1.0), "esp_eye_line_color": (1.0, 1.0, 1.0, 0.7),
            "esp_bomb_color": (1.0, 0.0, 0.0, 1.0), "esp_bomb_defusing_color": (0.0, 1.0, 0.0, 1.0),
            "esp_dropped_weapon_color": (1.0, 1.0, 1.0, 1.0), "esp_fov_color": (1.0, 1.0, 1.0, 0.7),
            "esp_crosshair_color": (0.0, 1.0, 0.0, 1.0),
            "aimbot_enable": False, "aimbot_key": "MOUSE5", "aim_bone": 4, "aim_attack_all": False, "draw_fov": True,
            "aimbot_fov": 40.0, "aimbot_speed": 1.6, "aimbot_smooth": 1.0, "aimbot_smooth_intensity": 1.0, "aimbot_ease_out": 0.85, "aimbot_overshoot_chance": 0.3, "aimbot_overshoot_strength": 3.5,
            "trigger_enable": False, "trigger_attack_all": False, "trigger_key": "MOUSE4", "trigger_delay": 0.01, "trigger_flash_check": True,
            "bunnyhop_enable": True, "bunnyhop_key": "SPACE", "noflash_enable": False, "noflash_strength": 1.0, "radar_enable": True, "draw_crosshair": True, "watermark_enable": True,
            "norecoil_enable": False, "norecoil_x": 1.0, "norecoil_y": 1.0, "autoaccept_enable": True, "DiscordRPC": True,
            "config_profile": 0,
        })
    
    def get(self, key, default=None):
        with self._lock:
            return self._data.get(key, default)
    
    def set(self, key, value):
        with self._lock:
            self._data[key] = value
            
    def save(self, filename):
        if not filename.endswith(".json"):
            filename += ".json"
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        filepath = os.path.join(self.config_dir, filename)
        
        with self._lock:
            config_data = dict(self._data)
            
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True

    def load(self, filename):
        if not filename.endswith(".json"):
            filename += ".json"
        filepath = os.path.join(self.config_dir, filename)
        if not os.path.exists(filepath):
            return False
        
        with open(filepath, 'r') as f:
            config_data = json.load(f)
            
        with self._lock:
            for key, value in config_data.items():
                self._data[key] = value
        return True
        
    def list_configs(self):
        if not os.path.exists(self.config_dir):
            return ["No configs found"]
        files = [f for f in os.listdir(self.config_dir) if f.endswith(".json")]
        return files if files else ["No configs found"]
    

client, pm = descritptor()

center_x_circle = WINDOW_WIDTH // 2 + 0.5
center_y_circle = WINDOW_HEIGHT // 2 + 0.5

weapon_draw_list = None

def weapon_worker(shared_list, settings_proxy):
    worker_client, worker_pm = descritptor()
    if not worker_client or not worker_pm:
        return

    while True:
        try:
            if is_cs2_window_active() is None:
                shared_list[:] = []
                time.sleep(1)
                continue

            if not settings_proxy.get("esp_dropped_weapons", False):
                shared_list[:] = []
                time.sleep(1)
                continue

            view_matrix, _, _, entity_list, _ = offsets_mem(worker_pm, worker_client)
            if entity_list == 0:
                time.sleep(1)
                continue

            temp_weapon_list = []
            for i in range(64, 1024):
                weapon_data = esp_dweapon(worker_pm, i, entity_list, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)
                if weapon_data:
                    weapon_screen_pos, weapon_name = weapon_data
                    if weapon_name != 'unknown' and weapon_screen_pos:
                        temp_weapon_list.append({
                            'pos': weapon_screen_pos,
                            'name': weapon_name
                        })
            
            shared_list[:] = temp_weapon_list

        except Exception:
            shared_list[:] = []
        
        time.sleep(0.1)

def esp(draw_list):
    global center_x_circle, center_y_circle
    
    if is_cs2_window_active() is None or not settings.get("esp_enable"):
        return

    s = {
        'draw_fov': settings.get('draw_fov'),
        'esp_fov_color': settings.get('esp_fov_color'),
        'aimbot_fov': settings.get('aimbot_fov'),
        'draw_crosshair': settings.get('draw_crosshair'),
        'esp_crosshair_color': settings.get('esp_crosshair_color'),
        'esp_snap_lines': settings.get('esp_snap_lines'),
        'esp_ally_color': settings.get('esp_ally_color'),
        'esp_enemy_color': settings.get('esp_enemy_color'),
        'esp_ally_snapline_color': settings.get('esp_ally_snapline_color'),
        'esp_enemy_snapline_color': settings.get('esp_enemy_snapline_color'),
        'esp_box_fill_spotted_color': settings.get('esp_box_fill_spotted_color'),
        'esp_box_fill_normal_color': settings.get('esp_box_fill_normal_color'),
        'esp_box_fill_immune_color': settings.get('esp_box_fill_immune_color'),
        'esp_box_border_color': settings.get('esp_box_border_color'),
        'esp_health_bar_bg_color': settings.get('esp_health_bar_bg_color'),
        'esp_health_bar_color': settings.get('esp_health_bar_color'),
        'esp_armor_bar_color': settings.get('esp_armor_bar_color'),
        'esp_head_dot_color': settings.get('esp_head_dot_color'),
        'esp_skeleton_color': settings.get('esp_skeleton_color'),
        'esp_name_color': settings.get('esp_name_color'),
        'esp_weapon_color': settings.get('esp_weapon_color'),
        'esp_eye_line_color': settings.get('esp_eye_line_color'),
        'esp_box': settings.get('esp_box'),
        'esp_filled_box': settings.get('esp_filled_box'),
        'esp_corners': settings.get('esp_corners'),
        'esp_head_dot': settings.get('esp_head_dot'),
        'esp_eye_lines': settings.get('esp_eye_lines'),
        'esp_skeleton': settings.get('esp_skeleton'),
        'esp_names': settings.get('esp_names'),
        'esp_weapons': settings.get('esp_weapons'),
        'esp_health_bar': settings.get('esp_health_bar'),
        'esp_armor_bar': settings.get('esp_armor_bar'),
        'esp_bomb': settings.get('esp_bomb'),
        'esp_bomb_defusing_color': settings.get('esp_bomb_defusing_color'),
        'esp_bomb_color': settings.get('esp_bomb_color'),
        'esp_dropped_weapons': settings.get('esp_dropped_weapons'),
        'esp_dropped_weapon_color': settings.get('esp_dropped_weapon_color'),
    }

    center_x = WINDOW_WIDTH / 2
    center_y = WINDOW_HEIGHT * 0.90

    view_matrix, local_player_pawn_addr, local_player_team, entity_list, entity_ptr = offsets_mem(pm, client)
    if local_player_team == 0 or entity_ptr == 0:
        return
    
    if s['draw_fov']:
        color_circle_outline = s['esp_fov_color']
        radius = s['aimbot_fov']
        screen_radius = radius / 100.0 * min(center_x_circle, center_y_circle)
        draw_circle_outline(draw_list, center_x_circle, center_y_circle, screen_radius, color_circle_outline, 1.0)

    if s['draw_crosshair']:
        px_size_crosshair = 1
        radius_crosshair = 3
        color_crosshair = s['esp_crosshair_color']
        draw_circle_outline(draw_list, center_x_circle, center_y_circle, radius_crosshair, color_crosshair, px_size_crosshair)
    
    for i in range(1, 65):
        try:
            client_m = client_mem(pm, i, entity_ptr, entity_list, local_player_pawn_addr, local_player_team)
            if not client_m:
                continue

            entity_team, _, entity_pawn_addr, entity_controller, spotted = client_m
            bottom_left_x, bottom_y, bone_matrix, headX, headY, headZ, head_pos = esp_line(pm, entity_pawn_addr, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)
            if head_pos[1] < 0:
                continue
            
            immunity = esp_immunity(pm, entity_pawn_addr)
            is_ally = entity_team == local_player_team
            
            espcolor = s['esp_ally_color'] if is_ally else s['esp_enemy_color']
            linecolor = s['esp_ally_snapline_color'] if is_ally else s['esp_enemy_snapline_color']
            filled_box_color = s['esp_box_fill_spotted_color'] if spotted else s['esp_box_fill_normal_color']
            if immunity:
                filled_box_color = s['esp_box_fill_immune_color']

            if s['esp_snap_lines']:
                draw_line(draw_list, bottom_left_x, bottom_y, center_x, center_y, linecolor, 1.0)
    
            leftX, leg_pos, rightX, deltaZ = esp_box(pm, bone_matrix, view_matrix, headX, headY, head_pos, WINDOW_WIDTH, WINDOW_HEIGHT)
            
            if s['esp_box']:
                draw_box(draw_list, leftX, leg_pos[1], rightX, head_pos[1], s['esp_box_border_color'], 1.0)
            if s['esp_filled_box']:
                draw_filled_box(draw_list, leftX, leg_pos[1], rightX, head_pos[1], filled_box_color)
            if s['esp_corners']:
                draw_corners(draw_list, leftX, leg_pos[1], rightX, head_pos[1], espcolor, 1.0, 0.3)
    
            if s['esp_head_dot']:
                head_hitbox_x, head_hitbox_y, head_hitbox_radius = esp_headbox(pm, bone_matrix, view_matrix, rightX, leftX, WINDOW_WIDTH, WINDOW_HEIGHT)
                draw_circle(draw_list, head_hitbox_x, head_hitbox_y, head_hitbox_radius, s['esp_head_dot_color'])

            if s['esp_eye_lines']:
                firstX, firstY, end_point  = esp_head_line(pm, entity_pawn_addr, bone_matrix, view_matrix, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
                draw_line(draw_list, firstX, firstY, end_point[0], end_point[1], s['esp_eye_line_color'], 1.0)

            if s['esp_skeleton']:
                bone_connections, bone_positions = esp_bone(pm, bone_matrix, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)
                for connection in bone_connections:
                    if connection[0] in bone_positions and connection[1] in bone_positions:
                        draw_line(draw_list, bone_positions[connection[0]][0], bone_positions[connection[0]][1], bone_positions[connection[1]][0], bone_positions[connection[1]][1], s['esp_skeleton_color'], 1.0)
            
            if s['esp_names']:
                player_name = esp_nickname(pm, entity_controller)
                draw_nickname(draw_list, player_name, head_pos, rightX, leftX, s['esp_name_color'])
            
            if s['esp_weapons']:
                weapon_name = esp_weapon(pm, entity_pawn_addr)
                draw_weapon(draw_list, weapon_name, leg_pos, rightX, leftX, s['esp_weapon_color'])

            if s['esp_health_bar']:
                hp_bar_x_left, hp_bar_y_top, hp_bar_y_bottom, current_hp_height = esp_hp(pm, entity_pawn_addr, deltaZ, head_pos, leftX)
                draw_line(draw_list, hp_bar_x_left, hp_bar_y_top, hp_bar_x_left, hp_bar_y_bottom + current_hp_height, s['esp_health_bar_bg_color'], 2.0)
                draw_line(draw_list, hp_bar_x_left, hp_bar_y_bottom, hp_bar_x_left, hp_bar_y_bottom + current_hp_height, s['esp_health_bar_color'], 2.0)
            
            if s['esp_armor_bar']:
                armor_bar_x_left, armor_bar_y_top, armor_bar_x_right, current_armor_width = esp_br(pm, entity_pawn_addr, deltaZ, head_pos, rightX, leftX, leg_pos)
                draw_line(draw_list, armor_bar_x_left, armor_bar_y_top, armor_bar_x_right, armor_bar_y_top, s['esp_health_bar_bg_color'], 2.0)
                draw_line(draw_list, armor_bar_x_left, armor_bar_y_top, armor_bar_x_left + current_armor_width, armor_bar_y_top, s['esp_armor_bar_color'], 2.0)

        except Exception:
            continue
            
    try:
        if s['esp_bomb'] and csBomb.isPlanted(pm, client):
            bomb_pos = csBomb.getPositionWTS(pm, client, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)
            if bomb_pos and bomb_pos[0] > 0 and bomb_pos[1] > 0:
                time_left = csBomb.getBombTime(pm, client)
                defuse_time = csBomb.getDefuseTime(pm, client)
                text = f"BOMB: {time_left:.1f}s"
                is_defusing = defuse_time > 0
                if is_defusing:
                    text += f" | DEFUSE: {defuse_time:.1f}s"
                bomb_color = s['esp_bomb_defusing_color'] if is_defusing else s['esp_bomb_color']
                draw_text(draw_list, bomb_pos[0], bomb_pos[1], text, color=bomb_color)
    except Exception:
        pass
        
    global weapon_draw_list
    if weapon_draw_list is not None and s["esp_dropped_weapons"]:
        dweaponcolor = s['esp_dropped_weapon_color']
        for weapon in weapon_draw_list:
            draw_text(draw_list, weapon['pos'][0], weapon['pos'][1], weapon['name'], dweaponcolor)

settings = None

def wallhack(s):
    global settings, weapon_draw_list
    settings = s
    manager = Manager()
    weapon_draw_list = manager.list()
    worker = Process(target=weapon_worker, args=(weapon_draw_list, settings,), daemon=True)
    worker.start()
    render_loop(esp)

tabs_config = config_tabs

def begin_disabled(disabled=True):
    if disabled:
        imgui.push_style_var(imgui.STYLE_ALPHA, imgui.get_style().alpha * 0.5)
    return disabled

def end_disabled(disabled):
    if disabled:
        imgui.pop_style_var()

def check_dependencies(element, settings):
    for (key, expected) in element.get("dependencies", []):
        if settings.get(key) != expected:
            return False
    return True

settings = None

def menu(s):
    global settings
    settings = s
    if not glfw.init():
        return
        
    if not verdana_bytes or not font_awesome:
        print("Essential fonts failed to download. The application cannot start.", file=sys.stderr)
        glfw.terminate()
        sys.exit(1)

    window_width, window_height = 800, 600
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.DECORATED, glfw.FALSE)
    window = glfw.create_window(window_width, window_height, "Cheat Menu", None, None)
    if not window:
        glfw.terminate()
        return
        
    glfw.hide_window(window)
    glfw.make_context_current(window)
    glfw.set_window_pos(window, 100, 100)

    imgui.create_context()
    impl = GlfwRenderer(window)
    io = imgui.get_io()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as f:
        f.write(verdana_bytes)
        verdana_path = f.name
    main_font = io.fonts.add_font_from_file_ttf(verdana_path, 16)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as f:
        f.write(font_awesome)
        fa_path = f.name

    icon_ranges = imgui.core.GlyphRanges([0xf000, 0xf8ff, 0])
    icon_font = io.fonts.add_font_from_file_ttf(fa_path, 30, glyph_ranges=icon_ranges)

    impl.refresh_font_texture()
    setup_imgui_style()

    current_tab = 0
    prev_tab = -1
    tab_animations = [0.0] * len(config_tabs)
    content_alpha = 0.0
    last_tab_change_time = 0
    last_press_time = 0
    dragging = False
    visible = False
    
    config_filename_buffer = [""]
    
    config_tab_index = next((i for i, tab in enumerate(tabs_config) if tab["name"] == "CONFIGS"), -1)
    if config_tab_index != -1:
        config_combo = next((el for el in tabs_config[config_tab_index]["elements"] if el["name"] == "config_profile"), None)
        if config_combo:
            config_combo["items"] = settings.list_configs()


    while not glfw.window_should_close(window):
        s_cache = {
            'menu_key': settings.get('menu_key'),
        }
        raw_key = s_cache['menu_key']
        
        if isinstance(raw_key, str):
            s_key = win32_key_map.get(raw_key, 0xA1)
        else:
            s_key = raw_key

        current_time = time.time()
        if win32api.GetAsyncKeyState(s_key) < 0:
            if current_time - last_press_time > 0.3:
                visible = not visible
                last_press_time = current_time
                if visible:
                    glfw.show_window(window)
                else:
                    glfw.hide_window(window)

        if visible:
            glfw.poll_events()
            impl.process_inputs()
            imgui.new_frame()
            
            if imgui.is_mouse_clicked(0) and not imgui.is_any_item_hovered() and not imgui.is_any_item_active():
                dragging = True
                win_x, win_y = glfw.get_window_pos(window)
                cursor_x, cursor_y = glfw.get_cursor_pos(window)
                initial_screen_x = win_x + cursor_x
                initial_screen_y = win_y + cursor_y
                initial_win_x, initial_win_y = win_x, win_y
        
            if dragging:
                current_win_x, current_win_y = glfw.get_window_pos(window)
                cursor_x, cursor_y = glfw.get_cursor_pos(window)
                current_screen_x = current_win_x + cursor_x
                current_screen_y = current_win_y + cursor_y
                delta_x = current_screen_x - initial_screen_x
                delta_y = current_screen_y - initial_screen_y
                glfw.set_window_pos(window, int(initial_win_x + delta_x), int(initial_win_y + delta_y))
        
            if imgui.is_mouse_released(0):
                dragging = False
        
            io = imgui.get_io()
            
            if prev_tab != current_tab:
                last_tab_change_time = current_time
                content_alpha = 0.0
                prev_tab = current_tab
            
            for i in range(len(tab_animations)):
                if i == current_tab:
                    tab_animations[i] = min(tab_animations[i] + io.delta_time * 2, 1.0)
                else:
                    tab_animations[i] = 0.0

            time_since_change = current_time - last_tab_change_time
            fade_duration = 0.5
            content_alpha = min(time_since_change / fade_duration, 1.0)
        
            imgui.set_next_window_size(window_width, window_height)
            imgui.set_next_window_position(0, 0)
            imgui.begin("MainWindow", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
            imgui.begin_child("MainContent", 0, 0, border=False)
            
            imgui.begin_group()
            current_tab = custom_tab_bar(config_tabs, current_tab, 120, icon_font, main_font, tab_animations)
            imgui.end_group()
            
            imgui.same_line()
            
            is_visuals_tab = tabs_config[current_tab]["name"] == "VISUALS"
            content_width = 450 if is_visuals_tab else 0
            
            imgui.begin_child("TabContent", content_width, 0, border=False)
            if content_alpha > 0:
                imgui.push_style_var(imgui.STYLE_ALPHA, content_alpha)
                
                current_tab_config = tabs_config[current_tab]
                section_header(current_tab_config["name"], main_font)
                
                if is_visuals_tab:
                    imgui.columns(2, "visuals_settings", border=False)

                for element in current_tab_config["elements"]:
                    disabled = not check_dependencies(element, settings)
                    disable_state = begin_disabled(disabled)
        
                    if element["type"] == "checkbox":
                        current_val = settings.get(element["name"], element.get("default", False))
                        changed, new_val = custom_checkbox(element["label"], current_val, main_font)
                        if changed and not disabled:
                            settings.set(element["name"], new_val)
        
                    elif element["type"] == "slider":
                        current_val = settings.get(element["name"], element.get("default", 0.0))
                        changed, new_val = custom_slider_float(
                            element["label"], current_val, element["min"], element["max"],
                            element.get("format", "%.2f"), main_font)
                        if changed and not disabled:
                            settings.set(element["name"], new_val)
                    
                    elif element["type"] == "combo":
                        current_val = settings.get(element["name"], element.get("default", 0))
                        new_val = custom_combo(element["label"], current_val, element["items"], main_font)
                        if new_val is not None and new_val != current_val and not disabled:
                            settings.set(element["name"], new_val)

                    elif element["type"] == "color":
                        current_val = settings.get(element["name"])
                        changed, new_val = color_cube(element["label"], current_val, main_font)
                        if changed and not disabled:
                            settings.set(element["name"], new_val)
                        if is_visuals_tab:
                            imgui.next_column()

                    elif element["type"] == "bind":
                        current_val = settings.get(element["name"])
                        new_val = key_bind(element["label"], current_val, main_font)
                        if new_val is not None and not disabled:
                            settings.set(element["name"], new_val)

                    elif element["type"] == "button":
                        if custom_button(element["label"], main_font) and not disabled:
                            if element["name"] == "config_save":
                                if config_filename_buffer[0]:
                                    settings.save(config_filename_buffer[0])
                            elif element["name"] == "config_load":
                                selected_idx = settings.get("config_profile", 0)
                                if selected_idx < len(config_combo["items"]):
                                    selected_file = config_combo["items"][selected_idx]
                                    if selected_file != "No configs found":
                                        settings.load(selected_file)
                            elif element["name"] == "config_refresh":
                                config_combo["items"] = settings.list_configs()
                                settings.set("config_profile", 0)

                    elif element["type"] == "text_input":
                        changed, new_text = custom_text_input(element["label"], config_filename_buffer[0], 64, main_font)
                        if changed:
                            config_filename_buffer[0] = new_text

                    end_disabled(disable_state)
                
                if is_visuals_tab:
                    imgui.columns(1)
                
                imgui.pop_style_var()
        
            imgui.end_child()
            
            if is_visuals_tab:
                imgui.same_line()
                imgui.begin_child("PreviewPanel", 0, 0, border=True)
                draw_esp_preview(settings, main_font)
                imgui.end_child()

            imgui.end_child()
            imgui.end()

            gl.glClearColor(*color_bg_dark)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)
            time.sleep(0.001)
        else:
            time.sleep(0.05)

    impl.shutdown()
    glfw.terminate()
    for path in [verdana_path, fa_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError as e:
                pass

client, pm = descritptor()

def norecoil(settings):
    while True:
        s_cache = {
            'norecoil_enable': settings.get('norecoil_enable'),
            'norecoil_x': settings.get('norecoil_x'),
            'norecoil_y': settings.get('norecoil_y'),
        }

        if not s_cache['norecoil_enable'] or not is_cs2_window_active():
            time.sleep(0.1)
            continue
        try:
            player = pm.read_longlong(client + dwLocalPlayerPawn)
            x, y = no_recoil(pm, client, player)
            
            move_x = int(x * s_cache['norecoil_x'])
            move_y = int(y * s_cache['norecoil_y'])
            
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, move_x, move_y, 0, 0)
        except:
            pass
        time.sleep(0.001)

client, pm = descritptor()

def send_mouse_click():
   if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
       return False
   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
   time.sleep(0.01)
   win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
   return True

def triggerbot(settings):
   while True:
        s_cache = {
            'trigger_enable': settings.get('trigger_enable'),
            'trigger_key': settings.get('trigger_key'),
            'trigger_attack_all': settings.get('trigger_attack_all'),
            'trigger_flash_check': settings.get('trigger_flash_check'),
            'trigger_delay': settings.get('trigger_delay'),
        }

        if not s_cache['trigger_enable'] or not is_cs2_window_active():
           time.sleep(0.1)
           continue
           
        key_code = win32_key_map.get(s_cache['trigger_key'], 0)
        if win32api.GetAsyncKeyState(key_code) & 0x8000:
           try:
               player = pm.read_longlong(client + dwLocalPlayerPawn)
               if not player:
                   continue

               if s_cache['trigger_flash_check']:
                   flash_duration = pm.read_float(player + m_flFlashDuration)
                   if flash_duration > 0:
                       time.sleep(0.1)
                       continue

               entityId = pm.read_int(player + m_iIDEntIndex)
               if entityId > 0:
                   entList = pm.read_longlong(client + dwEntityList)
                   entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                   entity = pm.read_longlong(entEntry + 112 * (entityId & 0x1FF))
                   
                   entityTeam = pm.read_int(entity + m_iTeamNum)
                   playerTeam = pm.read_int(player + m_iTeamNum)
                   
                   if entityTeam != playerTeam or s_cache['trigger_attack_all']:
                       entityHp = pm.read_int(entity + m_iHealth)
                       immunity = pm.read_int(entity + m_bGunGameImmunity)
                       if entityHp > 0 and immunity == 0:
                           time.sleep(s_cache['trigger_delay'])
                           send_mouse_click()
           except Exception:
               time.sleep(0.01)
        
        time.sleep(0.001)

def DiscordRPC(settings):
    rpc = None
    client_id = "1491827634429235363"

    while True:
        rpc_enabled = settings.get('DiscordRPC')

        if rpc_enabled:
            try:
                if rpc is None:
                    rpc = Presence(client_id)
                    rpc.connect()
                
                rpc.update(
                    details="Pena",
                    start=time.time(),
                    large_image="logo",
                    buttons=[
                        {
                            "label": "Download",
                            "url": "https://github.com/daggerfolskiy/LegitSense/releases/latest"
                        },
                        {
                            "label": "Github",
                            "url": "https://github.com/daggerfolskiy/LegitSense"
                        }
                    ]
                )
                time.sleep(15) 
                
            except Exception as e:
                rpc = None
                time.sleep(5)
        else:
            if rpc:
                rpc.close()
                rpc = None
            time.sleep(1)

if __name__ == "__main__":
    freeze_support()
    with Manager() as manager:
        settings = Settings(manager)
        if wait_cs2():
            processes = [
                Process(target=triggerbot, args=(settings,)),
                Process(target=menu, args=(settings,)),
                Process(target=bunnyhop, args=(settings,)),
                Process(target=wallhack, args=(settings,)),
                Process(target=aimbot, args=(settings,)),
                Process(target=norecoil, args=(settings,)),
                Process(target=auto_accept, args=(settings,)),
                Process(target=DiscordRPC, args=(settings,))
            ]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
