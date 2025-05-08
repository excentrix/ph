from fastmcp import FastMCP, Context
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

# This module will be imported into the main MCP server
planning_tools = FastMCP("Planning Tools")

@planning_tools.tool()
async def create_semester_schedule(
    courses: List[str],
    credits_target: Optional[int] = 15,
    include_study_time: Optional[bool] = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Create a balanced semester schedule based on selected courses.
    
    Args:
        courses: List of course IDs to include in the schedule
        credits_target: Target number of credits for the semester
        include_study_time: Whether to include recommended study time blocks
        
    Returns:
        Semester schedule with course distribution and study blocks
    """
    await ctx.info("Creating semester schedule...")
    
    course_details = []
    total_credits = 0
    
    # Get details for each course
    for course_id in courses:
        course = await ctx.read_resource(f"courses://{course_id}")
        if course and course.content:
            course_details.append(course.content)
            total_credits += course.content.get("credits", 0)
    
    if not course_details:
        return {
            "success": False,
            "message": "No valid courses found",
            "schedule": None
        }
    
    # Check if the total credits match the target
    credits_message = ""
    if total_credits < credits_target:
        credits_message = f"Warning: Schedule has {total_credits} credits, below target of {credits_target}"
    elif total_credits > credits_target:
        credits_message = f"Warning: Schedule has {total_credits} credits, above target of {credits_target}"
    else:
        credits_message = f"Schedule has {total_credits} credits, meeting the target"
    
    # Use LLM to generate an optimized schedule
    courses_json = json.dumps(course_details, indent=2)
    
    prompt = f"""
    I need to create an optimized semester schedule for a student taking these courses:
    {courses_json}
    
    Total credits: {total_credits} (target: {credits_target})
    
    Please create:
    1. A weekly class schedule (which days and times would be optimal for each course)
    2. A distribution of workload throughout the week to balance difficulty
    3. {"Include study time blocks in the schedule" if include_study_time else "No study time blocks needed"}
    
    Format the response as JSON with keys:
    - weekly_schedule: Array of class meetings with day, time, course_id
    - workload_distribution: Assessment of workload by day
    - study_blocks: Recommended study blocks (if requested)
    """
    
    schedule_response = await ctx.sample(prompt)
    schedule_text = schedule_response.text.strip()
    
    # Try to parse JSON response
    try:
        schedule = json.loads(schedule_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse LLM response as JSON, using basic schedule format")
        # Fallback to a basic schedule
        days = ["Monday", "Wednesday", "Friday"]
        times = ["9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM"]
        
        # Create a simple alternating schedule
        weekly_schedule = []
        day_index = 0
        time_index = 0
        
        for course in course_details:
            course_id = course.get("id")
            weekly_schedule.append({
                "day": days[day_index % len(days)],
                "time": times[time_index % len(times)],
                "course_id": course_id,
                "course_name": course.get("name")
            })
            
            # For this simplified version, add a second day for 4-credit courses
            if course.get("credits", 0) >= 4:
                day_index = (day_index + 1) % len(days)
                weekly_schedule.append({
                    "day": days[day_index % len(days)],
                    "time": times[time_index % len(times)],
                    "course_id": course_id,
                    "course_name": course.get("name")
                })
            
            day_index = (day_index + 1) % len(days)
            time_index = (time_index + 1) % len(times)
        
        # Create basic study blocks if requested
        study_blocks = []
        if include_study_time:
            study_days = ["Tuesday", "Thursday", "Saturday"]
            for i, course in enumerate(course_details):
                study_blocks.append({
                    "day": study_days[i % len(study_days)],
                    "time": "2:00 PM",
                    "duration": "2 hours",
                    "course_id": course.get("id"),
                    "course_name": course.get("name")
                })
        
        schedule = {
            "weekly_schedule": weekly_schedule,
            "workload_distribution": {
                "Monday": "Moderate",
                "Tuesday": "Light" if include_study_time else "None",
                "Wednesday": "Moderate",
                "Thursday": "Light" if include_study_time else "None",
                "Friday": "Moderate",
                "Saturday": "Light" if include_study_time else "None",
                "Sunday": "None"
            },
            "study_blocks": study_blocks if include_study_time else []
        }
    
    return {
        "courses": course_details,
        "total_credits": total_credits,
        "credits_message": credits_message,
        "success": True,
        "schedule": schedule
    }

@planning_tools.tool()
async def plan_degree_path(
    major: str,
    current_semester: int = 1,
    completed_courses: Optional[List[str]] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Plan a degree path to graduation.
    
    Args:
        major: The student's major
        current_semester: Current semester (1-8, where 1 is first semester of freshman year)
        completed_courses: List of already completed course IDs
        
    Returns:
        Degree path with course recommendations by semester
    """
    await ctx.info(f"Planning degree path for {major} major...")
    
    # Get all available courses
    all_courses = await ctx.read_resource("courses://catalog")
    if not all_courses or not all_courses.content:
        return {
            "success": False,
            "message": "Could not retrieve course catalog",
            "path": None
        }
    
    # Convert to list if not already
    course_catalog = all_courses.content if isinstance(all_courses.content, list) else [all_courses.content]
    
    # Get department courses if possible
    try:
        dept_courses = await ctx.read_resource(f"courses://departments/{major}")
        if dept_courses and dept_courses.content:
            major_courses = dept_courses.content if isinstance(dept_courses.content, list) else [dept_courses.content]
        else:
            major_courses = []
    except Exception:
        major_courses = []
    
    # Combine courses, with major courses if available
    courses_to_consider = course_catalog if not major_courses else major_courses + course_catalog
    courses_json = json.dumps(courses_to_consider, indent=2)
    
    # Handle completed courses
    completed = completed_courses or []
    completed_json = json.dumps(completed, indent=2)
    
    # Generate degree path using LLM
    prompt = f"""
    I need to create a degree path for a student majoring in {major}.
    The student is currently in semester {current_semester} (out of 8 semesters).
    
    Available courses:
    {courses_json}
    
    Completed courses:
    {completed_json}
    
    Please create a semester-by-semester plan from the current semester to graduation.
    For each remaining semester, recommend courses that:
    1. Build on each other appropriately (prerequisites)
    2. Distribute workload evenly
    3. Complete major requirements efficiently
    
    Format as JSON with an array of semesters, each containing:
    - semester_number: Number (current_semester to 8)
    - recommended_courses: Array of course IDs
    - credits: Total credits
    - focus_areas: Key areas of study for this semester
    """
    
    path_response = await ctx.sample(prompt)
    path_text = path_response.text.strip()
    
    # Try to parse JSON response
    try:
        degree_path = json.loads(path_text)
    except json.JSONDecodeError:
        await ctx.warning("Could not parse LLM response as JSON, using basic path")
        # Fallback to a basic path
        remaining_semesters = 9 - current_semester
        degree_path = {"semesters": []}
        
        # Create simple degree path with available courses
        courses_by_dept = {}
        for course in courses_to_consider:
            dept = course.get("department", "Other")
            if dept not in courses_by_dept:
                courses_by_dept[dept] = []
            courses_by_dept[dept].append(course)
        
        # Distribute courses across remaining semesters
        major_dept_courses = courses_by_dept.get(major, [])
        general_courses = []
        for dept, dept_courses in courses_by_dept.items():
            if dept != major:
                general_courses.extend(dept_courses)
        
        # Sort by course number to approximate level
        major_dept_courses.sort(key=lambda c: c.get("id", ""))
        general_courses.sort(key=lambda c: c.get("id", ""))
        
        # Create semesters
        all_recommended = set(completed)  # Track what we've recommended already
        for i in range(remaining_semesters):
            semester_number = current_semester + i
            semester_courses = []
            credits = 0
            
            # Add major courses first
            for course in major_dept_courses:
                course_id = course.get("id")
                if course_id not in all_recommended and credits < 12:
                    semester_courses.append(course_id)
                    all_recommended.add(course_id)
                    credits += course.get("credits", 3)
            
            # Fill with general courses
            for course in general_courses:
                course_id = course.get("id")
                if course_id not in all_recommended and credits < 15:
                    semester_courses.append(course_id)
                    all_recommended.add(course_id)
                    credits += course.get("credits", 3)
            
            semester = {
                "semester_number": semester_number,
                "recommended_courses": semester_courses,
                "credits": credits,
                "focus_areas": [f"{major} fundamentals", "General education"]
            }
            
            degree_path["semesters"].append(semester)
    
    return {
        "major": major,
        "current_semester": current_semester,
        "completed_courses": completed,
        "success": True,
        "path": degree_path
    }