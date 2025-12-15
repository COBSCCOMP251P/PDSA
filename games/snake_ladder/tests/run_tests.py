"""
Test Runner for Snake and Ladder Game
Runs all unit tests and generates a summary report
"""

import unittest
import sys
import os
from io import StringIO

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test modules
from test_game_logic import (
    TestSnakeLadderBoard,
    TestValidation,
    TestAnswerChoices,
    TestBoardEdgeCases
)

from test_pathfinding import (
    TestBFSAlgorithm,
    TestDFSAlgorithm,
    TestAlgorithmComparison,
    TestAnswerValidation,
    TestPerformance,
    TestEdgeCases
)

from test_integration import (
    TestGameFlow,
    TestBoardPersistence,
    TestAlgorithmConsistency,
    TestErrorHandling,
    TestStatisticsCalculation,
    TestAnswerChoiceGeneration
)


def run_all_tests(verbose=True):
    """
    Run all test suites and generate summary report.
    
    Args:
        verbose: Whether to show detailed output
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    print("=" * 70)
    print("SNAKE AND LADDER GAME - TEST SUITE")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Game Logic Tests
    print("Loading Game Logic Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestSnakeLadderBoard))
    suite.addTests(loader.loadTestsFromTestCase(TestValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAnswerChoices))
    suite.addTests(loader.loadTestsFromTestCase(TestBoardEdgeCases))
    
    # Pathfinding Tests
    print("Loading Pathfinding Algorithm Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestBFSAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestDFSAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestAnswerValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Integration Tests
    print("Loading Integration Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestGameFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestBoardPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticsCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestAnswerChoiceGeneration))
    
    print()
    print("=" * 70)
    print("RUNNING TESTS")
    print("=" * 70)
    print()
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print()
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
        
        if result.failures:
            print("\nFailed Tests:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        
        if result.errors:
            print("\nTests with Errors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    print("=" * 70)
    print()
    
    return result.wasSuccessful()


def run_specific_test_suite(suite_name):
    """
    Run a specific test suite.
    
    Args:
        suite_name: Name of the test suite ('game_logic', 'pathfinding', 'integration')
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if suite_name == 'game_logic':
        suite.addTests(loader.loadTestsFromTestCase(TestSnakeLadderBoard))
        suite.addTests(loader.loadTestsFromTestCase(TestValidation))
        suite.addTests(loader.loadTestsFromTestCase(TestAnswerChoices))
        suite.addTests(loader.loadTestsFromTestCase(TestBoardEdgeCases))
    
    elif suite_name == 'pathfinding':
        suite.addTests(loader.loadTestsFromTestCase(TestBFSAlgorithm))
        suite.addTests(loader.loadTestsFromTestCase(TestDFSAlgorithm))
        suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmComparison))
        suite.addTests(loader.loadTestsFromTestCase(TestAnswerValidation))
        suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
        suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    elif suite_name == 'integration':
        suite.addTests(loader.loadTestsFromTestCase(TestGameFlow))
        suite.addTests(loader.loadTestsFromTestCase(TestBoardPersistence))
        suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmConsistency))
        suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
        suite.addTests(loader.loadTestsFromTestCase(TestStatisticsCalculation))
        suite.addTests(loader.loadTestsFromTestCase(TestAnswerChoiceGeneration))
    
    else:
        print(f"Unknown test suite: {suite_name}")
        print("Available suites: game_logic, pathfinding, integration")
        return False
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Check if specific suite requested
    if len(sys.argv) > 1:
        suite_name = sys.argv[1]
        success = run_specific_test_suite(suite_name)
    else:
        success = run_all_tests(verbose=True)
    
    sys.exit(0 if success else 1)
