"""Sample data to be used for testing"""

def sample_stash_data():
    return [
        {'id': '227fb59f186902743142e4f2e26f8cb3b9583e38bcab49ed802d5793667c45bc', 'public': True, 'accountName': 'ACCOUNT1',
        'lastCharacterName': 'CHARACTER1', 'stash': 'Sell', 'stashType': 'PremiumStash', 'league': 'Incursion Event (IRE001)',
        'items': [
            {'verified': False, 'w': 2, 'h': 1, 'ilvl': 69, 'icon':
                'http://web.poecdn.com/image/Art/2DItems/Belts/Belt4.png?scale=1&scaleIndex=0&w=2&h=1&v=da282d3a3d76fc0d14b882450c3ed2ae',
                'league': 'Incursion Event (IRE001)', 'id': '5b4549df8f0c94683d08e42749cc1afd786afaf3b7a127690e4c22e50b74e03b',
                'name': '<<set:MS>><<set:M>><<set:S>>Behemoth Lock', 'typeLine': 'Cloth Belt', 'identified': True, 'note': '~price 3 chaos',
                'requirements': [{'name': 'Level', 'values': [['52', 0]], 'displayMode': 0}],
                'implicitMods': ['23% increased Stun and Block Recovery'], 'explicitMods': ['+41 to Strength', '+97 to maximum Life',
                '+36% to Lightning Resistance', '11% increased Flask effect duration'], 'frameType': 2,
                'category': {'accessories': ['belt']}, 'x': 10, 'y': 6, 'inventoryId': 'Stash1'},
            {'verified': False, 'w': 1, 'h': 1, 'ilvl': 0, 'icon':
                'http://web.poecdn.com/image/Art/2DItems/Gems/PowerSiphon.png?scale=1&scaleIndex=0&w=1&h=1&v=9650c4f94cef22ba419e0b0492fb4a8b',
                'support': False, 'league': 'Incursion Event (IRE001)', 'id':
                '650bc10eac5cb05c601aedb99fa8b899633bce33604e6b2dfeef3fa2001ef2d0', 'name': '', 'typeLine': 'Power Siphon',
                'identified': True, 'note': '~price 2 chaos', 'properties': [ {'name': 'Attack, Projectile', 'values': [], 'displayMode': 0},
                    {'name': 'Level', 'values': [['1', 0]], 'displayMode': 0, 'type': 5}, {'name': 'Mana Cost', 'values': [['7', 0]], 'displayMode': 0},
                    {'name': 'Effectiveness of Added Damage', 'values': [['125%', 0]], 'displayMode': 0}, {'name': 'Quality', 'values': [['+20%', 1]], 'displayMode': 0, 'type': 6}],
                'additionalProperties': [ {'name': 'Experience', 'values': [['1/15249', 0]], 'displayMode': 2, 'progress': 6.557806773344055e-05, 'type': 20}],
                'requirements': [ {'name': 'Level', 'values': [['12', 0]], 'displayMode': 0}, {'name': 'Int', 'values': [['33', 0]], 'displayMode': 1}],
                'secDescrText': 'Fires your wand to unleash projectiles that fire toward enemies in front of you or to your sides, dealing increased damage and granting you a power charge if an enemy is killed by, or soon after, the hit.',
                'explicitMods': [ 'Deals 125% of Base Damage', 'Fires 4 additional Projectiles', 'Culling Strike', '20% increased Damage',
                '20% chance to gain a Power Charge when Projectile Hits a Rare or Unique Enemy', '20% increased Critical Strike Chance per Power Charge',
                '+10% to Critical Strike Multiplier per Power Charge'],
                'descrText': 'Place into an item socket of the right colour to gain this skill.  Right click to remove from a socket.',
                'frameType': 4, 'category': {'gems': ['activegem']}, 'x': 0, 'y': 0, 'inventoryId': 'Stash2'},
            {'verified': False, 'w': 1, 'h': 1, 'ilvl': 0, 'icon':
                    'http://web.poecdn.com/image/Art/2DItems/Gems/VaalGems/VaalGroundslam.png?scale=1&scaleIndex=0&w=1&h=1&v=b639cf9fbe236d76ba0db71931344893',
                'support': False, 'league': 'Incursion Event (IRE001)', 'id': 'fbb2725aa43b18a7b3d9f733d1e17b0e2844d2be0899bab13f53a21352a13af8',
                'name': '', 'typeLine': 'Vaal Ground Slam', 'identified': True, 'note': '~price 1 chaos', 'corrupted': True,
                'properties': [{'name': 'Vaal, Attack, AoE, Melee', 'values': [], 'displayMode': 0}, {'name': 'Level', 'values': [['1', 0]],
                'displayMode': 0, 'type': 5}, {'name': 'Mana Cost', 'values': [['6', 0]], 'displayMode': 0},
                {'name': 'Quality', 'values': [['+20%', 1]], 'displayMode': 0, 'type': 6}], 'additionalProperties': [{'name': 'Experience',
                'values': [['1/70', 0]], 'displayMode': 2, 'progress': 0.014285714365541935, 'type': 20}], 'requirements': [{'name':
                'Level', 'values': [['1', 0]], 'displayMode': 0}], 'secDescrText': 'The character slams the ground in front of them with their main hand weapon, creating a wave that travels forward and damages enemies with an increased chance to stun.  The wave deals more damage to closer enemies.  Only works with Staves, Axes or Maces.',
                'explicitMods': ['25% reduced Enemy Stun Threshold', '30% increased Stun Duration on enemies', 'Deals up to 40% more Damage to closer targets'],
                'descrText': 'Place into an item socket of the right colour to gain this skill.  Right click to remove from a socket.',
                'frameType': 4, 'category': {'gems': ['activegem']}, 'x': 0, 'y': 2, 'inventoryId': 'Stash3',
                'vaal': {'baseTypeName': 'Ground Slam', 'properties': [{'name': 'Souls Per Use', 'values': [['15', 0]], 'displayMode': 0},
                {'name': 'Can Store %0 Uses', 'values': [['3', 0]], 'displayMode': 3}, {'name': 'Soul Gain Prevention', 'values': [['2 sec', 0]],
                'displayMode': 0}, {'name': 'Effectiveness of Added Damage', 'values': [['185%', 0]], 'displayMode': 0}], 'explicitMods':
                ['Deals 185% of Base Damage', 'Stuns Enemies', '230% increased Stun Duration on enemies', "Can't be Evaded",
                'Deals up to 40% more Damage to closer targets'], 'secDescrText': 'The character slams the ground in front of them with their main hand weapon, creating a wave that travels in all directions that damages and stuns enemies.  The wave deals more damage to closer enemies.  Only works with Staves, Axes or Maces.'}}]},
        {'id': '276b112975ebdc4909ce32618e5577e41028d66fe6d0be8e81d48f5c1229ac62', 'public': True, 'accountName': 'ACCOUNT2',
         'lastCharacterName': 'CHARACTER2', 'stash': '$',
         'stashType': 'PremiumStash', 'league': 'Incursion Event (IRE001)', 'items': [
            {'verified': False, 'w': 1, 'h': 1, 'ilvl': 0,
                'icon': 'http://web.poecdn.com/image/Art/2DItems/Divination/InventoryIcon.png?scale=1&scaleIndex=0&stackSize=1&w=1&h=1&v=a8ae131b97fad3c64de0e6d9f250d743',
                'league': 'Incursion Event (IRE001)', 'id': '673e6ffaa26b26c32b5aa082a4f7c779a4c5fc9b79cd06c3d3086b0f02b11b23',
                'name': '', 'typeLine': 'The Valkyrie', 'identified': True, 'note': '~price 4 chaos', 'properties':
                [{'name': 'Stack Size', 'values': [['1/8', 0]], 'displayMode': 0}], 'explicitMods': ['<uniqueitem>{Nemesis Item}'],
                'flavourText': ['<size:26>{The villain strikes,\r', 'the world is torn.\r', 'A war begins, a hero is born,\r',
                'The nemesis sets the sky alight.\r', "A hero's sacrifice\r", 'sets everything right.\r', "- Drake's Epitaph}"],
                'frameType': 6, 'stackSize': 1, 'maxStackSize': 8, 'artFilename': 'TheValkyrie', 'category': {'cards':
                []}, 'x': 1, 'y': 0, 'inventoryId': 'Stash1'},
            {'verified': False, 'w': 1, 'h': 1, 'ilvl': 0,
             'icon': 'http://web.poecdn.com/image/Art/2DItems/Divination/InventoryIcon.png?scale=1&scaleIndex=0&stackSize=1&w=1&h=1&v=a8ae131b97fad3c64de0e6d9f250d743',
             'league': 'Incursion Event (IRE001)', 'id': '79ded662e9a97821472cbab30d2cd45ae88dc285d177d78f5b399820cd3394ab',
             'name': '', 'typeLine': 'Abandoned Wealth', 'identified': True, 'note': '~price 50 chaos', 'properties': [{'name': 'Stack Size',
             'values': [['1/5', 0]], 'displayMode': 0}], 'explicitMods': ['<currencyitem>{3x Exalted Orb}'], 'flavourText':
                 ['When the world burned, the greedy burned with it, while the clever left as paupers.'],
                 'frameType': 6, 'stackSize': 1, 'maxStackSize': 5, 'artFilename': 'AbandonedWealth', 'category': {'cards': []},
                 'x': 2, 'y': 0, 'inventoryId': 'Stash2'},
            {'verified': False, 'w': 2, 'h': 3, 'ilvl': 69,
             'icon': 'http://web.poecdn.com/image/Art/2DItems/Armours/Shields/ShieldStrIntUnique2.png?scale=1&scaleIndex=0&w=2&h=3&v=3cc4e85d8f87166748078394fe27d218',
             'league': 'Incursion Event (IRE001)', 'id': '16fa6d7591fa9fdb0cffa6359ee53256b4986230dc4457889868ee7c4c74e4a8',
             'sockets': [{'group': 0, 'attr': 'I', 'sColour': 'B'},
             {'group': 1, 'attr': 'S', 'sColour': 'R'}], 'name': '<<set:MS>><<set:M>><<set:S>>Springleaf',
             'typeLine': 'Plank Kite Shield', 'identified': True, 'properties': [{'name': 'Chance to Block', 'values':
                 [['22%', 0]], 'displayMode': 0, 'type': 15}, {'name': 'Armour', 'values': [['36', 1]], 'displayMode': 0, 'type': 16},
             {'name': 'Energy Shield', 'values': [['8', 1]], 'displayMode': 0, 'type': 18}], 'requirements': [{'name': 'Level', 'values': [['7', 0]], 'displayMode': 0}],
             'implicitMods': ['+4% to all Elemental Resistances'], 'explicitMods': ['99% increased Armour and Energy Shield',
             '50% reduced Freeze Duration on you', '3% of Life Regenerated per second',
             '3% of Life Regenerated per second while on Low Life'], 'flavourText': ['From death springs life.'], 'frameType': 3,
             'category': {'armour': ['shield']}, 'x': 10, 'y': 9, 'inventoryId': 'Stash4', 'socketedItems': []},
            ]
        },
    ]
