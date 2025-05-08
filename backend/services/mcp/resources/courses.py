from fastmcp import FastMCP, Context
from typing import Dict, Any, List, Optional

# This module will be imported into the main MCP server
courses_data = FastMCP("Course Information")
courses_data.settings.sse_path = "/mcp/courses"

@courses_data.resource("courses://catalog")
async def get_course_catalog(ctx: Context = None) -> List[Dict[str, Any]]:
    """
    Get the full course catalog.
    
    Returns:
        List of all available courses
    """
    # In a real implementation, this would query a database
    await ctx.info("Retrieving course catalog")
    
    # Mock course catalog
    return [
        {
            "id": "CS101",
            "name": "Introduction to Programming",
            "department": "Computer Science",
            "credits": 3,
            "description": "Fundamentals of programming using Python, covering basic syntax, data structures, and algorithms."
        },
        {
            "id": "CS201",
            "name": "Data Structures",
            "department": "Computer Science", 
            "credits": 4,
            "description": "Advanced data structures and algorithms, including trees, graphs, and complexity analysis."
        },
        {
            "id": "MATH240",
            "name": "Linear Algebra",
            "department": "Mathematics",
            "credits": 3,
            "description": "Vector spaces, linear transformations, matrices, determinants, eigenvalues, and applications."
        },
        {
            "id": "BIO101",
            "name": "Introduction to Biology",
            "department": "Biology",
            "credits": 4,
            "description": "Foundational concepts in biology, including cell structure, genetics, and evolution."
        },
        {
            "id": "CHEM101",
            "name": "General Chemistry",
            "department": "Chemistry",
            "credits": 4,
            "description": "Basic principles of chemistry, atomic structure, periodic table, chemical bonding, and reactions."
        }
    ]

@courses_data.resource("courses://{course_id}")
async def get_course_details(course_id: str, ctx: Context = None) -> Dict[str, Any]:
    """
    Get detailed information about a specific course.
    
    Args:
        course_id: The ID of the course
        
    Returns:
        Detailed course information
    """
    # In a real implementation, this would query a database
    await ctx.info(f"Retrieving details for course {course_id}")
    
    # Mock course details
    course_details = {
        "CS101": {
            "id": "CS101",
            "name": "Introduction to Programming",
            "department": "Computer Science",
            "credits": 3,
            "description": "Fundamentals of programming using Python, covering basic syntax, data structures, and algorithms.",
            "prerequisites": [],
            "offered_semesters": ["Fall", "Spring"],
            "syllabus_url": "https://university.edu/cs101/syllabus",
            "topics": [
                "Programming fundamentals",
                "Variables and data types",
                "Control structures",
                "Functions",
                "Basic data structures",
                "File I/O",
                "Introduction to algorithms"
            ],
            "textbooks": [
                {"title": "Python Programming: An Introduction to Computer Science", "author": "John Zelle"}
            ]
        },
        "CS201": {
            "id": "CS201",
            "name": "Data Structures",
            "department": "Computer Science",
            "credits": 4,
            "description": "Advanced data structures and algorithms, including trees, graphs, and complexity analysis.",
            "prerequisites": ["CS101"],
            "offered_semesters": ["Spring"],
            "syllabus_url": "https://university.edu/cs201/syllabus",
            "topics": [
                "Algorithm analysis",
                "Linked lists",
                "Stacks and queues",
                "Trees and binary search trees",
                "Heaps",
                "Hash tables",
                "Graphs",
                "Sorting algorithms"
            ],
            "textbooks": [
                {"title": "Data Structures and Algorithms in Python", "author": "Michael T. Goodrich"}
            ]
        }
    }
    
    # Add more courses as needed
    
    # Return course details or a default if not found
    return course_details.get(course_id, {
        "id": course_id,
        "name": "Unknown Course",
        "department": "Unknown",
        "credits": 0,
        "description": "No description available",
        "prerequisites": [],
        "offered_semesters": [],
        "topics": []
    })

@courses_data.resource("courses://departments/{department_name}")
async def get_department_courses(department_name: str, ctx: Context = None) -> List[Dict[str, Any]]:
    """
    Get courses offered by a specific department.
    
    Args:
        department_name: The name of the department
        
    Returns:
        List of courses in the department
    """
    # In a real implementation, this would query a database
    await ctx.info(f"Retrieving courses for department {department_name}")
    
    # Get all courses
    all_courses = await get_course_catalog(ctx)
    
    # Filter by department
    department_courses = [
        course for course in all_courses 
        if course.get("department", "").lower() == department_name.lower()
    ]
    
    return department_courses