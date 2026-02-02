class FuzzyTrafficController:
    def __init__(self):
        self.density_levels = ['low', 'mid', 'high']
        self.waiting_time_levels = ['short', 'mid', 'long']
        # Assign crisp values in seconds for green light duration
        self.green_light_duration_levels = {'short': 20, 'medium': 40, 'long': 60}

        # Define fuzzy rules: (density, waiting_time, green_light_duration)
        self.rules = [
            # Vehicle Density: Low
            ('low', 'short', 'short'),
            ('low', 'mid', 'short'),
            ('low', 'long', 'medium'),
            # Vehicle Density: Mid
            ('mid', 'short', 'short'),
            ('mid', 'mid', 'medium'),
            ('mid', 'long', 'long'),
            # Vehicle Density: High
            ('high', 'short', 'medium'),
            ('high', 'mid', 'long'),
            ('high', 'long', 'long'),
        ]

    def _fuzzify(self, density_input: str, waiting_time_input: str):
        """
        Fuzzifies categorical inputs by assigning full membership (1) to the matching category
        and zero membership (0) to others. Also validates inputs.
        """
        if density_input not in self.density_levels:
            raise ValueError(f"Invalid vehicle density input: '{density_input}'. Expected one of {self.density_levels}")
        if waiting_time_input not in self.waiting_time_levels:
            raise ValueError(f"Invalid waiting time input: '{waiting_time_input}'. Expected one of {self.waiting_time_levels}")

        fuzzified_inputs = {
            'density': {level: (1 if level == density_input else 0) for level in self.density_levels},
            'waiting_time': {level: (1 if level == waiting_time_input else 0) for level in self.waiting_time_levels}
        }
        return fuzzified_inputs

    def _inference(self, fuzzified_inputs):
        """
        Evaluates each fuzzy rule and determines its activation level based on fuzzified inputs.
        For AND conditions, it uses the minimum of antecedent memberships.
        For output aggregation, it uses the maximum strength for each consequent.
        """
        rule_activations = {output_level: 0 for output_level in self.green_light_duration_levels.keys()}

        for d_antecedent, w_antecedent, consequent in self.rules:
            density_membership = fuzzified_inputs['density'][d_antecedent]
            waiting_time_membership = fuzzified_inputs['waiting_time'][w_antecedent]
            
            # Rule strength for 'AND' logic
            rule_strength = min(density_membership, waiting_time_membership)
            
            # Aggregate rule strengths for each output consequent (Max for 'OR' logic across rules)
            rule_activations[consequent] = max(rule_activations[consequent], rule_strength)

        return rule_activations

    def _defuzzify(self, rule_activations):
        """
        Converts the fuzzy output (rule activations) into a crisp numerical green light duration
        using a weighted average method, then maps it back to a linguistic label.
        """
        numerator = 0  # Sum of (strength * crisp_value)
        denominator = 0  # Sum of strengths

        for duration_level, strength in rule_activations.items():
            crisp_value = self.green_light_duration_levels[duration_level]
            numerator += strength * crisp_value
            denominator += strength
            
        if denominator == 0:
            return "Cannot determine green light duration (no rules activated)."
        
        crisp_duration = numerator / denominator

        # Find the linguistic label closest to the calculated crisp_duration
        closest_label = None
        min_diff = float('inf')

        for label, value in self.green_light_duration_levels.items():
            diff = abs(crisp_duration - value)
            if diff < min_diff:
                min_diff = diff
                closest_label = label
                
        return f"{closest_label.capitalize()} ({crisp_duration:.1f} seconds)"

    def get_green_light_duration(self, density: str, waiting_time: str) -> str:
        """
        Calculates the recommended green light duration based on vehicle density and waiting time.

        Args:
            density (str): The vehicle density ('low', 'mid', 'high').
            waiting_time (str): The waiting time ('short', 'mid', 'long').

        Returns:
            str: The recommended green light duration (e.g., "Short (20.0 seconds)", "Medium (40.0 seconds)", "Long (60.0 seconds)").
        """
        fuzzified_inputs = self._fuzzify(density, waiting_time)
        rule_activations = self._inference(fuzzified_inputs)
        final_duration = self._defuzzify(rule_activations)
        
        return final_duration

# Example Usage:
if __name__ == "__main__":
    controller = FuzzyTrafficController()

    print("--- Traffic Light Controller Examples ---")

    # Example 1: Low density, short waiting time
    density1 = 'low'
    waiting_time1 = 'short'
    duration1 = controller.get_green_light_duration(density1, waiting_time1)
    print(f"Density: {density1}, Waiting Time: {waiting_time1} -> Green Light Duration: {duration1}")
    # Expected: Short (20.0 seconds)

    # Example 2: High density, long waiting time
    density2 = 'high'
    waiting_time2 = 'long'
    duration2 = controller.get_green_light_duration(density2, waiting_time2)
    print(f"Density: {density2}, Waiting Time: {waiting_time2} -> Green Light Duration: {duration2}")
    # Expected: Long (60.0 seconds)

    # Example 3: Mid density, mid waiting time
    density3 = 'mid'
    waiting_time3 = 'mid'
    duration3 = controller.get_green_light_duration(density3, waiting_time3)
    print(f"Density: {density3}, Waiting Time: {waiting_time3} -> Green Light Duration: {duration3}")
    # Expected: Medium (40.0 seconds)

    # Example 4: Low density, long waiting time
    density4 = 'low'
    waiting_time4 = 'long'
    duration4 = controller.get_green_light_duration(density4, waiting_time4)
    print(f"Density: {density4}, Waiting Time: {waiting_time4} -> Green Light Duration: {duration4}")
    # Expected: Medium (40.0 seconds)

    # Example 5: High density, short waiting time
    density5 = 'high'
    waiting_time5 = 'short'
    duration5 = controller.get_green_light_duration(density5, waiting_time5)
    print(f"Density: {density5}, Waiting Time: {waiting_time5} -> Green Light Duration: {duration5}")
    # Expected: Medium (40.0 seconds)
