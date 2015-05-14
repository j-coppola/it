from __future__ import division
from math import ceil
from random import randint as roll

from helpers import infinite_defaultdict


GOAL_ITEM = 'cheese'



class TestCreature:
    def __init__(self):
        self.possessions = set([])
        self.gold = 10
        self.profession = None

        self.knowledge = infinite_defaultdict()
        self.knowledge['objects'][GOAL_ITEM]['location']['accuracy'] = 2

    def is_available_to_act(self):
        return 1

class TestEntity:
    def __init__(self):
        self.creature = TestCreature()

        self.wx = 10
        self.wy = 10





class AtLocation:
    def __init__(self, initial_location, target_location, entity):
        self.status = 'at_location'
        self.initial_location = initial_location
        self.target_location = target_location
        self.entity = entity
        # Will be set if this status isn't already completed
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return (self.entity.wx, self.entity.wy) == self.target_location

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = [MoveToLocation(initial_location=self.initial_location, target_location=self.target_location, entity=self.entity)]
        return self.behaviors_to_accomplish


class HaveItem:
    def __init__(self, item, entity):
        self.status = 'have_item'
        self.item = item
        self.entity = entity
        # Will be set if this status isn't already completed
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.item in self.entity.creature.possessions

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = [BuyItem(self.item, self.entity), StealItem(self.item, self.entity)]
        return self.behaviors_to_accomplish


class KnowWhereItemisLocated:
    def __init__(self, item, entity):
        self.status = 'know_where_item_is_located'
        self.item = item
        self.entity = entity
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.entity.creature.knowledge['objects'][self.item]['location']['accuracy'] == 1

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = [FindOutWhereItemIsLocated(self.item, self.entity)]
        return self.behaviors_to_accomplish


class HaveRoughIdeaOfLocation:
    def __init__(self, item, entity):
        self.status = 'have_rough_idea_of_location'
        self.item = item
        self.entity = entity
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.entity.creature.knowledge['objects'][self.item]['location']['accuracy'] <= 2

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = []
        return self.behaviors_to_accomplish


class HaveMoney:
    def __init__(self, money, entity):
        self.status = 'have_item'
        self.money = money
        self.entity = entity
        # Will be set if this status isn't already completed
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.entity.creature.gold >= self.money

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = [GetMoneyThroughWork(self.money, self.entity), StealMoney(self.money, self.entity)]
        return self.behaviors_to_accomplish


class HaveJob:
    def __init__(self, entity):
        self.status = 'have_job'
        self.entity = entity
        # Will be set if this status isn't already completed
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.entity.creature.profession

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = [GetJob(self.entity)]
        return self.behaviors_to_accomplish

class AmAvailableToAct:
    def __init__(self, entity):
        self.status = 'am_available_to_act'
        self.entity = entity
        # Will be set if this status isn't already completed
        self.behaviors_to_accomplish = []

    def is_completed(self):
        return self.entity.creature.is_available_to_act()

    def set_behaviors_to_accomplish(self):
        self.behaviors_to_accomplish = []
        return self.behaviors_to_accomplish



class ActionBase:
    ''' The base action class, providing some default methods for other actions '''
    def __init__(self):
        self.checked_for_movement = 0

    def get_unmet_conditions(self):
        return [precondition for precondition in self.preconditions if not precondition.is_completed()]

    def get_repeats(self):
        return 1

    def get_possible_locations(self):
        return [(roll(0, 10), roll(0, 10))]

    def get_behavior_location(self, current_location):
        return roll(0, 10), roll(0, 10)


class MoveToLocation(ActionBase):
    ''' Specific behavior component for moving to an area.
    Will use road paths if moving from city to city '''
    def __init__(self, initial_location, target_location, entity, travel_verb='travel'):
        ActionBase.__init__(self)
        self.behavior = 'move'
        self.initial_location = initial_location
        self.target_location = target_location
        self.entity = entity

        self.travel_verb = travel_verb

        self.preconditions = [AmAvailableToAct(self.entity)]

    def get_name(self):
        goal_name = '{0} to {1}'.format(self.travel_verb, g.WORLD.tiles[self.location[0]][self.location[1]].get_location_description())
        return goal_name

    def initialize_behavior(self):
        ''' Will be run as soon as this behavior is activated '''
        target_site = g.WORLD.tiles[self.x][self.y].site
        current_site = g.WORLD.tiles[self.entity.wx][self.entity.wy].site

        if target_site in g.WORLD.cities and current_site in g.WORLD.cities:
            self.entity.world_brain.path = current_site.path_to[target_site][:]
        else:
            # Default - use libtcod's A* to create a path to destination
            path = libtcod.path_compute(p=g.WORLD.path_map, ox=self.entity.wx, oy=self.entity.wy, dx=self.x, dy=self.y)
            self.entity.world_brain.path = libtcod_path_to_list(path_map=g.WORLD.path_map)

    def is_completed(self):
        return (self.figure.wx, self.figure.wy) == (self.x, self.y)

    def take_behavior_action(self):
        self.figure.w_move_along_path(path=self.figure.world_brain.path)



class FindOutWhereItemIsLocated(ActionBase):
    def __init__(self, item, entity):
        ActionBase.__init__(self)
        self.behavior = 'find_out_where_item_is_located'
        self.item = item
        self.entity = entity

        self.preconditions = [AmAvailableToAct(self.entity)]

    def get_behavior_location(self, current_location):
        return None

class SearchForItem(ActionBase):
    def __init__(self, item, entity):
        ActionBase.__init__(self)
        self.behavior = 'search_for_item'
        self.item = item
        self.entity = entity

        self.preconditions = [AmAvailableToAct(self.entity), HaveRoughIdeaOfLocation(self.item, self.entity)]


class GetJob(ActionBase):
    def __init__(self, entity):
        ActionBase.__init__(self)
        self.behavior = 'get_job'
        self.entity = entity
        self.preconditions = [AmAvailableToAct(self.entity)]


class GetMoneyThroughWork(ActionBase):
    def __init__(self, money, entity):
        ActionBase.__init__(self)
        self.behavior = 'get_money_through_work'
        self.money = money
        self.entity = entity
        self.preconditions = [HaveJob(self.entity)]

    def get_repeats(self):
        return ceil(self.money / self.entity.profession.monthly_pay)

    # def get_behavior_location(self):
    #     return self.entity.profession.current_work_building.site.x, self.entity.profession.current_work_building.site.y

    #def is_at_location(self):
    #    return (self.entity.wx, self.entity.wy) == self.get_behavior_location()


class StealMoney(ActionBase):
    def __init__(self, money, entity):
        ActionBase.__init__(self)
        self.behavior = 'steal_money'
        self.money = money
        self.entity = entity
        self.preconditions = [AmAvailableToAct(self.entity)]


class BuyItem(ActionBase):
    def __init__(self, item, entity):
        ActionBase.__init__(self)
        self.behavior = 'buy_item'
        self.item = item
        self.entity = entity
        self.preconditions = [HaveMoney(self.item, self.entity)]


class StealItem(ActionBase):
    def __init__(self, item, entity):
        ActionBase.__init__(self)
        self.behavior = 'steal_item'
        self.item = item
        self.entity = entity
        self.preconditions = [KnowWhereItemisLocated(self.item, self.entity)]



def get_movement_behavior_subtree_old(action_path, new_behavior):

    loc1 = new_behavior.get_behavior_location()
    loc2 = action_path[0].get_behavior_location() if action_path else None

    if loc1 and loc2 and loc1 != loc2 and new_behavior.behavior != 'move':
        movement_behavior_subtree = find_actions_leading_to_goal(goal_state=AtLocation(initial_location=loc1, target_location=loc2, entity=action_path[0].entity), action_path=[], all_possible_paths=[])
    else:
        movement_behavior_subtree = [[]]

    return movement_behavior_subtree


def find_actions_leading_to_goal_old(goal_state, action_path, all_possible_paths):
    ''' Recursive function to find all possible behaviors which can be undertaken to get to a particular goal '''
    #print ' --- ', r_level, goal_state.status, [a.behavior for a in action_list], ' --- '

    for behavior_option in goal_state.set_behaviors_to_accomplish():
        ## CHECK IF MOVEMENT IS NEEDED
        movement_behavior_subtree = get_movement_behavior_subtree(action_path=action_path, new_behavior=behavior_option)
        unmet_conditions = behavior_option.get_unmet_conditions()

        for subtree in movement_behavior_subtree:
            current_action_path = [behavior_option] + subtree + action_path # Copy of the new behavior + action_path

            # If there are conditions that need to be met, then we find the actions that can be taken to complete each of them
            for condition in unmet_conditions:
                find_actions_leading_to_goal(goal_state=condition, action_path=current_action_path, all_possible_paths=all_possible_paths)

            # If all conditions are met, then this behavior can be accomplished, so it gets added to the list
            if not unmet_conditions and behavior_option != 'move':
                movement_behavior_subtree = get_movement_behavior_subtree(action_path=action_path, new_behavior=behavior_option)
                for new_subtree in movement_behavior_subtree:
                    all_possible_paths.append(new_subtree + current_action_path)

    return all_possible_paths





def get_movement_behavior_subtree(entity, current_location, target_location):

    if current_location and target_location and current_location != target_location:
        movement_behavior_subtree = find_actions_leading_to_goal(goal_state=AtLocation(initial_location=current_location , target_location=target_location, entity=entity), action_path=[], all_possible_paths=[])
    else:
        movement_behavior_subtree = None

    return movement_behavior_subtree


def find_actions_leading_to_goal(goal_state, action_path, all_possible_paths):
    ''' Recursive function to find all possible behaviors which can be undertaken to get to a particular goal '''
    #print ' --- ', r_level, goal_state.status, [a.behavior for a in action_list], ' --- '

    for behavior_option in goal_state.set_behaviors_to_accomplish():
        unmet_conditions = behavior_option.get_unmet_conditions()
        current_action_path = [behavior_option] + action_path # Copy of the new behavior + action_path

        # If there are conditions that need to be met, then we find the actions that can be taken to complete each of them
        for condition in unmet_conditions:
            find_actions_leading_to_goal(goal_state=condition, action_path=current_action_path, all_possible_paths=all_possible_paths)

        # If all conditions are met, then this behavior can be accomplished, so it gets added to the list
        if not unmet_conditions:
            #all_possible_paths.append(current_action_path)
            print [a.behavior for a in current_action_path]
            all_paths_worked = adjust_path_for_movement(entity=test_entity, action_path=current_action_path, all_paths_worked=[])
            for i, p in enumerate(all_paths_worked):
                print i, [a.behavior for a in p]
                all_possible_paths.append(p)

    return all_possible_paths


def adjust_path_for_movement(entity, action_path, all_paths_worked, r_level=0):
    ''' Recursive function to find all possible behaviors which can be undertaken to get to a particular goal '''

    if r_level > 10:
        return

    current_location = (entity.wx, entity.wy)

    current_action_path = action_path[:]
    for i, behavior in enumerate(action_path):
        if (not behavior.checked_for_movement) and behavior.behavior != 'move':
            target_location = behavior.get_behavior_location(current_location=current_location)
            behavior.checked_for_movement = 1

            if target_location != current_location:
                movement_behavior_subtree = get_movement_behavior_subtree(entity=entity, current_location=current_location, target_location=target_location)
                # print ' --- ', behavior.behavior, movement_behavior_subtree
                if movement_behavior_subtree:
                    for subtree in movement_behavior_subtree:
                        for s_behavior in reversed(subtree):
                            current_action_path.insert(i, s_behavior)

                        adjust_path_for_movement(entity=entity, action_path=current_action_path, all_paths_worked=all_paths_worked, r_level=r_level+1)

                elif not movement_behavior_subtree:
                    adjust_path_for_movement(entity=entity, action_path=current_action_path, all_paths_worked=all_paths_worked, r_level=r_level+1)


    unchecked_for_movement = [a for a in current_action_path if (a.behavior != 'move' and not a.checked_for_movement)]
    if not unchecked_for_movement:
        all_paths_worked.append(current_action_path)

    return all_paths_worked



test_entity = TestEntity()
path_list = find_actions_leading_to_goal(goal_state=HaveItem(item=GOAL_ITEM, entity=test_entity), action_path=[], all_possible_paths=[])
for p in path_list:
    print [b.behavior for b in p]

#test = adjust_path_for_movement(entity=test_entity, action_path=path_list[0], all_paths_worked=[])
#print test