class FuzzyStudentEvaluator:
    def __init__(self):
        self.exam_score_levels = ['poor', 'avg', 'good']
        self.class_participation_levels = ['low', 'mid', 'high']
        self.assignment_quality_levels = ['low', 'mid', 'high']
        # Assign crisp values for defuzzification.
        # These represent an ordinal scale where higher value means better performance.
        self.performance_levels = {'weak': 1, 'moderate': 2, 'strong': 3}

        # Maps for numerical conversion to formulate rules more easily
        self._es_map = {'poor': 0, 'avg': 1, 'good': 2}
        self._cp_map = {'low': 0, 'mid': 1, 'high': 2}
        self._aq_map = {'low': 0, 'mid': 1, 'high': 2}
        
        # Define fuzzy rules: (exam_score, participation, assignment_quality, performance)
        self.rules = []
        
        # Weights for each input to calculate a combined "input strength"
        # These weights can be adjusted to reflect the relative importance of each factor
        weight_exam_score = 0.4
        weight_participation = 0.2
        weight_assignment_quality = 0.4

        # Generate all 3x3x3 = 27 possible rules
        for es_str in self.exam_score_levels:
            for cp_str in self.class_participation_levels:
                for aq_str in self.assignment_quality_levels:
                    # Calculate a combined "input strength"
                    input_strength = (
                        weight_exam_score * self._es_map[es_str] +
                        weight_participation * self._cp_map[cp_str] +
                        weight_assignment_quality * self._aq_map[aq_str]
                    )
                    
                    # Map combined strength to output performance linguistic term
                    # The thresholds are set based on the possible range of input_strength (0 to 2.0)
                    if input_strength >= 1.5:  # e.g., anything above a "good average"
                        performance = 'strong'
                    elif input_strength >= 0.7: # e.g., anything above a "poor average"
                        performance = 'moderate'
                    else:                       # e.g., anything below that
                        performance = 'weak'
                    
                    self.rules.append((es_str, cp_str, aq_str, performance))

    def _fuzzify(self, exam_score_input: str, participation_input: str, assignment_quality_input: str):
        """
        Fuzzifies categorical inputs by assigning full membership (1) to the matching category
        and zero membership (0) to others. Also validates inputs.
        """
        if exam_score_input not in self.exam_score_levels:
            raise ValueError(f"Invalid exam score input: '{exam_score_input}'. Expected one of {self.exam_score_levels}")
        if participation_input not in self.class_participation_levels:
            raise ValueError(f"Invalid class participation input: '{participation_input}'. Expected one of {self.class_participation_levels}")
        if assignment_quality_input not in self.assignment_quality_levels:
            raise ValueError(f"Invalid assignment quality input: '{assignment_quality_input}'. Expected one of {self.assignment_quality_levels}")

        fuzzified_inputs = {
            'exam_score': {level: (1 if level == exam_score_input else 0) for level in self.exam_score_levels},
            'participation': {level: (1 if level == participation_input else 0) for level in self.class_participation_levels},
            'assignment_quality': {level: (1 if level == assignment_quality_input else 0) for level in self.assignment_quality_levels}
        }
        return fuzzified_inputs

    def _inference(self, fuzzified_inputs):
        """
        Evaluates each fuzzy rule and determines its activation level based on fuzzified inputs.
        For AND conditions, it uses the minimum of antecedent memberships.
        For output aggregation, it uses the maximum strength for each consequent.
        """
        rule_activations = {output_level: 0 for output_level in self.performance_levels.keys()}

        for es_antecedent, cp_antecedent, aq_antecedent, consequent in self.rules:
            es_membership = fuzzified_inputs['exam_score'][es_antecedent]
            cp_membership = fuzzified_inputs['participation'][cp_antecedent]
            aq_membership = fuzzified_inputs['assignment_quality'][aq_antecedent]
            
            # Rule strength for 'AND' logic (minimum of all antecedent memberships)
            rule_strength = min(es_membership, cp_membership, aq_membership)
            
            # Aggregate rule strengths for each output consequent (Max for 'OR' logic across rules)
            rule_activations[consequent] = max(rule_activations[consequent], rule_strength)

        return rule_activations

    def _defuzzify(self, rule_activations):
        """
        Converts the fuzzy output (rule activations) into a crisp numerical performance score
        using a weighted average method, then maps it back to a linguistic label.
        """
        numerator = 0  # Sum of (strength * crisp_value)
        denominator = 0  # Sum of strengths

        for performance_level, strength in rule_activations.items():
            crisp_value = self.performance_levels[performance_level]
            numerator += strength * crisp_value
            denominator += strength
            
        if denominator == 0:
            return "Cannot determine performance (no rules activated)."
        
        crisp_performance_score = numerator / denominator

        # Find the linguistic label closest to the calculated crisp_performance_score
        closest_label = None
        min_diff = float('inf')

        for label, value in self.performance_levels.items():
            diff = abs(crisp_performance_score - value)
            if diff < min_diff:
                min_diff = diff
                closest_label = label
                
        # Return the label and the numerical score for more detail
        return f"{closest_label.capitalize()} (Score: {crisp_performance_score:.2f})"

    def evaluate_performance(self, exam_score: str, participation: str, assignment_quality: str) -> str:
        """
        Evaluates student performance based on exam score, class participation, and assignment quality.

        Args:
            exam_score (str): The exam score ('poor', 'avg', 'good').
            participation (str): The class participation ('low', 'mid', 'high').
            assignment_quality (str): The assignment quality ('low', 'mid', 'high').

        Returns:
            str: The evaluated performance (e.g., "Weak (Score: 1.00)", "Moderate (Score: 2.00)", "Strong (Score: 3.00)").
        """
        fuzzified_inputs = self._fuzzify(exam_score, participation, assignment_quality)
        rule_activations = self._inference(fuzzified_inputs)
        final_performance = self._defuzzify(rule_activations)
        
        return final_performance

# Example Usage:
if __name__ == "__main__":
    evaluator = FuzzyStudentEvaluator()

    print("--- Student Performance Evaluator Examples ---")

    # Example 1: High performance student
    exam_score1 = 'good'
    participation1 = 'high'
    assignment_quality1 = 'high'
    performance1 = evaluator.evaluate_performance(exam_score1, participation1, assignment_quality1)
    print(f"Exam: {exam_score1}, Participation: {participation1}, Assignment: {assignment_quality1} -> Performance: {performance1}")
    # Expected: Strong (Score: 3.00)

    # Example 2: Low performance student
    exam_score2 = 'poor'
    participation2 = 'low'
    assignment_quality2 = 'low'
    performance2 = evaluator.evaluate_performance(exam_score2, participation2, assignment_quality2)
    print(f"Exam: {exam_score2}, Participation: {participation2}, Assignment: {assignment_quality2} -> Performance: {performance2}")
    # Expected: Weak (Score: 1.00)

    # Example 3: Moderate performance student
    exam_score3 = 'avg'
    participation3 = 'mid'
    assignment_quality3 = 'mid'
    performance3 = evaluator.evaluate_performance(exam_score3, participation3, assignment_quality3)
    print(f"Exam: {exam_score3}, Participation: {participation3}, Assignment: {assignment_quality3} -> Performance: {performance3}")
    # Expected: Moderate (Score: 2.00)

    # Example 4: Student with good exam but low other scores
    exam_score4 = 'good'
    participation4 = 'low'
    assignment_quality4 = 'low'
    performance4 = evaluator.evaluate_performance(exam_score4, participation4, assignment_quality4)
    print(f"Exam: {exam_score4}, Participation: {participation4}, Assignment: {assignment_quality4} -> Performance: {performance4}")
    # Expected: Moderate (Score: 2.00)

    # Example 5: Student with poor exam but high other scores
    exam_score5 = 'poor'
    participation5 = 'high'
    assignment_quality5 = 'high'
    performance5 = evaluator.evaluate_performance(exam_score5, participation5, assignment_quality5)
    print(f"Exam: {exam_score5}, Participation: {participation5}, Assignment: {assignment_quality5} -> Performance: {performance5}")
    # Expected: Moderate (Score: 2.00)