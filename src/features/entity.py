import pyMeow as pm
from core.offsets import *
from core.utils import *

class Entity:
    def __init__(self, entity_controller, entity_pawn, process):
        self.entity_controller = entity_controller
        self.entity_pawn = entity_pawn
        self.process = process

    def health(self):
        return pm.r_int(self.process, self.entity_pawn + m_iHealth)
    
    def armor(self):
        return pm.r_int(self.process, self.entity_pawn + m_ArmorValue)

    def team(self):
        return pm.r_int(self.process, self.entity_pawn + m_iTeamNum)

    def name(self):
        return pm.r_string(self.process, self.entity_controller + m_iszPlayerName)
    
    def weapon(self):
        current = pm.r_int64(self.process, self.entity_pawn + m_pClippingWeapon)

        if current == 0:
            return ""

        index = pm.r_int16(self.process, current + m_AttributeManager + m_Item + m_iItemDefinitionIndex)
        return Utils.weapon_icon(index)

    def spotted(self):
        return pm.r_bool(self.process, self.entity_pawn + m_entitySpottedState + m_bSpotted)
    
    def pos(self):
        return pm.r_vec3(self.process, self.entity_pawn + m_vOldOrigin)
    
    def bone_pos(self, index):
        scene = pm.r_int64(self.process, self.entity_pawn + m_pGameSceneNode)
        bone = pm.r_int64(self.process, scene + m_pBoneArray)
        return pm.r_vec3(self.process, bone + index * 48)

    def world_to_screen(self, view_matrix):
        try:
            self.pos_2d = pm.world_to_screen(view_matrix, self.pos(), 1)
            self.head_pos_2d = pm.world_to_screen(view_matrix, self.bone_pos(7), 1)       # HEAD
            self.neck = pm.world_to_screen(view_matrix, self.bone_pos(6), 1)              # NECK
            self.left_feet = pm.world_to_screen(view_matrix, self.bone_pos(74), 1)        # FOOT_TOES_L_T
            self.right_feet = pm.world_to_screen(view_matrix, self.bone_pos(77), 1)       # FOOT_TOES_R_T
            self.waist = pm.world_to_screen(view_matrix, self.bone_pos(1), 1)             # PELVIS
            self.left_knees = pm.world_to_screen(view_matrix, self.bone_pos(18), 1)       # KNEE_L
            self.right_knees = pm.world_to_screen(view_matrix, self.bone_pos(21), 1)      # KNEE_R
            self.left_hand = pm.world_to_screen(view_matrix, self.bone_pos(11), 1)        # HAND_L
            self.right_hand = pm.world_to_screen(view_matrix, self.bone_pos(15), 1)       # HAND_R
            self.left_elbow = pm.world_to_screen(view_matrix, self.bone_pos(10), 1)       # ELBOW_L
            self.right_elbow = pm.world_to_screen(view_matrix, self.bone_pos(14), 1)      # ELBOW_R
            self.left_shoulder = pm.world_to_screen(view_matrix, self.bone_pos(9), 1)     # SHOULDER_L
            self.right_shoulder = pm.world_to_screen(view_matrix, self.bone_pos(13), 1)   # SHOULDER_R
        except:
            return False
        
        return True

class Entities:
    def __init__(self, process, module):
        self.process = process
        self.module = module

    def enumerate(self):
        try:
            local_player_controller = pm.r_int64(self.process, self.module + dwLocalPlayerController)
            entity_list = pm.r_int64(self.process, self.module + dwEntityList)
            
            for entity in range(1, 65):
                try:
                    entity_entry = pm.r_int64(self.process, entity_list + (8 * (entity & 0x7FFF) >> 9) + 16)
                    entity_controller = pm.r_int64(self.process, entity_entry + 120 * (entity & 0x1FF))

                    if entity_controller == 0 or entity_controller == local_player_controller:
                        continue
                    
                    entity_controller_pawn = pm.r_int64(self.process, entity_controller + m_hPlayerPawn)
                    
                    if entity_controller_pawn == 0:
                        continue
                        
                    entity_list_ptr = pm.r_int64(self.process, entity_list + 8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16)
                    entity_pawn = pm.r_int64(self.process, entity_list_ptr + 120 * (entity_controller_pawn & 0x1FF))
                    
                    if entity_pawn == 0:
                        continue
                except:
                    continue

                yield Entity(entity_controller, entity_pawn, self.process)
        except:
            pass
