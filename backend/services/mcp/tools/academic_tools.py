from fastmcp import FastMCP, Context
from typing import Dict, Any, List, Optional
import json

# This module will be imported into the main MCP server
academic_tools = FastMCP("Academic Tools")

@academic_tools.tool()
async def calculate_gpa(
    courses: List[Dict[str, Any]],
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Calculate GPA based on course grades.
    
    Args:
        courses: List of course objects, each with 'credits' and 'grade_points' fields
        
    Returns:
        Dictionary with calculated GPA and credit information
    """
    await ctx.info("Calculating GPA...")
    
    if not courses:
        return {
            "gpa": 0.0,
            "total_credits": 0,
            "total_grade_points": 0.0,
            "message": "No courses provided"
        }
    
    total_credits = sum(course.get("credits", 0) for course in courses)
    total_grade_points = sum(
        course.get("credits", 0) * course.get("grade_points", 0) 
        for course in courses
    )
    
    gpa = total_grade_points / total_credits if total_credits > 0 else 0
    
    return {
        "gpa": round(gpa, 2),
        "total_credits": total_credits,
        "total_grade_points": round(total_grade_points, 2),
        "message": f"Calculated GPA from {len(courses)} courses"
    }

@academic_tools.tool()
async def generate_study_plan(
    course_id: str,
    hours_available: int,
    goals: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Generate a personalized study plan for a course.
    
    Args:
        course_id: The ID of the course
        hours_available: Hours available per week for studying
        goals: Optional list of learning goals
        
    Returns:
        Study plan with schedule and resources
    """
    await ctx.info(f"Generating study plan for course {course_id}...")
    
    # Get course details
    course = await ctx.read_resource(f"courses://{course_id}")
    
    if not course or not course.content:
        await ctx.warning(f"Course {course_id} not found")
        return {
            "course_id": course_id,
            "success": False,
            "message": "Course not found",
            "plan": None
        }
    
    course_data = course.content
    
    # Generate study plan using LLM
    goals_text = ", ".join(goals) if goals else "general mastery of the subject"
    
    prompt = f"""
    I need to create a weekly study plan for a student taking {course_data.get('name', course_id)}.
    
    Course details:
    {json.dumps(course_data, indent=2)}
    
    The student has {hours_available} hours available per week to study for this course.
    Their learning goals are: {goals_text}
    
    Please create a detailed weekly study plan that includes:
    1. How to distribute the {hours_available} hours across the week
    2. Specific study activities for each session
    3. Resources to use for each topic
    4. How to track progress
    
    Format the response as JSON with keys: weekly_schedule, study_strategies, resources, progress_tracking
    """
    
    plan_response = await ctx.sample(prompt)
    plan_text = plan_response.text.strip()
    
    # Try to parse JSON response
    try:
        study_plan = json.loads(plan_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse LLM response as JSON, using structured extraction")
        # Fallback to a basic plan
        study_plan = {
            "weekly_schedule": [
                {"day": "Monday", "duration": "1 hour", "focus": "Review last week's material"},
                {"day": "Wednesday", "duration": "1 hour", "focus": "Work on new concepts"},
                {"day": "Friday", "duration": "1 hour", "focus": "Practice problems"}
            ],
            "study_strategies": [
                "Active recall through self-testing",
                "Spaced repetition of key concepts",
                "Teaching concepts to others"
            ],
            "resources": [
                {"name": "Course textbook", "type": "Primary reading"},
                {"name": "Online tutorials", "type": "Supplementary material"}
            ],
            "progress_tracking": [
                "Weekly self-assessment quizzes",
                "Track completion of practice problems"
            ]
        }
    
    return {
        "course_id": course_id,
        "course_name": course_data.get('name', course_id),
        "hours_available": hours_available,
        "goals": goals,
        "success": True,
        "plan": study_plan
    }