class FuzzyWashingMachineController:
    def __init__(self):
        # Define the possible input and output linguistic variables and their associated crisp values (for defuzzification)
        self.dirtiness_levels = ['low', 'mid', 'high']
        self.load_size_levels = ['small', 'mid', 'large']
        # Assign crisp values in minutes for defuzzification
        self.wash_time_levels = {'short': 10, 'medium': 30, 'long': 60} 

        # Define fuzzy rules. Each rule is a tuple: (dirtiness_antecedent, load_size_antecedent, wash_time_consequent)
        # These rules will be evaluated based on the crisp input categories.
        self.rules = [
            # Dirtiness: low
            ('low', 'small', 'short'),
            ('low', 'mid', 'short'),
            ('low', 'large', 'medium'),
            # Dirtiness: mid
            ('mid', 'small', 'medium'),
            ('mid', 'mid', 'medium'),
            ('mid', 'large', 'long'),
            # Dirtiness: high
            ('high', 'small', 'medium'),
            ('high', 'mid', 'long'),
            ('high', 'large', 'long'),
        ]

    def _fuzzify(self, dirtiness_input: str, load_size_input: str):
        """
        Fuzzifies categorical inputs by assigning full membership (1) to the matching category
        and zero membership (0) to others. Also validates inputs.
        """
        if dirtiness_input not in self.dirtiness_levels:
            raise ValueError(f"Invalid dirtiness input: '{dirtiness_input}'. Expected one of {self.dirtiness_levels}")
        if load_size_input not in self.load_size_levels:
            raise ValueError(f"Invalid load size input: '{load_size_input}'. Expected one of {self.load_size_levels}")

        fuzzified_inputs = {
            'dirtiness': {level: (1 if level == dirtiness_input else 0) for level in self.dirtiness_levels},
            'load_size': {level: (1 if level == load_size_input else 0) for level in self.load_size_levels}
        }
        return fuzzified_inputs

    def _inference(self, fuzzified_inputs):
        """
        Evaluates each fuzzy rule and determines its activation level based on fuzzified inputs.
        For AND conditions, it uses the minimum of antecedent memberships.
        For output aggregation, it uses the maximum strength for each consequent.
        """
        rule_activations = {output_level: 0 for output_level in self.wash_time_levels.keys()}

        for d_antecedent, l_antecedent, consequent in self.rules:
            dirtiness_membership = fuzzified_inputs['dirtiness'][d_antecedent]
            load_size_membership = fuzzified_inputs['load_size'][l_antecedent]
            
            # Rule strength for 'AND' logic
            rule_strength = min(dirtiness_membership, load_size_membership)
            
            # Aggregate rule strengths for each output consequent (Max for 'OR' logic across rules)
            rule_activations[consequent] = max(rule_activations[consequent], rule_strength)

        return rule_activations

    def _defuzzify(self, rule_activations):
        """
        Converts the fuzzy output (rule activations) into a crisp numerical wash time
        using a weighted average method, then maps it back to a linguistic label.
        """
        numerator = 0  # Sum of (strength * crisp_value)
        denominator = 0  # Sum of strengths

        for wash_time_level, strength in rule_activations.items():
            crisp_value = self.wash_time_levels[wash_time_level]
            numerator += strength * crisp_value
            denominator += strength
            
        if denominator == 0:
            return "Cannot determine wash time (no rules activated)."
        
        crisp_wash_time = numerator / denominator

        # Find the linguistic label closest to the calculated crisp_wash_time
        closest_label = None
        min_diff = float('inf')

        for label, value in self.wash_time_levels.items():
            diff = abs(crisp_wash_time - value)
            if diff < min_diff:
                min_diff = diff
                closest_label = label
                
        return f"{closest_label.capitalize()} ({crisp_wash_time:.1f} minutes)"

    def get_wash_time(self, dirtiness: str, load_size: str) -> str:
        """
        Calculates the recommended wash time based on dirtiness and load size.

        Args:
            dirtiness (str): The level of dirtiness ('low', 'mid', 'high').
            load_size (str): The size of the load ('small', 'mid', 'large').

        Returns:
            str: The recommended wash time (e.g., "Short (10.0 minutes)", "Medium (30.0 minutes)", "Long (60.0 minutes)").
        """
        fuzzified_inputs = self._fuzzify(dirtiness, load_size)
        rule_activations = self._inference(fuzzified_inputs)
        final_wash_time = self._defuzzify(rule_activations)
        
        return final_wash_time

# Example Usage:
if __name__ == "__main__":
    controller = FuzzyWashingMachineController()

    print("--- Washing Machine Controller Examples ---")

    # Example 1: Low dirtiness, small load
    dirtiness1 = 'low'
    load_size1 = 'small'
    wash_time1 = controller.get_wash_time(dirtiness1, load_size1)
    print(f"Dirtiness: {dirtiness1}, Load Size: {load_size1} -> Wash Time: {wash_time1}")
    # Expected: Short (10.0 minutes)

    # Example 2: High dirtiness, large load
    dirtiness2 = 'high'
    load_size2 = 'large'
    wash_time2 = controller.get_wash_time(dirtiness2, load_size2)
    print(f"Dirtiness: {dirtiness2}, Load Size: {load_size2} -> Wash Time: {wash_time2}")
    # Expected: Long (60.0 minutes)

    # Example 3: Mid dirtiness, mid load
    dirtiness3 = 'mid'
    load_size3 = 'mid'
    wash_time3 = controller.get_wash_time(dirtiness3, load_size3)
    print(f"Dirtiness: {dirtiness3}, Load Size: {load_size3} -> Wash Time: {wash_time3}")
    # Expected: Medium (30.0 minutes)

    # Example 4: Low dirtiness, large load
    dirtiness4 = 'low'
    load_size4 = 'large'
    wash_time4 = controller.get_wash_time(dirtiness4, load_size4)
    print(f"Dirtiness: {dirtiness4}, Load Size: {load_size4} -> Wash Time: {wash_time4}")
    # Expected: Medium (30.0 minutes)

    # Example 5: High dirtiness, small load
    dirtiness5 = 'high'
    load_size5 = 'small'
    wash_time5 = controller.get_wash_time(dirtiness5, load_size5)
    print(f"Dirtiness: {dirtiness5}, Load Size: {load_size5} -> Wash Time: {wash_time5}")
    # Expected: Medium (30.0 minutes)
