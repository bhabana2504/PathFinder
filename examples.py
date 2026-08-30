"""
End-to-End Example Usage of PathFinder AI/ML Module

This script demonstrates the complete workflow:
1. Create learner profile
2. Analyze skill gaps
3. Get recommendations (simulated RAG)
4. Generate learning path
5. Update profile with progress
6. Analyze progress
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from __init__ import (
    LearnerProfile,
    analyze_skill_gap,
    recommend_resources,
    generate_learning_path,
    update_learner_profile,
)
from sample_data import (
    SAMPLE_LEARNER_BEGINNER,
    SAMPLE_RESOURCES,
    get_sample_resources_for_skill,
)
from adaptive_learning import (
    update_skill_from_assessment,
    ProgressAnalyzer,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def example_1_basic_workflow():
    """Example 1: Basic workflow with a beginner learner."""
    print_section("EXAMPLE 1: Basic Workflow - AI Engineer Path for Beginner")
    
    # Step 1: Create learner profile
    print("1️⃣  Creating learner profile...")
    profile = LearnerProfile(
        user_id="learner_example_001",
        career_goal="AI Engineer",
        experience_level="beginner",
        current_skills=["Python"],
        skill_proficiency={"Python": 0.75},
        interests=["Machine Learning", "Deep Learning", "AI"],
        learning_hours_per_week=12.0,
        completed_resources=[],
        assessment_results={},
        feedback=[]
    )
    
    print(f"   ✓ User: {profile.user_id}")
    print(f"   ✓ Goal: {profile.career_goal}")
    print(f"   ✓ Current skills: {profile.current_skills}")
    print(f"   ✓ Available time: {profile.learning_hours_per_week} hours/week")
    
    # Step 2: Analyze skill gaps
    print("\n2️⃣  Analyzing skill gaps...")
    gap = analyze_skill_gap(profile)
    
    print(f"   ✓ Required skills: {len(gap.required_skills)}")
    print(f"   ✓ Missing skills: {gap.missing_skills[:5]}")
    print(f"   ✓ Priority skills (top 5):")
    for i, skill in enumerate(gap.priority_skills[:5], 1):
        score = gap.skill_scores.get(skill, 0)
        print(f"      {i}. {skill} (score: {score:.2f})")
    
    # Step 3: Get recommendations (using sample resources as RAG output)
    print("\n3️⃣  Getting recommendations...")
    # In real system: resources = rag_system.retrieve(gap.priority_skills)
    recommendations = recommend_resources(
        profile=profile,
        skill_gap=gap,
        resources=SAMPLE_RESOURCES,
        top_n=5
    )
    
    print(f"   ✓ Total recommendations: {recommendations.total_recommendations}")
    print(f"   ✓ Average score: {recommendations.average_score:.2f}")
    print(f"   ✓ Top 3 recommendations:")
    
    for i, rec in enumerate(recommendations.recommendations[:3], 1):
        print(f"\n      Recommendation #{i}:")
        print(f"      Title: {rec.title}")
        print(f"      Skill: {rec.primary_skill}")
        print(f"      Priority: {rec.priority}")
        print(f"      Score: {rec.score:.2f}")
        print(f"      Reason: {rec.reason[:100]}...")
        print(f"      Time needed: {rec.estimated_hours} hours")
    
    # Step 4: Generate learning path
    print("\n4️⃣  Generating personalized learning path...")
    path = generate_learning_path(
        profile=profile,
        skill_gap=gap,
        recommendations=recommendations.recommendations
    )
    
    print(f"   ✓ Path created with {len(path.nodes)} steps")
    print(f"   ✓ Learning path:")
    
    for node in path.nodes[:5]:
        status_emoji = {
            "available": "🟢",
            "locked": "🔒",
            "in_progress": "⏳",
            "completed": "✅"
        }.get(node.status, "❓")
        
        print(f"      {status_emoji} {node.position + 1}. {node.recommendation.title}")
        print(f"         Skill: {node.recommendation.primary_skill} | {node.recommendation.difficulty}")


def example_2_progress_tracking():
    """Example 2: Track progress and update recommendations."""
    print_section("EXAMPLE 2: Progress Tracking & Adaptive Recommendations")
    
    # Start with intermediate learner
    print("1️⃣  Starting with intermediate learner profile...")
    profile = LearnerProfile(
        user_id="learner_example_002",
        career_goal="Machine Learning Engineer",
        experience_level="intermediate",
        current_skills=["Python", "Statistics", "Data Analysis"],
        skill_proficiency={
            "Python": 0.80,
            "Statistics": 0.65,
            "Data Analysis": 0.70,
        },
        interests=["Machine Learning", "Deep Learning"],
        learning_hours_per_week=10.0,
        completed_resources=["python_basics_101", "stats_intro_202"],
        assessment_results={},
        feedback=["Great Python course!"]
    )
    
    print(f"   ✓ Completed resources: {len(profile.completed_resources)}")
    print(f"   ✓ Skills: {list(profile.skill_proficiency.keys())}")
    
    # Analyze initial gaps
    print("\n2️⃣  Analyzing initial skill gaps...")
    gap = analyze_skill_gap(profile)
    print(f"   ✓ Priority skills: {gap.priority_skills[:3]}")
    
    # Get initial recommendations
    print("\n3️⃣  Getting initial recommendations...")
    initial_recs = recommend_resources(profile, gap, SAMPLE_RESOURCES, top_n=3)
    print(f"   ✓ Recommendations: {[r.title for r in initial_recs.recommendations]}")
    
    # Simulate learner completing assessment
    print("\n4️⃣  Learner completes statistics assessment: 75%")
    updated_profile = update_skill_from_assessment(
        profile,
        skill="Statistics",
        assessment_score=0.75,
        weight=0.6
    )
    print(f"   ✓ Statistics proficiency updated: {profile.get_skill_proficiency('Statistics'):.2f} → {updated_profile.get_skill_proficiency('Statistics'):.2f}")
    
    # Mark resource as completed
    print("\n5️⃣  Learner completes 'Machine Learning Fundamentals'")
    updated_profile = update_learner_profile(
        updated_profile,
        completed_resources=["ml_fundamentals_404"]
    )
    print(f"   ✓ Completed resources: {len(updated_profile.completed_resources)}")
    
    # Re-analyze gaps with updated profile
    print("\n6️⃣  Re-analyzing skill gaps with updated profile...")
    new_gap = analyze_skill_gap(updated_profile)
    print(f"   ✓ Updated priority skills: {new_gap.priority_skills[:3]}")
    
    # Get updated recommendations
    print("\n7️⃣  Getting updated recommendations...")
    new_recs = recommend_resources(updated_profile, new_gap, SAMPLE_RESOURCES, top_n=3)
    print(f"   ✓ Updated recommendations:")
    for rec in new_recs.recommendations[:3]:
        print(f"      - {rec.title} ({rec.primary_skill})")
    
    # Analyze progress
    print("\n8️⃣  Analyzing learner progress...")
    analyzer = ProgressAnalyzer()
    report = analyzer.generate_progress_report(updated_profile)
    
    print(f"   ✓ Skills acquired: {report['skills_acquired']}")
    print(f"   ✓ Resources completed: {report['resources_completed']}")
    print(f"   ✓ Mastered skills: {report['mastered_skills']}")
    print(f"   ✓ Strengths: {analyzer.identify_strengths(updated_profile)}")
    print(f"   ✓ Areas to improve: {analyzer.identify_struggles(updated_profile)[:3]}")


def example_3_multiple_learners():
    """Example 3: Processing multiple learners with different paths."""
    print_section("EXAMPLE 3: Multiple Learners - Different Career Paths")
    
    learners = [
        {
            "name": "Beginner - Full Stack Developer",
            "profile": LearnerProfile(
                user_id="learner_fs_001",
                career_goal="Full Stack Developer",
                experience_level="beginner",
                current_skills=["JavaScript"],
                skill_proficiency={"JavaScript": 0.70},
                interests=["Web Development", "Frontend", "Backend"],
                learning_hours_per_week=15.0,
            )
        },
        {
            "name": "Intermediate - Data Scientist",
            "profile": LearnerProfile(
                user_id="learner_ds_001",
                career_goal="Data Scientist",
                experience_level="intermediate",
                current_skills=["Python", "SQL", "Statistics"],
                skill_proficiency={
                    "Python": 0.85,
                    "SQL": 0.75,
                    "Statistics": 0.70
                },
                interests=["Machine Learning", "Data Analysis"],
                learning_hours_per_week=12.0,
            )
        },
        {
            "name": "Advanced - DevOps Engineer",
            "profile": LearnerProfile(
                user_id="learner_devops_001",
                career_goal="DevOps Engineer",
                experience_level="advanced",
                current_skills=["Docker", "CI/CD", "Python", "Linux"],
                skill_proficiency={
                    "Docker": 0.88,
                    "CI/CD": 0.82,
                    "Python": 0.90,
                },
                interests=["Kubernetes", "Cloud", "Infrastructure"],
                learning_hours_per_week=8.0,
            )
        },
    ]
    
    results = []
    
    for learner_info in learners:
        print(f"\n📚 Processing: {learner_info['name']}")
        profile = learner_info["profile"]
        
        try:
            # Analyze gaps
            gap = analyze_skill_gap(profile)
            
            # Get recommendations
            recs = recommend_resources(profile, gap, SAMPLE_RESOURCES, top_n=3)
            
            # Generate path
            path = generate_learning_path(profile, gap, recs.recommendations)
            
            result = {
                "user_id": profile.user_id,
                "career": profile.career_goal,
                "success": True,
                "gap_count": len(gap.missing_skills),
                "priority_skills": gap.priority_skills[:3],
                "recommendations": len(recs.recommendations),
                "path_length": len(path.nodes),
            }
            
            print(f"   ✓ Success!")
            print(f"   ✓ Skill gaps: {result['gap_count']}")
            print(f"   ✓ Recommendations: {result['recommendations']}")
            print(f"   ✓ Learning path: {result['path_length']} steps")
            
        except Exception as e:
            result = {
                "user_id": profile.user_id,
                "career": profile.career_goal,
                "success": False,
                "error": str(e)
            }
            print(f"   ✗ Error: {e}")
        
        results.append(result)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY: Processed {len(results)} learners")
    print(f"  {'='*70}\n")
    
    successful = sum(1 for r in results if r["success"])
    print(f"✓ Successful: {successful}/{len(results)}")
    
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"{status} {result['user_id']}: {result['career']}")


def example_4_explanation_quality():
    """Example 4: Demonstrate recommendation explanations."""
    print_section("EXAMPLE 4: High-Quality Explanations")
    
    profile = LearnerProfile(
        user_id="learner_explain_001",
        career_goal="AI Engineer",
        experience_level="beginner",
        current_skills=["Python"],
        skill_proficiency={"Python": 0.70},
        interests=["Machine Learning", "AI", "Neural Networks"],
        learning_hours_per_week=10.0,
    )
    
    gap = analyze_skill_gap(profile)
    recs = recommend_resources(profile, gap, SAMPLE_RESOURCES, top_n=5)
    
    print("Detailed Recommendation Explanations:\n")
    
    for i, rec in enumerate(recs.recommendations[:3], 1):
        print(f"Recommendation #{i}: {rec.title}")
        print(f"Skill: {rec.primary_skill}")
        print(f"Priority: {rec.priority}")
        print(f"Score: {rec.score:.2%}")
        print(f"\nExplanation:")
        print(f"  {rec.reason}\n")
        print(f"Score Breakdown:")
        for component, score in rec.score_breakdown.items():
            bar_length = int(score * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            print(f"  {component:25} {bar} {score:.2%}")
        print()


def example_5_custom_configuration():
    """Example 5: Using custom scoring weights."""
    print_section("EXAMPLE 5: Custom Scoring Weights")
    
    from recommendation.ranker import ScoringWeights
    
    profile = SAMPLE_LEARNER_BEGINNER
    gap = analyze_skill_gap(profile)
    
    # Strategy 1: Emphasize quick wins (shorter courses)
    print("Strategy 1: Quick Wins (Emphasize Time Fit)")
    quick_wins_weights = ScoringWeights(
        skill_gap_weight=0.20,
        career_relevance_weight=0.20,
        difficulty_match_weight=0.15,
        prerequisite_match_weight=0.10,
        interest_match_weight=0.10,
        time_fit_weight=0.25,  # High emphasis on fitting schedule
    )
    
    recs_quick = recommend_resources(
        profile, gap, SAMPLE_RESOURCES, top_n=3, weights=quick_wins_weights
    )
    
    print("Top recommendations with quick wins strategy:")
    for rec in recs_quick.recommendations[:3]:
        print(f"  - {rec.title} ({rec.estimated_hours:.0f}h) - fits schedule: {rec.fits_schedule}")
    
    # Strategy 2: Comprehensive path (emphasize skill gaps)
    print("\nStrategy 2: Comprehensive Path (Emphasize Skill Gaps)")
    comprehensive_weights = ScoringWeights(
        skill_gap_weight=0.40,  # High emphasis on gaps
        career_relevance_weight=0.25,
        difficulty_match_weight=0.15,
        prerequisite_match_weight=0.10,
        interest_match_weight=0.05,
        time_fit_weight=0.05,
    )
    
    recs_comp = recommend_resources(
        profile, gap, SAMPLE_RESOURCES, top_n=3, weights=comprehensive_weights
    )
    
    print("Top recommendations with comprehensive strategy:")
    for rec in recs_comp.recommendations[:3]:
        print(f"  - {rec.title} (addresses: {rec.primary_skill})")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  PathFinder AI/ML Module - End-to-End Examples")
    print("="*70)
    
    # Run all examples
    example_1_basic_workflow()
    example_2_progress_tracking()
    example_3_multiple_learners()
    example_4_explanation_quality()
    example_5_custom_configuration()
    
    print("\n" + "="*70)
    print("  ✅ All examples completed successfully!")
    print("="*70 + "\n")
