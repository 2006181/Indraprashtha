import heapq
import random
from typing import List, Dict, Optional
from ..digital_twin.network import RailwayNetwork
from ..digital_twin.state_manager import StateManager
from ..digital_twin.train import TrainStatus
from ..digital_twin.signal import SignalAspect
from .events import SimulationEvent, EventType
from .telemetry import TelemetryGenerator, TelemetryFrame

class TrainSimulator:
    def __init__(self, network: RailwayNetwork, seed: Optional[int] = 42):
        self.network = network
        self.state_manager = StateManager(network)
        self.telemetry_gen = TelemetryGenerator(network)
        self.current_time_seconds: float = 0.0
        self.event_queue: List[SimulationEvent] = []
        self.history: List[TelemetryFrame] = []
        
        if seed is not None:
            random.seed(seed)

    def schedule_event(self, event: SimulationEvent):
        heapq.heappush(self.event_queue, event)

    def inject_delay(self, train_id: str, delay_minutes: float):
        if train_id in self.network.trains:
            t = self.network.trains[train_id]
            t.update_delay(delay_minutes)

    def inject_block_failure(self, block_id: str):
        if block_id in self.network.blocks:
            b = self.network.blocks[block_id]
            b.set_available(False)
            self.network.update_all_signals()

    def inject_signal_failure(self, signal_id: str):
        if signal_id in self.network.signals:
            s = self.network.signals[signal_id]
            s.set_functional(False)

    def inject_platform_failure(self, platform_id: str):
        for st in self.network.stations.values():
            if platform_id in st.platforms:
                st.platforms[platform_id].set_available(False)

    def step(self, time_delta_seconds: float = 10.0):
        self.current_time_seconds += time_delta_seconds

        # Process pending events for current time window
        while self.event_queue and self.event_queue[0].event_time_seconds <= self.current_time_seconds:
            ev = heapq.heappop(self.event_queue)
            self._handle_event(ev)

        # Move trains along their routes
        for train in self.network.trains.values():
            # Record telemetry frame for current step
            self.history.append(self.telemetry_gen.capture_frame(self.current_time_seconds, train.train_id))

            if train.status in (TrainStatus.SCHEDULED, TrainStatus.ARRIVED, TrainStatus.STOPPED):
                if train.status == TrainStatus.SCHEDULED:
                    # Start train if at position 0
                    if train.route:
                        start_block = train.route[0]
                        if self.network.blocks[start_block].state.value == "CLEAR":
                            self.state_manager.move_train_to_block(train.train_id, start_block)
                            train.status = TrainStatus.RUNNING
                            train.update_speed(train.max_speed)
                continue

            if train.status in (TrainStatus.RUNNING, TrainStatus.DELAYED):
                # Calculate movement distance
                dist = (train.current_speed / 3600.0) * time_delta_seconds
                train.update_position(train.position + dist)

                # Check block transitions
                curr_block = self.network.blocks.get(train.current_block_id) if train.current_block_id else None
                if curr_block:
                    # Check if train traversed current block
                    next_block_id = train.get_next_block_id()
                    if next_block_id:
                        next_block = self.network.blocks.get(next_block_id)
                        # Check associated signal aspect if any
                        sig = None
                        for s in self.network.signals.values():
                            if s.target_block_id == next_block_id:
                                sig = s
                                break
                        
                        if sig and sig.aspect == SignalAspect.RED:
                            train.update_speed(0.0)
                            train.status = TrainStatus.STOPPED
                        elif next_block and next_block.state.value == "CLEAR" and next_block.is_available:
                            # Move train to next block preserving exact distance carryover
                            if train.position >= (curr_block.length_km):
                                excess_dist = train.position - curr_block.length_km
                                self.state_manager.move_train_to_block(train.train_id, next_block_id)
                                train.position = excess_dist
                                train.update_speed(train.max_speed)
                                train.status = TrainStatus.RUNNING
                        else:
                            train.update_speed(0.0)
                            train.status = TrainStatus.STOPPED

    def _handle_event(self, ev: SimulationEvent):
        if ev.event_type == EventType.DELAY_INJECTION:
            self.inject_delay(ev.target_id, ev.payload.get("delay_minutes", 5.0))
        elif ev.event_type == EventType.BLOCK_FAILURE:
            self.inject_block_failure(ev.target_id)
        elif ev.event_type == EventType.SIGNAL_FAILURE:
            self.inject_signal_failure(ev.target_id)
        elif ev.event_type == EventType.PLATFORM_FAILURE:
            self.inject_platform_failure(ev.target_id)
