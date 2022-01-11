#!/usr/bin/python
"""
NOTES - class for PID controller
[ATTRIBUTE]
    pid set limits tupple -> ( min , max )
"""

import time

class PID:
    def __init__(
        self, P=0.0, 
        I=0.0, 
        D=0.0,
        setPoint = 0.0, 
        output_limits = (None, None),
        current_time = None
    ):
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.sample_time = 0.00
        self.current_time = current_time if current_time is not None else time.time()
        self.last_time = self.current_time
    
        self.setPoint = setPoint
        self.min_output, self.max_output = None, None
        self.output_limits = output_limits
        self.clear()
        
    def setKValue(self, P, I, D):
        self.Kp = P
        self.Ki = I
        self.Kd = D 
        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        self.last_output = 0.0

    def update(self, feedback_value, current_time=None):
        error = self.setPoint - feedback_value

        self.current_time = current_time if current_time is not None else time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            self.Iterm = self.clamp(self.ITerm, self.output_limits)

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error
            
            output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)
            output = self.clamp(output , self.output_limits)
            
            self.last_output = output
            return output
    
    def setOutputLimits(self, limits):
        if limits is None:
            self.min_output , self.max_output = (None , None)
            return
            
        _min_output , _max_output = limits
        
        self.min_output = _min_output
        self.max_output = _max_output
        self.output_limits = self.min_output, self.max_output

    def clamp(self, value, limits):
        lower , upper = limits
        if value is None:
            return None
        if (upper is not None) and  (value > upper):
            return upper
        if (lower is not None) and  (value < lower):
            return lower
        return value        

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time
