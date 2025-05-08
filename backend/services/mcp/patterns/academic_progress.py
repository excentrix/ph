from fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional
import json

# This pattern will be imported into the main MCP server
academic_progress = FastMCP("Academic Progress Analysis")

@academic_progress.tool()
async def analyze_academic_performance(
    courses: List[Dict[str, Any]],
    goals: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Analyze a student's academic performance and provide insights and recommendations.
    
    Args:
        courses: List of course objects with grades, credits, and other metadata
        goals: Optional academic goals the student has set
        
    Returns:
        Dictionary containing performance analysis, strengths, weaknesses, and recommendations
    """
    # Log progress
    await ctx.info("Analyzing academic performance...")
    
    # Calculate GPA and other metrics
    total_credits = sum(course.get("credits", 0) for course in courses)
    total_grade_points = sum(
        course.get("credits", 0) * course.get("grade_points", 0) 
        for course in courses
    )
    
    gpa = total_grade_points / total_credits if total_credits > 0 else 0
    
    # Use LLM to analyze strengths and weaknesses
    courses_json = json.dumps(courses, indent=2)
    goals_json = json.dumps(goals, indent=2) if goals else "{}"
    
    prompt = f"""
    I need to analyze a student's academic performance based on their courses and goals.
    
    Courses:
    {courses_json}
    
    Goals:
    {goals_json}
    
    GPA: {gpa:.2f}
    
    Please identify:
    1. Top 3 strengths based on course performance
    2. Top 3 areas for improvement
    3. 5 specific, actionable recommendations to improve academic performance
    
    Format your response as JSON with keys: strengths, weaknesses, recommendations
    """
    
    # Sample from LLM
    analysis_response = await ctx.sample(prompt)
    analysis_text = analysis_response.text.strip()
    
    # Try to parse JSON response, fall back to structured analysis if it fails
    try:
        analysis = json.loads(analysis_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse LLM response as JSON, falling back to structured analysis")
        # Fallback analysis
        analysis = {
            "strengths": [{"subject": "General", "reason": "Please check individual course grades"}],
            "weaknesses": [{"subject": "General", "reason": "Please check individual course grades"}],
            "recommendations": ["Review course materials regularly", 
                               "Connect with professors during office hours",
                               "Form study groups with classmates",
                               "Practice time management",
                               "Utilize campus resources like tutoring centers"]
        }
    
    # Report progress
    await ctx.info("Generating action plan...")
    
    # Now create an action plan based on the analysis
    action_plan_prompt = f"""
    Based on this academic analysis:
    {json.dumps(analysis, indent=2)}
    
    And student information:
    - GPA: {gpa:.2f}
    - Courses: {len(courses)} courses taken
    
    Create a weekly action plan to help the student improve. Include:
    1. Specific daily activities for a week
    2. Resources they should use (websites, books, campus services)
    3. How to measure progress
    
    Format as JSON with keys: weekly_actions, resources, progress_metrics
    """
    
    action_plan_response = await ctx.sample(action_plan_prompt)
    action_plan_text = action_plan_response.text.strip()
    
    # Parse action plan
    try:
        action_plan = json.loads(action_plan_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse action plan as JSON, using default")
        # Default action plan
        action_plan = {
            "weekly_actions": [
                {"day": "Monday", "focus": "Review", "activities": ["Review notes", "Identify weak areas"]},
                {"day": "Wednesday", "focus": "Practice", "activities": ["Complete practice problems", "Online tutorials"]},
                {"day": "Friday", "focus": "Assessment", "activities": ["Self-quiz", "Summarize learning"]}
            ],
            "resources": [
                {"name": "Khan Academy", "url": "https://www.khanacademy.org/"},
                {"name": "University Tutoring Center", "url": "Contact academic advisor for details"}
            ],
            "progress_metrics": ["Weekly self-assessment", "Course grade improvement"]
        }
    
    # Combine analysis and action plan
    result = {
        "gpa": round(gpa, 2),
        "total_credits": total_credits,
        "strengths": analysis.get("strengths", []),
        "weaknesses": analysis.get("weaknesses", []),
        "recommendations": analysis.get("recommendations", []),
        "action_plan": action_plan
    }
    
    await ctx.info("Academic analysis complete!")
    return result

@academic_progress.prompt()
def academic_improvement_prompt(
    course_name: str, 
    current_grade: str
) -> str:
    """
    Generate a prompt for improving performance in a specific course.
    
    Args:
        course_name: Name of the course
        current_grade: Current grade in the course
        
    Returns:
        Prompt for the LLM to generate improvement strategies
    """
    return f"""
    I'm currently taking {course_name} and have a grade of {current_grade}.
    What are the most effective strategies to improve my understanding and performance in this course?
    Please provide specific study techniques, resource recommendations, and a weekly study plan.
    """