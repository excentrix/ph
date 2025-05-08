from fastmcp import FastMCP, Context
from typing import Dict, Any, List, Optional

# This module will be imported into the main MCP server
student_data = FastMCP("Student Data Resources")

@student_data.resource("student://{student_id}/profile")
async def get_student_profile(student_id: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Get a student's profile information.
    
    Args:
        student_id: The ID of the student
        
    Returns:
        Student profile data
    """
    # In a real implementation, this would query a database
    # For now, we'll return mock data
    await ctx.info(f"Retrieving profile for student {student_id}")
    
    # Mock student profiles
    profiles = {
        "1": {
            "id": "1",
            "name": "Alex Johnson",
            "major": "Computer Science",
            "year": 3,
            "gpa": 3.7,
            "interests": ["Artificial Intelligence", "Web Development", "Game Design"],
            "career_goals": ["Software Engineer", "AI Researcher"]
        },
        "2": {
            "id": "2",
            "name": "Sam Rivera",
            "major": "Biology",
            "year": 2,
            "gpa": 3.2,
            "interests": ["Genetics", "Environmental Science", "Research"],
            "career_goals": ["Medical Researcher", "Biotechnology"]
        },
        # Add more mock profiles as needed
    }
    
    # Return the profile or a default if not found
    return profiles.get(student_id, {
        "id": student_id,
        "name": "Unknown Student",
        "major": "Undeclared",
        "year": 1,
        "gpa": 0.0,
        "interests": [],
        "career_goals": []
    })

@student_data.resource("student://{student_id}/courses")
async def get_student_courses(student_id: str, ctx: Context = None) -> List[Dict[str, Any]]:
    """
    Get a student's course information.
    
    Args:
        student_id: The ID of the student
        
    Returns:
        List of course data
    """
    # In a real implementation, this would query a database
    await ctx.info(f"Retrieving courses for student {student_id}")
    
    # Mock course data by student
    courses = {
        "1": [
            {
                "id": "CS101",
                "name": "Introduction to Programming",
                "credits": 3,
                "grade": "A",
                "grade_points": 4.0,
                "semester": "Fall 2024"
            },
            {
                "id": "CS201",
                "name": "Data Structures",
                "credits": 4,
                "grade": "B+",
                "grade_points": 3.3,
                "semester": "Spring 2025"
            },
            {
                "id": "MATH240",
                "name": "Linear Algebra",
                "credits": 3,
                "grade": "B",
                "grade_points": 3.0,
                "semester": "Fall 2024"
            },
            {
                "id": "ENG101",
                "name": "College Writing",
                "credits": 3,
                "grade": "A-",
                "grade_points": 3.7,
                "semester": "Fall 2024"
            }
        ],
        "2": [
            {
                "id": "BIO101",
                "name": "Introduction to Biology",
                "credits": 4,
                "grade": "A-",
                "grade_points": 3.7,
                "semester": "Fall 2024"
            },
            {
                "id": "CHEM101",
                "name": "General Chemistry",
                "credits": 4,
                "grade": "B",
                "grade_points": 3.0,
                "semester": "Fall 2024"
            },
            {
                "id": "MATH101",
                "name": "Calculus I",
                "credits": 4,
                "grade": "C+",
                "grade_points": 2.3,
                "semester": "Spring 2025"
            }
        ]
    }
    
    # Return courses or empty list if not found
    return courses.get(student_id, [])