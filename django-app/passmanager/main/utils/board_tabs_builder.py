from typing import Iterable
from main.models import BoardTab, Board
from django.db import transaction
from django.db.models import Value


class BoardTabsBuilder:

    def __init__(self, board_id:int):
        self.board_id = board_id
        board_exists = Board.objects.filter(id=board_id).exists()
        self.__tabs_qs_cache = BoardTab.objects.filter(board_id=board_id) \
            .order_by("board_order")
        self.tabs = list(self.__tabs_qs_cache)
        self.__delete = []

        if not board_exists:
            raise BoardDoesNotExistError()


    def append_tab(self, name:str, is_default:bool=False):
        if not is_default:
            is_default = None

        obj = BoardTab(
            board_id=self.board_id,
            name=name,
            is_default=is_default
        )
        self.tabs.append(obj)
        return obj

    def prepend_tab(self, name:str, is_default:bool=False):
        if not is_default:
            is_default = None

        obj = BoardTab(
            board_id=self.board_id,
            name=name,
            is_default=is_default
        )
        self.tabs.insert(0, obj)
        return obj

    def change_tab_order(self, tab_id:int, place_after_tab_id:int=None):
        '''
        place_after_tab_id === None will place the tab at the beginning of the list
        '''
        source_tab = None
        source_index = 0
        target_index = 0

        for item in self.tabs:
            if item.id == tab_id:
                source_tab = item
                break
            source_index += 1

        if source_tab is None:
            raise BoardTabNotFoundError()

        if place_after_tab_id is not None:
            for item in self.tabs:
                if item.id == place_after_tab_id:
                    break

                target_index += 1
        else:
            target_index = -1 # -1 means put after the -1 element, so at the beginning of the list

        if target_index == len(self.tabs):
            raise BoardTabNotFoundError()

        if target_index == source_index:
            return

        target_index += 1

        # After removing source index from list, target index will decrease by 1
        if target_index > source_index:
            target_index -= 1

        self.tabs.pop(source_index)
        self.tabs.insert(target_index, source_tab)



    def insert_tab(self, name:str, index:int, is_default:bool=False):
        if not is_default:
            is_default = None

        obj = BoardTab(
            board_id=self.board_id,
            name=name,
            is_default=is_default
        )
        self.tabs.insert(index+1, obj)
        return obj

    def insert_tab_after_id(self, name:str, id:int, is_default:bool=False):
        if not is_default:
            is_default = None

        index = 0
        found = False
        for item in self.tabs:
            if item.id == id:
                found = True
                break

            index += 1

        if not found:
            raise BoardTabNotFoundError()

        obj = BoardTab(
            board_id=self.board_id,
            name=name,
            is_default=is_default
        )
        self.tabs.insert(index+1, obj)
        return obj

    def insert_tab_after_obj(self, name:str, obj:BoardTab, is_default:bool=False):
        if not is_default:
            is_default = None

        index = 0
        found = False
        for item in self.tabs:
            if item == obj:
                found = True
                break

            index += 1

        if not found:
            raise BoardTabNotFoundError()

        obj = BoardTab(
            board_id=self.board_id,
            name=name,
            is_default=is_default
        )
        self.tabs.insert(index+1, obj)
        
        return obj


    def update_objects(self, updates:dict):
        '''
        Updates values in existing tabs

        NOTICE: reordering will be ignored! If you want to reorder tabs, use override_objects method

        Required format: 
        {
            <tab_id>: {
                key:value dict of attributes to update
            }
        }
        '''
        for item in self.tabs:
            if updates.__contains__(item.id):
                for key, value in updates[item.id].items():
                    setattr(item, key, value)

    def get_tab(self, tab_id:int):
        for item in self.tabs:
            if item.id == tab_id:
                return item

        raise BoardTabNotFoundError()

    def override_objects(self, updates:Iterable):
        '''
        Updates values and reorders tabs based on the order in provided array

        NOTICE: if you don't want to change objects order, use update_objects method

        NOTICE2: for new objects (non-existing ones) use id == None
        '''

        tmp_list = []
        tmp_item = None

        for update in updates:
            if update["id"] is not None:
                tmp_item = self.get_tab(update["id"])
            else:
                tmp_item = BoardTab()
            
            for key, value in update.items():
                setattr(tmp_item, key, value)

            tmp_list.append(tmp_item)

        self.tabs.clear()
        for item in tmp_list:
            self.tabs.append(item)
        del tmp_list


    def delete_tab(self, tab_id:int):
        index = 0
        for item in self.tabs:
            if item.id == tab_id:
                break

            index += 1

        if index < len(self.tabs):
            if(self.tabs[index].is_default):
                raise CannotDeleteDefaultTabError()

            self.__delete.append(self.tabs[index].id)
            self.tabs.pop(index)
        else:
            raise BoardTabNotFoundError()

    def save(self):
        create = []
        update = []

        order = 1
        for item in self.tabs:
            item.board_order = order
            if item.id != None:
                update.append(item)
            else:
                create.append(item)

            order += 1

        with transaction.atomic():
            if len(self.__delete) > 0:
                BoardTab.objects.filter(id__in=self.__delete).delete()
            if len(create) > 0:
                BoardTab.objects.bulk_create(create)
            if len(update) > 0:
                BoardTab.objects.bulk_update(update, ("name", "board_order", "is_default"))
            
    


    
class BoardTabsBuilderError(Exception):
    pass

class BoardDoesNotExistError(BoardTabsBuilderError):
    pass

class BoardTabNotFoundError(BoardTabsBuilderError):
    pass

class CannotDeleteDefaultTabError(BoardTabsBuilderError):
    pass



    

