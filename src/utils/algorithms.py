"""
Algorithms module for Q&A Practice Application.

Implements various sorting, searching, and data structure algorithms
required for the application following SOLID principles.
"""

from typing import List, Any, Dict, Optional, Callable
from src.models.question import Question


class SortingAlgorithms:
    """
    Collection of sorting algorithms for question organization.
    
    Follows Single Responsibility principle by implementing
    only sorting operations.
    """
    
    @staticmethod
    def bubble_sort_by_difficulty(questions: List[Question]) -> List[Question]:
        """
        Sort questions by difficulty using bubble sort algorithm.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions (Easy -> Medium -> Hard)
        """
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        n = len(questions)
        sorted_questions = questions.copy()
        
        for i in range(n):
            for j in range(0, n - i - 1):
                if difficulty_order[sorted_questions[j].difficulty] > difficulty_order[sorted_questions[j + 1].difficulty]:
                    sorted_questions[j], sorted_questions[j + 1] = sorted_questions[j + 1], sorted_questions[j]
        
        return sorted_questions
    
    @staticmethod
    def selection_sort_by_topic(questions: List[Question]) -> List[Question]:
        """
        Sort questions by topic using selection sort algorithm.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions (Chemistry -> Math -> Physics)
        """
        topic_order = {'Chemistry': 0, 'Math': 1, 'Physics': 2}
        n = len(questions)
        sorted_questions = questions.copy()
        
        for i in range(n):
            min_idx = i
            for j in range(i + 1, n):
                if topic_order[sorted_questions[j].topic] < topic_order[sorted_questions[min_idx].topic]:
                    min_idx = j
            sorted_questions[i], sorted_questions[min_idx] = sorted_questions[min_idx], sorted_questions[i]
        
        return sorted_questions
    
    @staticmethod
    def insertion_sort_by_id(questions: List[Question]) -> List[Question]:
        """
        Sort questions by ID using insertion sort algorithm.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions by ID
        """
        sorted_questions = questions.copy()
        
        for i in range(1, len(sorted_questions)):
            key = sorted_questions[i]
            j = i - 1
            while j >= 0 and key.id < sorted_questions[j].id:
                sorted_questions[j + 1] = sorted_questions[j]
                j -= 1
            sorted_questions[j + 1] = key
        
        return sorted_questions
    
    @staticmethod
    def quick_sort_by_difficulty(questions: List[Question]) -> List[Question]:
        """
        Sort questions by difficulty using quick sort algorithm.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions (Easy -> Medium -> Hard)
        """
        if len(questions) <= 1:
            return questions.copy()
        
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        pivot = questions[len(questions) // 2]
        pivot_difficulty = difficulty_order[pivot.difficulty]
        
        left = [q for q in questions if difficulty_order[q.difficulty] < pivot_difficulty]
        middle = [q for q in questions if difficulty_order[q.difficulty] == pivot_difficulty]
        right = [q for q in questions if difficulty_order[q.difficulty] > pivot_difficulty]
        
        return SortingAlgorithms.quick_sort_by_difficulty(left) + middle + SortingAlgorithms.quick_sort_by_difficulty(right)
    
    @staticmethod
    def merge_sort_by_topic(questions: List[Question]) -> List[Question]:
        """
        Sort questions by topic using merge sort algorithm.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions (Chemistry -> Math -> Physics)
        """
        if len(questions) <= 1:
            return questions.copy()
        
        topic_order = {'Chemistry': 0, 'Math': 1, 'Physics': 2}
        mid = len(questions) // 2
        left = SortingAlgorithms.merge_sort_by_topic(questions[:mid])
        right = SortingAlgorithms.merge_sort_by_topic(questions[mid:])
        
        return SortingAlgorithms._merge_by_topic(left, right, topic_order)
    
    @staticmethod
    def _merge_by_topic(left: List[Question], right: List[Question], topic_order: Dict[str, int]) -> List[Question]:
        """Helper method for merge sort by topic."""
        result = []
        i = j = 0
        
        while i < len(left) and j < len(right):
            if topic_order[left[i].topic] <= topic_order[right[j].topic]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        result.extend(left[i:])
        result.extend(right[j:])
        return result
    
    @staticmethod
    def sort_by_multiple_criteria(questions: List[Question]) -> List[Question]:
        """
        Sort questions by multiple criteria: topic first, then difficulty.
        
        Args:
            questions: List of questions to sort
            
        Returns:
            Sorted list of questions by topic then difficulty
        """
        def sort_key(question: Question) -> tuple:
            topic_order = {'Chemistry': 0, 'Math': 1, 'Physics': 2}
            difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
            return (topic_order[question.topic], difficulty_order[question.difficulty])
        
        return sorted(questions, key=sort_key)
    
    @staticmethod
    def custom_sort(questions: List[Question], key_func: Callable[[Question], Any], reverse: bool = False) -> List[Question]:
        """
        Custom sort using user-provided key function.
        
        Args:
            questions: List of questions to sort
            key_func: Function to extract sort key from question
            reverse: Whether to sort in descending order
            
        Returns:
            Sorted list of questions
        """
        return sorted(questions, key=key_func, reverse=reverse)


class SearchingAlgorithms:
    """
    Collection of searching algorithms for question filtering.
    
    Follows Single Responsibility principle by implementing
    only searching operations.
    """
    
    @staticmethod
    def linear_search_by_topic(questions: List[Question], topic: str) -> List[Question]:
        """
        Search questions by topic using linear search.
        
        Args:
            questions: List of questions to search
            topic: Topic to search for
            
        Returns:
            List of questions matching the topic
        """
        return [q for q in questions if q.topic == topic]
    
    @staticmethod
    def linear_search_by_difficulty(questions: List[Question], difficulty: str) -> List[Question]:
        """
        Search questions by difficulty using linear search.
        
        Args:
            questions: List of questions to search
            difficulty: Difficulty to search for
            
        Returns:
            List of questions matching the difficulty
        """
        return [q for q in questions if q.difficulty == difficulty]
    
    @staticmethod
    def binary_search_by_id(sorted_questions: List[Question], question_id: str) -> Optional[Question]:
        """
        Search question by ID using binary search (requires sorted list).
        
        Args:
            sorted_questions: List of questions sorted by ID
            question_id: ID to search for
            
        Returns:
            Question if found, None otherwise
        """
        left, right = 0, len(sorted_questions) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_question = sorted_questions[mid]
            
            if mid_question.id == question_id:
                return mid_question
            elif mid_question.id < question_id:
                left = mid + 1
            else:
                right = mid - 1
        
        return None
    
    @staticmethod
    def search_by_text_content(questions: List[Question], search_text: str) -> List[Question]:
        """
        Search questions containing specific text in question text.
        
        Args:
            questions: List of questions to search
            search_text: Text to search for (case-insensitive)
            
        Returns:
            List of questions containing the search text
        """
        search_text_lower = search_text.lower()
        return [q for q in questions if search_text_lower in q.question_text.lower()]
    
    @staticmethod
    def search_by_multiple_criteria(questions: List[Question], topic: Optional[str] = None, 
                                  difficulty: Optional[str] = None) -> List[Question]:
        """
        Search questions by multiple criteria.
        
        Args:
            questions: List of questions to search
            topic: Optional topic filter
            difficulty: Optional difficulty filter
            
        Returns:
            Filtered list of questions
        """
        result = questions
        
        if topic:
            result = [q for q in result if q.topic == topic]
        
        if difficulty:
            result = [q for q in result if q.difficulty == difficulty]
        
        return result


class DataStructureOperations:
    """
    Collection of data structure operations for complex manipulations.
    
    Follows Single Responsibility principle by implementing
    only data structure operations.
    """
    
    @staticmethod
    def merge_sorted_lists(list1: List[Question], list2: List[Question], 
                          key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Merge two sorted lists into one sorted list.
        
        Args:
            list1: First sorted list
            list2: Second sorted list
            key_func: Function to extract comparison key
            
        Returns:
            Merged sorted list
        """
        result = []
        i = j = 0
        
        while i < len(list1) and j < len(list2):
            if key_func(list1[i]) <= key_func(list2[j]):
                result.append(list1[i])
                i += 1
            else:
                result.append(list2[j])
                j += 1
        
        result.extend(list1[i:])
        result.extend(list2[j:])
        return result

    @staticmethod
    def merge_multiple_sorted_lists(sorted_lists: List[List[Question]], 
                                   key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Merge multiple sorted lists into one sorted list.
        
        Args:
            sorted_lists: List of sorted lists
            key_func: Function to extract comparison key
            
        Returns:
            Merged sorted list
        """
        if not sorted_lists:
            return []
        
        # Use divide and conquer approach
        while len(sorted_lists) > 1:
            merged_lists = []
            for i in range(0, len(sorted_lists), 2):
                if i + 1 < len(sorted_lists):
                    merged = DataStructureOperations.merge_sorted_lists(
                        sorted_lists[i], sorted_lists[i + 1], key_func
                    )
                    merged_lists.append(merged)
                else:
                    merged_lists.append(sorted_lists[i])
            sorted_lists = merged_lists
        
        return sorted_lists[0]

    @staticmethod
    def merge_intersecting_lists(list1: List[Question], list2: List[Question]) -> List[Question]:
        """
        Merge two lists keeping only common elements (intersection).
        
        Args:
            list1: First list
            list2: Second list
            
        Returns:
            List of common elements
        """
        set2 = {q.id for q in list2}
        return [q for q in list1 if q.id in set2]

    @staticmethod
    def merge_union_lists(list1: List[Question], list2: List[Question]) -> List[Question]:
        """
        Merge two lists keeping all unique elements (union).
        
        Args:
            list1: First list
            list2: Second list
            
        Returns:
            List of unique elements from both lists
        """
        seen = set()
        result = []
        
        for q in list1 + list2:
            if q.id not in seen:
                seen.add(q.id)
                result.append(q)
        
        return result

    @staticmethod
    def merge_difference_lists(list1: List[Question], list2: List[Question]) -> List[Question]:
        """
        Merge two lists keeping only elements in first list not in second (difference).
        
        Args:
            list1: First list
            list2: Second list
            
        Returns:
            List of elements in list1 but not in list2
        """
        set2 = {q.id for q in list2}
        return [q for q in list1 if q.id not in set2]

    @staticmethod
    def merge_by_criteria(lists: List[List[Question]], 
                         merge_func: str = 'union') -> List[Question]:
        """
        Merge multiple lists using specified criteria.
        
        Args:
            lists: List of question lists to merge
            merge_func: Type of merge ('union', 'intersection', 'difference')
            
        Returns:
            Merged list based on criteria
        """
        if not lists:
            return []
        
        if merge_func == 'union':
            result = lists[0]
            for lst in lists[1:]:
                result = DataStructureOperations.merge_union_lists(result, lst)
            return result
        
        elif merge_func == 'intersection':
            result = lists[0]
            for lst in lists[1:]:
                result = DataStructureOperations.merge_intersecting_lists(result, lst)
            return result
        
        elif merge_func == 'difference':
            result = lists[0]
            for lst in lists[1:]:
                result = DataStructureOperations.merge_difference_lists(result, lst)
            return result
        
        else:
            raise ValueError(f"Unknown merge function: {merge_func}")

    @staticmethod
    def merge_sorted_with_duplicates(list1: List[Question], list2: List[Question], 
                                    key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Merge two sorted lists keeping duplicates.
        
        Args:
            list1: First sorted list
            list2: Second sorted list
            key_func: Function to extract comparison key
            
        Returns:
            Merged sorted list with duplicates preserved
        """
        result = []
        i = j = 0
        
        while i < len(list1) and j < len(list2):
            key1 = key_func(list1[i])
            key2 = key_func(list2[j])
            
            if key1 < key2:
                result.append(list1[i])
                i += 1
            elif key1 > key2:
                result.append(list2[j])
                j += 1
            else:
                # Equal keys - add both to preserve duplicates
                result.append(list1[i])
                result.append(list2[j])
                i += 1
                j += 1
        
        # Add remaining elements
        result.extend(list1[i:])
        result.extend(list2[j:])
        return result
    
    @staticmethod
    def partition_questions(questions: List[Question], 
                           partition_func: Callable[[Question], bool]) -> tuple[List[Question], List[Question]]:
        """
        Partition questions into two groups based on a predicate function.
        
        Args:
            questions: List of questions to partition
            partition_func: Function that returns True for first group, False for second
            
        Returns:
            Tuple of (first_group, second_group)
        """
        first_group = []
        second_group = []
        
        for question in questions:
            if partition_func(question):
                first_group.append(question)
            else:
                second_group.append(question)
        
        return first_group, second_group
    
    @staticmethod
    def group_questions_by_key(questions: List[Question], 
                               key_func: Callable[[Question], str]) -> Dict[str, List[Question]]:
        """
        Group questions by a key function.
        
        Args:
            questions: List of questions to group
            key_func: Function to extract group key
            
        Returns:
            Dictionary mapping keys to lists of questions
        """
        groups = {}
        
        for question in questions:
            key = key_func(question)
            if key not in groups:
                groups[key] = []
            groups[key].append(question)
        
        return groups
    
    @staticmethod
    def flatten_nested_lists(nested_lists: List[List[Question]]) -> List[Question]:
        """
        Flatten a list of lists into a single list.
        
        Args:
            nested_lists: List containing other lists of questions
            
        Returns:
            Flattened list of questions
        """
        return [question for sublist in nested_lists for question in sublist]
    
    @staticmethod
    def reverse_list(questions: List[Question]) -> List[Question]:
        """
        Reverse a list of questions.
        
        Args:
            questions: List to reverse
            
        Returns:
            Reversed list
        """
        return questions[::-1]
    
    @staticmethod
    def rotate_list(questions: List[Question], positions: int) -> List[Question]:
        """
        Rotate a list by specified number of positions.
        
        Args:
            questions: List to rotate
            positions: Number of positions to rotate (positive = right, negative = left)
            
        Returns:
            Rotated list
        """
        if not questions:
            return questions.copy()
        
        n = len(questions)
        positions = positions % n
        return questions[-positions:] + questions[:-positions]

    # Recursion for complex data structure operations
    @staticmethod
    def recursive_binary_search(questions: List[Question], target_id: str, left: int = 0, right: int = None) -> Optional[Question]:
        """
        Recursive binary search for a question by ID.
        
        Args:
            questions: Sorted list of questions
            target_id: ID to search for
            left: Left boundary (for recursion)
            right: Right boundary (for recursion)
            
        Returns:
            Question if found, None otherwise
        """
        if right is None:
            right = len(questions) - 1
        
        # Base case
        if left > right:
            return None
        
        # Recursive case
        mid = (left + right) // 2
        mid_question = questions[mid]
        
        if mid_question.id == target_id:
            return mid_question
        elif mid_question.id < target_id:
            return DataStructureOperations.recursive_binary_search(questions, target_id, mid + 1, right)
        else:
            return DataStructureOperations.recursive_binary_search(questions, target_id, left, mid - 1)

    @staticmethod
    def recursive_quick_sort(questions: List[Question], key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Recursive quick sort implementation for questions.
        
        Args:
            questions: List of questions to sort
            key_func: Function to extract comparison key
            
        Returns:
            Sorted list of questions
        """
        # Base case
        if len(questions) <= 1:
            return questions
        
        # Recursive case
        pivot = questions[0]
        pivot_key = key_func(pivot)
        
        less = [q for q in questions[1:] if key_func(q) <= pivot_key]
        greater = [q for q in questions[1:] if key_func(q) > pivot_key]
        
        # Recursively sort sublists
        sorted_less = DataStructureOperations.recursive_quick_sort(less, key_func)
        sorted_greater = DataStructureOperations.recursive_quick_sort(greater, key_func)
        
        return sorted_less + [pivot] + sorted_greater

    @staticmethod
    def recursive_merge_sort(questions: List[Question], key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Recursive merge sort implementation for questions.
        
        Args:
            questions: List of questions to sort
            key_func: Function to extract comparison key
            
        Returns:
            Sorted list of questions
        """
        # Base case
        if len(questions) <= 1:
            return questions
        
        # Recursive case - divide
        mid = len(questions) // 2
        left_half = DataStructureOperations.recursive_merge_sort(questions[:mid], key_func)
        right_half = DataStructureOperations.recursive_merge_sort(questions[mid:], key_func)
        
        # Conquer - merge sorted halves
        return DataStructureOperations._merge_recursive(left_half, right_half, key_func)

    @staticmethod
    def _merge_recursive(left: List[Question], right: List[Question], key_func: Callable[[Question], Any]) -> List[Question]:
        """
        Helper method to merge two sorted lists recursively.
        
        Args:
            left: First sorted list
            right: Second sorted list
            key_func: Function to extract comparison key
            
        Returns:
            Merged sorted list
        """
        # Base cases
        if not left:
            return right
        if not right:
            return left
        
        # Recursive case
        if key_func(left[0]) <= key_func(right[0]):
            return [left[0]] + DataStructureOperations._merge_recursive(left[1:], right, key_func)
        else:
            return [right[0]] + DataStructureOperations._merge_recursive(left, right[1:], key_func)

    @staticmethod
    def recursive_filter_questions(questions: List[Question], filter_func: Callable[[Question], bool], index: int = 0) -> List[Question]:
        """
        Recursively filter questions based on a predicate function.
        
        Args:
            questions: List of questions to filter
            filter_func: Function that returns True for questions to keep
            index: Current index (for recursion)
            
        Returns:
            Filtered list of questions
        """
        # Base case
        if index >= len(questions):
            return []
        
        # Recursive case
        current_question = questions[index]
        rest_filtered = DataStructureOperations.recursive_filter_questions(questions, filter_func, index + 1)
        
        if filter_func(current_question):
            return [current_question] + rest_filtered
        else:
            return rest_filtered

    @staticmethod
    def recursive_group_by_topic(questions: List[Question], index: int = 0) -> Dict[str, List[Question]]:
        """
        Recursively group questions by topic.
        
        Args:
            questions: List of questions to group
            index: Current index (for recursion)
            
        Returns:
            Dictionary with topics as keys and question lists as values
        """
        # Base case
        if index >= len(questions):
            return {}
        
        # Recursive case
        current_question = questions[index]
        topic = current_question.topic
        
        # Recursively group the rest
        rest_grouped = DataStructureOperations.recursive_group_by_topic(questions, index + 1)
        
        # Add current question to its topic group
        if topic not in rest_grouped:
            rest_grouped[topic] = []
        rest_grouped[topic].append(current_question)
        
        return rest_grouped

    @staticmethod
    def recursive_find_max_difficulty(questions: List[Question], index: int = 0, max_question: Optional[Question] = None) -> Optional[Question]:
        """
        Recursively find the question with maximum difficulty.
        
        Args:
            questions: List of questions to search
            index: Current index (for recursion)
            max_question: Current maximum question (for recursion)
            
        Returns:
            Question with highest difficulty
        """
        # Base case
        if index >= len(questions):
            return max_question
        
        # Recursive case
        current_question = questions[index]
        
        # Define difficulty order
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        
        # Compare difficulties
        if max_question is None:
            current_max = current_question
        else:
            if difficulty_order[current_question.difficulty] > difficulty_order[max_question.difficulty]:
                current_max = current_question
            else:
                current_max = max_question
        
        # Recursively search the rest
        return DataStructureOperations.recursive_find_max_difficulty(questions, index + 1, current_max)

    @staticmethod
    def recursive_count_by_criteria(questions: List[Question], criteria_func: Callable[[Question], bool], index: int = 0) -> int:
        """
        Recursively count questions matching criteria.
        
        Args:
            questions: List of questions to count
            criteria_func: Function that returns True for matching questions
            index: Current index (for recursion)
            
        Returns:
            Count of matching questions
        """
        # Base case
        if index >= len(questions):
            return 0
        
        # Recursive case
        current_question = questions[index]
        current_count = 1 if criteria_func(current_question) else 0
        
        # Add count from rest of list
        return current_count + DataStructureOperations.recursive_count_by_criteria(questions, criteria_func, index + 1)

    @staticmethod
    def recursive_flatten_nested_questions(nested_structure: List, index: int = 0) -> List[Question]:
        """
        Recursively flatten a nested structure of questions.
        
        Args:
            nested_structure: Nested list structure containing questions
            index: Current index (for recursion)
            
        Returns:
            Flattened list of questions
        """
        # Base case
        if index >= len(nested_structure):
            return []
        
        # Recursive case
        current_element = nested_structure[index]
        rest_flattened = DataStructureOperations.recursive_flatten_nested_questions(nested_structure, index + 1)
        
        if isinstance(current_element, list):
            # If current element is a list, recursively flatten it
            return DataStructureOperations.recursive_flatten_nested_questions(current_element) + rest_flattened
        elif isinstance(current_element, Question):
            # If current element is a question, add it
            return [current_element] + rest_flattened
        else:
            # Skip other types
            return rest_flattened

    @staticmethod
    def recursive_power_set(questions: List[Question], index: int = 0) -> List[List[Question]]:
        """
        Generate power set of questions recursively.
        
        Args:
            questions: List of questions
            index: Current index (for recursion)
            
        Returns:
            List of all possible subsets
        """
        # Base case
        if index >= len(questions):
            return [[]]
        
        # Recursive case
        current_question = questions[index]
        
        # Get power set of rest
        rest_power_set = DataStructureOperations.recursive_power_set(questions, index + 1)
        
        # Add current question to each subset in rest power set
        with_current = [[current_question] + subset for subset in rest_power_set]
        
        # Combine subsets without and with current question
        return rest_power_set + with_current
