from fastmcp import FastMCP, Context
from typing import Dict, List, Any, Optional
import json

# This pattern will be imported into the main MCP server
career_guidance = FastMCP("Career Guidance")

@career_guidance.tool()
async def analyze_career_path(
    interests: List[str],
    skills: List[str],
    courses: Optional[List[Dict[str, Any]]] = None,
    career_goals: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Analyze potential career paths based on interests, skills, courses, and goals.
    
    Args:
        interests: List of student's interests
        skills: List of student's skills
        courses: Optional list of courses taken
        career_goals: Optional list of career goals
        
    Returns:
        Dictionary containing career path analysis and recommendations
    """
    # Log progress
    await ctx.info("Analyzing career paths based on your profile...")
    
    # Prepare data for LLM
    profile_data = {
        "interests": interests,
        "skills": skills,
        "courses": courses or [],
        "career_goals": career_goals or []
    }
    
    profile_json = json.dumps(profile_data, indent=2)
    
    # Use LLM to analyze career paths
    prompt = f"""
    I need to analyze potential career paths for a student with the following profile:
    
    {profile_json}
    
    Please provide:
    1. Top 5 potential career paths that match their interests and skills
    2. For each career path, list required skills they already have and skills they need to develop
    3. Recommended courses or certifications for each path
    4. Entry-level job titles to look for in each path
    
    Format your response as JSON with an array of career paths, each containing:
    - path_name: Name of career path
    - description: Brief description
    - existing_skills: Array of skills they already have
    - skills_to_develop: Array of skills to acquire
    - recommended_courses: Array of course/certification recommendations
    - job_titles: Array of entry-level job titles
    """
    
    # Sample from LLM
    analysis_response = await ctx.sample(prompt)
    analysis_text = analysis_response.text.strip()
    
    # Try to parse JSON response
    try:
        career_paths = json.loads(analysis_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse LLM response as JSON, falling back to structured analysis")
        # Fallback analysis
        career_paths = {
            "career_paths": [
                {
                    "path_name": "Based on your interests",
                    "description": "Please provide more specific information about your interests and skills for better recommendations",
                    "existing_skills": skills[:2] if skills else ["Not enough information"],
                    "skills_to_develop": ["Research skills", "Communication skills"],
                    "recommended_courses": ["Courses related to your interests"],
                    "job_titles": ["Entry-level positions in your field of interest"]
                }
            ]
        }
    
    # Generate action steps
    await ctx.info("Creating career development action plan...")
    
    action_plan_prompt = f"""
    Based on these career path recommendations:
    {json.dumps(career_paths, indent=2)}
    
    Create a 3-month action plan for this student to explore and prepare for these career paths.
    Include:
    1. Research activities (people to talk to, resources to explore)
    2. Skill development activities
    3. Networking opportunities
    4. Timeline with milestones
    
    Format as JSON with keys: research_activities, skill_development, networking, timeline
    """
    
    plan_response = await ctx.sample(action_plan_prompt)
    plan_text = plan_response.text.strip()
    
    # Parse action plan
    try:
        action_plan = json.loads(plan_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse action plan as JSON, using default")
        # Default action plan
        action_plan = {
            "research_activities": [
                "Research job descriptions for positions of interest",
                "Read industry publications and blogs",
                "Watch informational videos about careers of interest"
            ],
            "skill_development": [
                "Identify online courses related to desired skills",
                "Practice projects to build portfolio",
                "Join student organizations related to career interests"
            ],
            "networking": [
                "Attend university career events",
                "Connect with alumni in fields of interest",
                "Join professional groups on LinkedIn"
            ],
            "timeline": [
                {"month": 1, "focus": "Research and exploration"},
                {"month": 2, "focus": "Skill building and initial networking"},
                {"month": 3, "focus": "Applied projects and informational interviews"}
            ]
        }
    
    # Combine results
    result = {
        "career_paths": career_paths.get("career_paths", []),
        "action_plan": action_plan
    }
    
    await ctx.info("Career path analysis complete!")
    return result

@career_guidance.prompt()
def informational_interview_prompt(
    career_field: str
) -> str:
    """
    Generate questions for an informational interview in a specific career field.
    
    Args:
        career_field: The career field of interest
        
    Returns:
        List of informational interview questions
    """
    return f"""
    I'm interested in pursuing a career in {career_field} and would like to conduct
    informational interviews with professionals in this field. 
    
    Please provide me with 10 thoughtful questions I could ask during these interviews
    to gain valuable insights about the career path, day-to-day work, skills needed,
    and industry trends.
    """