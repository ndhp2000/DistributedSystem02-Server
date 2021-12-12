from network.network import ServerNetwork
from network.signal_handler import register_exit_signal
import uuid

from utils.log import GameLog

GameLog.load_config()

if __name__ == "__main__":
    register_exit_signal()
    game_network = ServerNetwork()
    try:
        while True:
            game_packet = game_network.receive()
            if game_packet['game']['type'] == '_JOIN_GAME_':
                new_id = uuid.uuid4()
                game_network.send({'type': '_JOIN_GAME_', 'instance_id': str(new_id)},
                                  game_packet['__client_address__'])
            elif game_packet['game']['type'] == '_EXAMPLE_BROADCAST_':
                game_network.broadcast(game_packet['game'])
    except SystemExit:
        game_network.safety_closed()
    print("PLEASE WAIT FOR CLEANING THREADS...")
