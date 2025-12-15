async def run_algorithms_for_round(round_id: int, n_disks: int, peg_count: int):
    """Background task to run all algorithms for a round"""
    try:
        # Run all appropriate algorithms
        results = solve_tower_of_hanoi(n_disks, peg_count)
        
        # Store results in database
        queries = []
        for result in results:
            query = """
                INSERT INTO algorithm_runs (round_id, algorithm_name, peg_count, computed_moves, runtime_ms)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                round_id,
                result.algorithm_name,
                peg_count,
                result.moves,
                result.runtime_ms
            )
            queries.append((query, params))
        
        db_manager.execute_transaction(queries)
        print(f"✅ Algorithm runs completed for round {round_id}")
        
    except Exception as e:
        print(f"❌ Error running algorithms for round {round_id}: {e}")
</content>
</invoke>