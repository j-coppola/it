import random
from random import randint as roll

features = {
            'eyes':{'prefix':['bright', 'dull', 'large', 'tiny', 'squinting', 'piercing'],
                    'color':['red', 'blue', 'yellow', 'azure', 'teal'],
                    'value':['eyes']
                    },

            'teeth':{'prefix':['large', 'particularly large', 'small but sharp'],
                     'color':[],
                     'value':['fangs', 'incisors', 'teeth']
                     },

            'ears':{'prefix':['pointed', 'wide', 'protruding', 'flat', 'flattened'],
                     'color':[],
                     'value':['ears']
                     },

            'face':{'prefix':['a scowling', 'a wizened', 'a friendly', 'a gaunt', 'a sulking'],
                    'color':[],
                    'value':['face', 'face', 'face', 'face', 'face', 'visage', 'countenance', 'appearance']
                    },

            'arms':{'prefix':['muscular', 'slender', 'strong', 'bulky', 'long'],
                    'color':[],
                    'value':['arms']
                    },

            'size':{'prefix':['small', 'smallish', 'medium-sized', 'stout', 'squat', 'large', 'hulking', 'hefty', 'lanky', 'limber'],
                    'color':[],
                    'value':['humanoid', 'humanoid', 'humanoid' , 'creature', 'biped', 'critter'] # 'being'
                    },


            'skin_naked':{'prefix':['dull', 'pale', 'muted', 'smooth', 'rough'],
                           'color':['green', 'blue', 'tan', 'pinkish'],
                           'value':['skin']
                    },

            'skin_scaled':{'prefix':['tiny', 'small', 'large', 'hexagonal', 'rough'],
                           'color':['green', 'blue', 'brown', 'grey', 'greyish', 'greenish', 'blueish', 'brownish'],
                           'value':['scales']
                    },


            'skin_covering_hair':{'prefix':['partially covered in', 'sparsely covered in', 'mostly covered in', 'covered in', 'completely covered in', 'completely covered in thick', 'covered in thick'],
                                  'color':['brown', 'dull brown', 'dull grey', 'grey', 'black'],
                                  'value':['hair', 'hair', 'fur']
                    },

            }

def describe_feature(feature):
    description = ''

    if features[feature]['prefix']:
        description += random.choice(features[feature]['prefix']) + ' '

    if features[feature]['color']:
        description += random.choice(features[feature]['color']) + ' '

    description += random.choice(features[feature]['value'])

    return description


def gen_creature_description(creature_name):
    # Using the human template for now, this will be updated to include actual procedurally generated creatures eventually

    possible_flavor_text_values = ['eyes', 'teeth', 'ears', 'face', 'arms']
    flavor_text_values = []

    for i in xrange(2):
        flavor_text = describe_feature(possible_flavor_text_values.pop(roll(0, len(possible_flavor_text_values)-1)))
        flavor_text_values.append(flavor_text)

    size = describe_feature('size')
    skin = describe_feature('skin_naked')

    if roll(1, 10) > 1:
        hair = describe_feature('skin_covering_hair')
    else:
        hair = 'completely hairless'

    description = random.choice([
                    'A {0} with {1} and {2}. It has {3} and is {4}.',
                    'A {0} with {1} and {2}. It has {3} and is {4}.',
                    'A {0} with {1} and {2}. It is {4} and has {3}.',
                    'A {0} with {3}. It has {1} and {2}. It is {4}.',
                    'A {0} that is {4}. It has {3}, {1}, and {2}.',
                    'This {0} has {3} and is {4}. It has {1} and {2}.',
                    'This {0} is {4} and has {3}. It has {1} and {2}.',

                    'The {5}s are {0}s who are {4} and have {3}. They have {1} and {2}.',
                    '{5}s are a race of {0}s who are {4} and have {3}. They have {1} and {2}.',
                    ])

    description = description.format(size, flavor_text_values[0], flavor_text_values[1], skin, hair, creature_name)

    return description


if __name__ == '__main__':
    for i in xrange(8):
        print gen_creature_description('test')