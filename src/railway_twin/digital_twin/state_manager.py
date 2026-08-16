from typing import Optional, Dict
from .network import RailwayNetwork

class StateManager:
    def __init__(self, network: RailwayNetwork):
        self.network = network

    def move_train_to_block(self, train_id: str, target_block_id: str) -> bool:
        if train_id not in self.network.trains:
            raise ValueError(f"Train {train_id} not registered")
        if target_block_id not in self.network.blocks:
            raise ValueError(f"Block {target_block_id} does not exist")

        train = self.network.trains[train_id]
        target_block = self.network.blocks[target_block_id]

        if not target_block.is_available:
            raise ValueError(f"Cannot move train to unavailable block {target_block_id}")

        current_block_id = train.current_block_id

        # Occupy target block (this will raise ValueError if already occupied)
        target_block.occupy(train_id)

        # Release previous block if any
        if current_block_id and current_block_id in self.network.blocks:
            self.network.blocks[current_block_id].release(train_id)

        train.set_current_block(target_block_id)
        self.network.update_all_signals()
        return True

    def get_snapshot(self) -> Dict:
        return self.network.to_dict()
