"""Instrument protocols and deterministic simulators."""
from typing import Protocol
import math, random

class Multimeter(Protocol):
    def measure_voltage(self)->float: ...
    def measure_current(self)->float: ...

class PowerSupply(Protocol):
    def set_output(self,voltage_v:float,current_limit_a:float)->None: ...
    def output_enabled(self)->bool: ...

class Oscilloscope(Protocol):
    def measure_frequency(self)->float: ...

class SimulatedInstruments:
    """Noise-injectable device model; it does not control physical equipment."""
    def __init__(self,voltage_v=5.0,current_a=.12,frequency_hz=1000.0,noise=0.0,seed=1):
        if noise<0: raise ValueError("noise must be non-negative")
        self.voltage,self.current,self.frequency,self.noise=voltage_v,current_a,frequency_hz,noise
        self.rng=random.Random(seed); self.enabled=False; self.limit=0.0
    def _read(self,value): return value+self.rng.gauss(0,self.noise)
    def measure_voltage(self): return self._read(self.voltage if self.enabled else 0.0)
    def measure_current(self): return self._read(self.current if self.enabled else 0.0)
    def set_output(self,voltage_v,current_limit_a):
        if not math.isfinite(voltage_v) or not math.isfinite(current_limit_a) or voltage_v<0 or current_limit_a<=0: raise ValueError("invalid supply setpoint")
        self.voltage,self.limit,self.enabled=voltage_v,current_limit_a,True
    def disable_output(self): self.enabled=False
    def output_enabled(self): return self.enabled
    def measure_frequency(self): return self._read(self.frequency)

class SerialInstrumentAdapter:
    """Example boundary only; protocol commands depend on target instrument and are intentionally unimplemented."""
    def __init__(self,port:str,baudrate:int=115200):
        self.port,self.baudrate=port,baudrate
    def connect(self):
        try: import serial
        except ImportError as exc: raise RuntimeError("install the serial extra and implement the device-specific command set") from exc
        raise NotImplementedError("physical serial protocol is device-specific and unverified")
