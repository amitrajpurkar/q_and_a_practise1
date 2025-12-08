"""
Unit tests for algorithms module.

Tests sorting, searching, and data structure operations.
"""

import pytest
from typing import List

from src.utils.algorithms import SortingAlgorithms, SearchingAlgorithms, DataStructureOperations
from src.models.question import Question


class TestSortingAlgorithms:
    """Unit tests for sorting algorithms."""

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions for testing."""
        return [
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Hard",
                tag="Physics-Hard"
            ),
            Question(
                id="chemistry_1",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            ),
            Question(
                id="math_1",
                topic="Math",
                question_text="What is 2+2?",
                option1="3",
                option2="4",
                option3="5",
                option4="6",
                correct_answer="4",
                difficulty="Medium",
                tag="Math-Medium"
            ),
        ]

    def test_bubble_sort_by_difficulty(self, sample_questions: List[Question]) -> None:
        """Test bubble sort by difficulty."""
        sorted_questions = SortingAlgorithms.bubble_sort_by_difficulty(sample_questions)
        
        assert len(sorted_questions) == 3
        assert sorted_questions[0].difficulty == "Easy"
        assert sorted_questions[1].difficulty == "Medium"
        assert sorted_questions[2].difficulty == "Hard"

    def test_selection_sort_by_topic(self, sample_questions: List[Question]) -> None:
        """Test selection sort by topic."""
        sorted_questions = SortingAlgorithms.selection_sort_by_topic(sample_questions)
        
        assert len(sorted_questions) == 3
        assert sorted_questions[0].topic == "Chemistry"
        assert sorted_questions[1].topic == "Math"
        assert sorted_questions[2].topic == "Physics"

    def test_insertion_sort_by_id(self, sample_questions: List[Question]) -> None:
        """Test insertion sort by ID."""
        sorted_questions = SortingAlgorithms.insertion_sort_by_id(sample_questions)
        
        assert len(sorted_questions) == 3
        # IDs should be in alphabetical order
        assert sorted_questions[0].id == "chemistry_1"
        assert sorted_questions[1].id == "math_1"
        assert sorted_questions[2].id == "physics_1"

    def test_quick_sort_by_difficulty(self, sample_questions: List[Question]) -> None:
        """Test quick sort by difficulty."""
        sorted_questions = SortingAlgorithms.quick_sort_by_difficulty(sample_questions)
        
        assert len(sorted_questions) == 3
        assert sorted_questions[0].difficulty == "Easy"
        assert sorted_questions[1].difficulty == "Medium"
        assert sorted_questions[2].difficulty == "Hard"

    def test_merge_sort_by_topic(self, sample_questions: List[Question]) -> None:
        """Test merge sort by topic."""
        sorted_questions = SortingAlgorithms.merge_sort_by_topic(sample_questions)
        
        assert len(sorted_questions) == 3
        assert sorted_questions[0].topic == "Chemistry"
        assert sorted_questions[1].topic == "Math"
        assert sorted_questions[2].topic == "Physics"

    def test_sort_by_multiple_criteria(self, sample_questions: List[Question]) -> None:
        """Test sorting by multiple criteria."""
        sorted_questions = SortingAlgorithms.sort_by_multiple_criteria(sample_questions)
        
        assert len(sorted_questions) == 3
        # Should be sorted by topic first, then difficulty
        assert sorted_questions[0].topic == "Chemistry"

    def test_custom_sort(self, sample_questions: List[Question]) -> None:
        """Test custom sort with user-provided key function."""
        # Sort by question text length
        sorted_questions = SortingAlgorithms.custom_sort(
            sample_questions, 
            key_func=lambda q: len(q.question_text)
        )
        
        assert len(sorted_questions) == 3
        # Verify sorted by length (ascending)
        lengths = [len(q.question_text) for q in sorted_questions]
        assert lengths == sorted(lengths)

    def test_empty_list_sorting(self) -> None:
        """Test sorting empty list."""
        result = SortingAlgorithms.bubble_sort_by_difficulty([])
        assert result == []

    def test_single_element_sorting(self, sample_questions: List[Question]) -> None:
        """Test sorting single element list."""
        result = SortingAlgorithms.quick_sort_by_difficulty([sample_questions[0]])
        assert len(result) == 1


class TestSearchingAlgorithms:
    """Unit tests for searching algorithms."""

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions for testing."""
        return [
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="physics_2",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Medium",
                tag="Physics-Medium"
            ),
            Question(
                id="chemistry_1",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            ),
        ]

    def test_linear_search_by_topic(self, sample_questions: List[Question]) -> None:
        """Test linear search by topic."""
        result = SearchingAlgorithms.linear_search_by_topic(sample_questions, "Physics")
        
        assert len(result) == 2
        assert all(q.topic == "Physics" for q in result)

    def test_linear_search_by_difficulty(self, sample_questions: List[Question]) -> None:
        """Test linear search by difficulty."""
        result = SearchingAlgorithms.linear_search_by_difficulty(sample_questions, "Easy")
        
        assert len(result) == 2
        assert all(q.difficulty == "Easy" for q in result)

    def test_binary_search_by_id(self, sample_questions: List[Question]) -> None:
        """Test binary search by ID."""
        # Sort by ID first (required for binary search)
        sorted_questions = sorted(sample_questions, key=lambda q: q.id)
        
        result = SearchingAlgorithms.binary_search_by_id(sorted_questions, "physics_1")
        
        assert result is not None
        assert result.id == "physics_1"

    def test_binary_search_not_found(self, sample_questions: List[Question]) -> None:
        """Test binary search when ID not found."""
        sorted_questions = sorted(sample_questions, key=lambda q: q.id)
        
        result = SearchingAlgorithms.binary_search_by_id(sorted_questions, "nonexistent")
        
        assert result is None

    def test_search_by_text_content(self, sample_questions: List[Question]) -> None:
        """Test search by text content."""
        result = SearchingAlgorithms.search_by_text_content(sample_questions, "Newton")
        
        assert len(result) == 1
        assert result[0].id == "physics_1"

    def test_search_by_text_content_case_insensitive(self, sample_questions: List[Question]) -> None:
        """Test search by text content is case insensitive."""
        result = SearchingAlgorithms.search_by_text_content(sample_questions, "newton")
        
        assert len(result) == 1

    def test_search_by_multiple_criteria(self, sample_questions: List[Question]) -> None:
        """Test search by multiple criteria."""
        result = SearchingAlgorithms.search_by_multiple_criteria(
            sample_questions, 
            topic="Physics", 
            difficulty="Easy"
        )
        
        assert len(result) == 1
        assert result[0].id == "physics_1"


class TestDataStructureOperations:
    """Unit tests for data structure operations."""

    @pytest.fixture
    def sample_questions(self) -> List[Question]:
        """Create sample questions for testing."""
        return [
            Question(
                id="physics_1",
                topic="Physics",
                question_text="What is Newton's first law?",
                option1="Inertia",
                option2="F=ma",
                option3="Action-reaction",
                option4="Gravity",
                correct_answer="Inertia",
                difficulty="Easy",
                tag="Physics-Easy"
            ),
            Question(
                id="chemistry_1",
                topic="Chemistry",
                question_text="What is H2O?",
                option1="Water",
                option2="Oxygen",
                option3="Hydrogen",
                option4="Carbon",
                correct_answer="Water",
                difficulty="Easy",
                tag="Chemistry-Easy"
            ),
        ]

    @pytest.fixture
    def more_questions(self) -> List[Question]:
        """Create additional questions for testing."""
        return [
            Question(
                id="math_1",
                topic="Math",
                question_text="What is 2+2?",
                option1="3",
                option2="4",
                option3="5",
                option4="6",
                correct_answer="4",
                difficulty="Easy",
                tag="Math-Easy"
            ),
            Question(
                id="physics_2",
                topic="Physics",
                question_text="What is the speed of light?",
                option1="3x10^8 m/s",
                option2="2x10^8 m/s",
                option3="4x10^8 m/s",
                option4="1x10^8 m/s",
                correct_answer="3x10^8 m/s",
                difficulty="Hard",
                tag="Physics-Hard"
            ),
        ]

    def test_merge_union_lists(self, sample_questions: List[Question], more_questions: List[Question]) -> None:
        """Test merging lists with union."""
        result = DataStructureOperations.merge_union_lists(sample_questions, more_questions)
        
        assert len(result) == 4
        ids = {q.id for q in result}
        assert ids == {"physics_1", "chemistry_1", "math_1", "physics_2"}

    def test_merge_intersecting_lists(self, sample_questions: List[Question]) -> None:
        """Test merging lists with intersection."""
        list1 = sample_questions
        list2 = [sample_questions[0]]  # Only physics_1
        
        result = DataStructureOperations.merge_intersecting_lists(list1, list2)
        
        assert len(result) == 1
        assert result[0].id == "physics_1"

    def test_merge_difference_lists(self, sample_questions: List[Question]) -> None:
        """Test merging lists with difference."""
        list1 = sample_questions
        list2 = [sample_questions[0]]  # Only physics_1
        
        result = DataStructureOperations.merge_difference_lists(list1, list2)
        
        assert len(result) == 1
        assert result[0].id == "chemistry_1"

    def test_partition_questions(self, sample_questions: List[Question]) -> None:
        """Test partitioning questions."""
        physics, non_physics = DataStructureOperations.partition_questions(
            sample_questions,
            lambda q: q.topic == "Physics"
        )
        
        assert len(physics) == 1
        assert len(non_physics) == 1
        assert physics[0].topic == "Physics"

    def test_group_questions_by_key(self, sample_questions: List[Question], more_questions: List[Question]) -> None:
        """Test grouping questions by key."""
        all_questions = sample_questions + more_questions
        
        groups = DataStructureOperations.group_questions_by_key(
            all_questions,
            lambda q: q.topic
        )
        
        assert "Physics" in groups
        assert "Chemistry" in groups
        assert "Math" in groups
        assert len(groups["Physics"]) == 2

    def test_flatten_nested_lists(self, sample_questions: List[Question], more_questions: List[Question]) -> None:
        """Test flattening nested lists."""
        nested = [sample_questions, more_questions]
        
        result = DataStructureOperations.flatten_nested_lists(nested)
        
        assert len(result) == 4

    def test_reverse_list(self, sample_questions: List[Question]) -> None:
        """Test reversing list."""
        result = DataStructureOperations.reverse_list(sample_questions)
        
        assert len(result) == 2
        assert result[0].id == "chemistry_1"
        assert result[1].id == "physics_1"

    def test_rotate_list(self, sample_questions: List[Question]) -> None:
        """Test rotating list."""
        result = DataStructureOperations.rotate_list(sample_questions, 1)
        
        assert len(result) == 2
        assert result[0].id == "chemistry_1"

    def test_recursive_binary_search(self, sample_questions: List[Question]) -> None:
        """Test recursive binary search."""
        sorted_questions = sorted(sample_questions, key=lambda q: q.id)
        
        result = DataStructureOperations.recursive_binary_search(sorted_questions, "physics_1")
        
        assert result is not None
        assert result.id == "physics_1"

    def test_recursive_quick_sort(self, sample_questions: List[Question]) -> None:
        """Test recursive quick sort."""
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2}
        
        result = DataStructureOperations.recursive_quick_sort(
            sample_questions,
            lambda q: difficulty_order[q.difficulty]
        )
        
        assert len(result) == 2

    def test_recursive_filter_questions(self, sample_questions: List[Question]) -> None:
        """Test recursive filter."""
        result = DataStructureOperations.recursive_filter_questions(
            sample_questions,
            lambda q: q.topic == "Physics"
        )
        
        assert len(result) == 1
        assert result[0].topic == "Physics"

    def test_recursive_count_by_criteria(self, sample_questions: List[Question]) -> None:
        """Test recursive count by criteria."""
        count = DataStructureOperations.recursive_count_by_criteria(
            sample_questions,
            lambda q: q.difficulty == "Easy"
        )
        
        assert count == 2

    def test_recursive_find_max_difficulty(self, sample_questions: List[Question], more_questions: List[Question]) -> None:
        """Test finding question with max difficulty."""
        all_questions = sample_questions + more_questions
        
        result = DataStructureOperations.recursive_find_max_difficulty(all_questions)
        
        assert result is not None
        assert result.difficulty == "Hard"
