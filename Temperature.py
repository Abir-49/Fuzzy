class FuzzyRoomTemperatureController:
    def __init__(self):
        self.temperature_levels = ['low', 'mid', 'high']
        self.humidity_levels = ['dry', 'comfortable', 'humid']
        # Assign crisp values for defuzzification.
        # These represent an ordinal scale where higher value means faster speed.
        self.fan_speed_levels = {'slow': 1, 'mid': 2, 'fast': 3}

        # Define fuzzy rules: (temperature_antecedent, humidity_antecedent, fan_speed_consequent)
        self.rules = [
            # Temperature: Low
            ('low', 'dry', 'slow'),
            ('low', 'comfortable', 'slow'),
            ('low', 'humid', 'mid'),
            # Temperature: Mid
            ('mid', 'dry', 'slow'),
            ('mid', 'comfortable', 'mid'),
            ('mid', 'humid', 'fast'),
            # Temperature: High
            ('high', 'dry', 'mid'),
            ('high', 'comfortable', 'fast'),
            ('high', 'humid', 'fast'),
        ]

    def _fuzzify(self, temperature_input: str, humidity_input: str):
        """
        Fuzzifies categorical inputs by assigning full membership (1) to the matching category
        and zero membership (0) to others. Also validates inputs.
        """
        if temperature_input not in self.temperature_levels:
            raise ValueError(f"Invalid temperature input: '{temperature_input}'. Expected one of {self.temperature_levels}")
        if humidity_input not in self.humidity_levels:
            raise ValueError(f"Invalid humidity input: '{humidity_input}'. Expected one of {self.humidity_levels}")

        fuzzified_inputs = {
            'temperature': {level: (1 if level == temperature_input else 0) for level in self.temperature_levels},
            'humidity': {level: (1 if level == humidity_input else 0) for level in self.humidity_levels}
        }
        return fuzzified_inputs

    def _inference(self, fuzzified_inputs):
        """
        Evaluates each fuzzy rule and determines its activation level based on fuzzified inputs.
        For AND conditions, it uses the minimum of antecedent memberships.
        For output aggregation, it uses the maximum strength for each consequent.
        """
        rule_activations = {output_level: 0 for output_level in self.fan_speed_levels.keys()}

        for temp_antecedent, hum_antecedent, consequent in self.rules:
            temp_membership = fuzzified_inputs['temperature'][temp_antecedent]
            hum_membership = fuzzified_inputs['humidity'][hum_antecedent]
            
            # Rule strength for 'AND' logic (minimum of all antecedent memberships)
            rule_strength = min(temp_membership, hum_membership)
            
            # Aggregate rule strengths for each output consequent (Max for 'OR' logic across rules)
            rule_activations[consequent] = max(rule_activations[consequent], rule_strength)

        return rule_activations

    def _defuzzify(self, rule_activations):
        """
        Converts the fuzzy output (rule activations) into a crisp numerical fan speed score
        using a weighted average method, then maps it back to a linguistic label.
        """
        numerator = 0  # Sum of (strength * crisp_value)
        denominator = 0  # Sum of strengths

        for fan_speed_level, strength in rule_activations.items():
            crisp_value = self.fan_speed_levels[fan_speed_level]
            numerator += strength * crisp_value
            denominator += strength
            
        if denominator == 0:
            return "Cannot determine fan speed (no rules activated)."
        
        crisp_fan_speed_score = numerator / denominator

        # Find the linguistic label closest to the calculated crisp_fan_speed_score
        closest_label = None
        min_diff = float('inf')

        for label, value in self.fan_speed_levels.items():
            diff = abs(crisp_fan_speed_score - value)
            if diff < min_diff:
                min_diff = diff
                closest_label = label
                
        # Return the label and the numerical score for more detail
        return f"{closest_label.capitalize()} (Score: {crisp_fan_speed_score:.2f})"

    def get_fan_speed(self, temperature: str, humidity: str) -> str:
        """
        Calculates the recommended fan speed based on room temperature and humidity.

        Args:
            temperature (str): The room temperature ('low', 'mid', 'high').
            humidity (str): The humidity level ('dry', 'comfortable', 'humid').

        Returns:
            str: The recommended fan speed (e.g., "Slow (Score: 1.00)", "Mid (Score: 2.00)", "Fast (Score: 3.00)").
        """
        fuzzified_inputs = self._fuzzify(temperature, humidity)
        rule_activations = self._inference(fuzzified_inputs)
        final_fan_speed = self._defuzzify(rule_activations)
        
        return final_fan_speed

# Example Usage:
if __name__ == "__main__":
    controller = FuzzyRoomTemperatureController()

    print("--- Room Temperature Controller Examples ---")

    # Example 1: Low temperature, dry humidity
    temp1 = 'low'
    hum1 = 'dry'
    speed1 = controller.get_fan_speed(temp1, hum1)
    print(f"Temperature: {temp1}, Humidity: {hum1} -> Fan Speed: {speed1}")
    # Expected: Slow (Score: 1.00)

    # Example 2: High temperature, humid humidity
    temp2 = 'high'
    hum2 = 'humid'
    speed2 = controller.get_fan_speed(temp2, hum2)
    print(f"Temperature: {temp2}, Humidity: {hum2} -> Fan Speed: {speed2}")
    # Expected: Fast (Score: 3.00)

    # Example 3: Mid temperature, comfortable humidity
    temp3 = 'mid'
    hum3 = 'comfortable'
    speed3 = controller.get_fan_speed(temp3, hum3)
    print(f"Temperature: {temp3}, Humidity: {hum3} -> Fan Speed: {speed3}")
    # Expected: Mid (Score: 2.00)

    # Example 4: Low temperature, humid humidity
    temp4 = 'low'
    hum4 = 'humid'
    speed4 = controller.get_fan_speed(temp4, hum4)
    print(f"Temperature: {temp4}, Humidity: {hum4} -> Fan Speed: {speed4}")
    # Expected: Mid (Score: 2.00)

    # Example 5: High temperature, dry humidity
    temp5 = 'high'
    hum5 = 'dry'
    speed5 = controller.get_fan_speed(temp5, hum5)
    print(f"Temperature: {temp5}, Humidity: {hum5} -> Fan Speed: {speed5}")
    # Expected: Mid (Score: 2.00)
