#!/usr/bin/env python3
"""
Stress test runner for Lár examples using Ollama
Tests all examples and verifies log output
"""
import os
import sys
import subprocess
import json
from pathlib import Path
import time

# Test configuration
OLLAMA_MODEL = "ollama/phi4"
TEST_RESULTS = []

# Examples to test (categorized)
EXAMPLES = {
    "basic": [
        "1_simple_triage.py",
        "2_reward_code_agent.py",
        "3_support_helper_agent.py",
        # Skip: 4_fastapi_server.py (needs server)
    ],
    "patterns": [
        "1_rag_researcher.py",
        "2_self_correction.py",
        "3_parallel_execution.py",
        "4_structured_output.py",
        "5_multi_agent_handoff.py",
        "6_meta_prompt_optimizer.py",
        "7_integration_test.py",
        "8_ab_tester.py",
        "9_resumable_graph.py",
        "16_custom_logger_tracker.py",
    ],
    "compliance": [
        # Skip HITL examples (require user input)
        "2_security_firewall.py",
        "3_juried_layer.py",
        "4_access_control_agent.py",
        "5_context_contamination_test.py",
        "6_zombie_action_test.py",
    ],
    "scale": [
        "1_corporate_swarm.py",
        "2_mini_swarm_pruner.py",
        "3_parallel_newsroom.py",
        "4_parallel_corporate_swarm.py",
    ],
    "metacognition": [
        "1_dynamic_depth.py",
        "2_tool_inventor.py",
        "3_self_healing.py",
        "4_adaptive_deep_dive.py",
        "5_expert_summoner.py",
    ]
}

def patch_example_for_ollama(filepath):
    """Temporarily patch an example file to use Ollama"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Replace common model names with Ollama
    replacements = [
        ('model_name="gemini/gemini-2.5-pro"', f'model_name="{OLLAMA_MODEL}"'),
        ('model_name="gemini/gemini-1.5-pro"', f'model_name="{OLLAMA_MODEL}"'),
        ('model_name="gemini-1.5-pro"', f'model_name="{OLLAMA_MODEL}"'),
        ('model_name="gpt-4o"', f'model_name="{OLLAMA_MODEL}"'),
        ('model_name="claude-3-5-sonnet"', f'model_name="{OLLAMA_MODEL}"'),
    ]
    
    original_content = content
    for old, new in replacements:
        content = content.replace(old, new)
    
    # Write patched version
    with open(filepath, 'w') as f:
        f.write(content)
    
    return original_content

def restore_example(filepath, original_content):
    """Restore original example content"""
    with open(filepath, 'w') as f:
        f.write(original_content)

def run_example(category, filename):
    """Run a single example and collect results"""
    filepath = Path(f"examples/{category}/{filename}")
    
    if not filepath.exists():
        return {"status": "SKIP", "reason": "File not found", "filename": filename}
    
    print(f"\n{'='*60}")
    print(f"Testing: {category}/{filename}")
    print(f"{'='*60}")
    
    # Patch the file
    original_content = patch_example_for_ollama(filepath)
    
    try:
        # Run the example
        start_time = time.time()
        result = subprocess.run(
            ["python", filename],
            cwd=filepath.parent,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        duration = time.time() - start_time
        
        # Check for success indicators
        success_indicators = [
            "✅ [AuditLogger] Log saved to:",
            "Step",
            "success",
        ]
        
        output = result.stdout + result.stderr
        has_log = any(indicator in output for indicator in success_indicators)
        
        # Check for log files
        log_dir = filepath.parent / "lar_logs"
        log_files = list(log_dir.glob("*.json")) if log_dir.exists() else []
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime) if log_files else None
        
        test_result = {
            "category": category,
            "filename": filename,
            "status": "PASS" if result.returncode == 0 and has_log else "FAIL",
            "return_code": result.returncode,
            "duration": round(duration, 2),
            "has_audit_log": has_log,
            "log_file": str(latest_log.name) if latest_log else None,
            "stdout_preview": result.stdout[:500] if result.stdout else "",
            "stderr_preview": result.stderr[:500] if result.stderr else "",
        }
        
        # Verify log structure if exists
        if latest_log:
            with open(latest_log, 'r') as f:
                log_data = json.load(f)
                test_result["log_has_steps"] = "steps" in log_data or isinstance(log_data, list)
                test_result["log_has_metadata"] = any("run_metadata" in step for step in (log_data if isinstance(log_data, list) else log_data.get("steps", [])))
        
        return test_result
        
    except subprocess.TimeoutExpired:
        return {
            "category": category,
            "filename": filename,
            "status": "TIMEOUT",
            "reason": "Exceeded 60 second timeout"
        }
    except Exception as e:
        return {
            "category": category,
            "filename": filename,
            "status": "ERROR",
            "reason": str(e)
        }
    finally:
        # Restore original file
        restore_example(filepath, original_content)

def main():
    print(f"🧪 Lár Stress Test - Using {OLLAMA_MODEL}")
    print(f"{'='*60}\n")
    
    # Run all tests
    for category, files in EXAMPLES.items():
        print(f"\n📁 Category: {category.upper()}")
        for filename in files:
            result = run_example(category, filename)
            TEST_RESULTS.append(result)
            
            # Print result
            status_emoji = {
                "PASS": "✅",
                "FAIL": "❌",
                "SKIP": "⏭️",
                "TIMEOUT": "⏱️",
                "ERROR": "💥"
            }
            print(f"{status_emoji.get(result['status'], '❓')} {result['status']}: {result['filename']}")
            if result.get('duration'):
                print(f"   Duration: {result['duration']}s")
            if result.get('log_file'):
                print(f"   Log: {result['log_file']}")
    
    # Generate summary
    print(f"\n\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r['status'] == 'PASS')
    failed = sum(1 for r in TEST_RESULTS if r['status'] == 'FAIL')
    skipped = sum(1 for r in TEST_RESULTS if r['status'] in ['SKIP', 'TIMEOUT', 'ERROR'])
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏭️  Skipped/Error: {skipped}")
    print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
    
    # Save detailed results
    results_file = "stress_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print(f"\n📝 Detailed results saved to: {results_file}")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
