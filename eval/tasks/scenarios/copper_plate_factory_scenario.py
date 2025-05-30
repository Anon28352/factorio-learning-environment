from env.src.entities import Direction, Position
from eval.tasks.scenarios.scenario_abc import ScenarioABC
from env.src.game_types import Resource, Prototype
from env.src.instance import FactorioInstance


class CopperPlateFactoryScenario(ScenarioABC):
    def __init__(self):
        #self.num_drills = num_drills
        pass

    def deploy(self, instance: FactorioInstance):
        instance.initial_inventory = {'stone-furnace': 5,
                                      'iron-chest': 10,
                                      'burner-inserter': 10,
                                      'coal': 50,
                                      'transport-belt': 100,
                                      'burner-mining-drill': 5}
        instance.reset()

        game = instance.namespaces[0]

        # Find copper ore patch
        copper_pos = game.nearest(Resource.CopperOre)
        print(f"Found copper ore at {copper_pos}")

        # Move there and place first drill
        game.move_to(copper_pos)
        drill1 = game.place_entity(Prototype.BurnerMiningDrill, position=copper_pos)
        drill1 = game.insert_item(Prototype.Coal, drill1, quantity=5)
        print(f"Placed first drill at {drill1.position}")

        # Place second drill
        drill2_pos = Position(x=drill1.position.x - 3, y=drill1.position.y)
        game.move_to(drill2_pos)
        drill2 = game.place_entity(Prototype.BurnerMiningDrill, position=drill2_pos)
        drill2 = game.insert_item(Prototype.Coal, drill2, quantity=5)
        print(f"Placed second drill at {drill2.position}")

        # Place third drill
        drill3_pos = Position(x=drill2.position.x - 3, y=drill2.position.y)
        game.move_to(drill3_pos)
        drill3 = game.place_entity(Prototype.BurnerMiningDrill, position=drill3_pos)
        drill3 = game.insert_item(Prototype.Coal, drill3, quantity=5)
        print(f"Placed third drill at {drill3.position}")

        # Log the positions for next step
        print(f"Drill positions: {drill1.position}, {drill2.position}, {drill3.position}")
        # Place first furnace north of middle drill
        furnace1_pos = drill1.drop_position.up(4)
        game.move_to(furnace1_pos)
        furnace1 = game.place_entity(Prototype.StoneFurnace, position=furnace1_pos)
        furnace1 = game.insert_item(Prototype.Coal, furnace1, quantity=5)
        print(f"Placed first furnace at {furnace1.position}")
        game.move_to(furnace1_pos)

        # Place second furnace next to first
        furnace2_pos = furnace1_pos.right(3)
        game.move_to(furnace2_pos)
        furnace2 = game.place_entity(Prototype.StoneFurnace, position=furnace2_pos)
        furnace2 = game.insert_item(Prototype.Coal, furnace2, quantity=5)
        print(f"Placed second furnace at {furnace2.position}")

        # Get the drill entities again to ensure fresh state
        drill1 = game.get_entity(Prototype.BurnerMiningDrill, drill1.position)
        drill2 = game.get_entity(Prototype.BurnerMiningDrill, drill2.position)
        drill3 = game.get_entity(Prototype.BurnerMiningDrill, drill3.position)

        # Connect drills with transport belts to create a collection line
        belts = game.connect_entities(drill1.drop_position, drill2.drop_position, Prototype.TransportBelt)
        belts = game.connect_entities(belts, drill3.drop_position, Prototype.TransportBelt)

        # Connect the collection line to both furnaces using inserters
        # Place inserter for first furnace
        inserter1 = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=furnace1.position,
            direction=Direction.DOWN,
            spacing=0
        )
        inserter1 = game.insert_item(Prototype.Coal, inserter1, quantity=1)
        print(f"Placed first inserter at {inserter1.position}")

        # Place inserter for second furnace
        inserter2 = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=furnace2.position,
            direction=Direction.DOWN,
            spacing=0
        )
        inserter2 = game.insert_item(Prototype.Coal, inserter2, quantity=1)
        print(f"Placed second inserter at {inserter2.position}")

        # Rotate input inserters to pick up from belts and insert into furnaces
        inserter1 = game.rotate_entity(inserter1, Direction.UP)
        inserter2 = game.rotate_entity(inserter2, Direction.UP)

        # Connect collection line to furnace inserters
        belts = game.connect_entities(belts, inserter2.pickup_position, Prototype.TransportBelt)
        belts = game.connect_entities(belts, inserter1.pickup_position, Prototype.TransportBelt)

        # Add output inserters for furnaces
        # First furnace output inserter
        output_inserter1 = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=furnace1_pos,  # first furnace position
            direction=Direction.UP,
            spacing=0
        )
        output_inserter1 = game.insert_item(Prototype.Coal, output_inserter1, quantity=1)
        print(f"Placed first output inserter at {output_inserter1.position}")

        # Second furnace output inserter
        output_inserter2 = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=furnace2_pos,  # second furnace position
            direction=Direction.UP,
            spacing=0
        )
        output_inserter2 = game.insert_item(Prototype.Coal, output_inserter2, quantity=1)
        print(f"Placed second output inserter at {output_inserter2.position}")

        # Place a chest to collect copper plates
        collection_chest = game.place_entity_next_to(
            Prototype.WoodenChest,
            reference_position=furnace2_pos,  # Right of second furnace
            spacing=2
        )
        print(f"Placed collection chest at {collection_chest.position}")

        # Connect output inserters to chest with belts
        belts = game.connect_entities(output_inserter1.drop_position, output_inserter2.drop_position, Prototype.TransportBelt)
        game.connect_entities(belts, collection_chest.position.right(2), Prototype.TransportBelt)

        output_inserter3 = game.place_entity_next_to(
            Prototype.BurnerInserter,
            reference_position=collection_chest.position,  # second furnace position
            direction=Direction.RIGHT,
            spacing=0
        )
        output_inserter3 = game.rotate_entity(output_inserter3, Direction.LEFT)
        output_inserter3 = game.insert_item(Prototype.Coal, output_inserter3, quantity=10)

        entities = game.get_entities()
        game.sleep(30)

        production_stats = game._production_stats()
        assert production_stats['output']['copper-plate'] > 10