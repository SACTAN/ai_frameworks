"""
Leave Management System Example using FastMCP

To run:
    cd to the examples/snippets/clients directory and run:
    uv run server leave_management stdio
"""

from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("LeaveManagementSystem")

# -----------------------------------------------
# SAMPLE DATA
# -----------------------------------------------
employees = {
    "E001": {"name": "Ravi Kumar", "leave_balance": 12, "leaves_taken": []},
    "E002": {"name": "Sneha Patel", "leave_balance": 8, "leaves_taken": []},
    "E003": {"name": "Amit Sharma", "leave_balance": 15, "leaves_taken": []},
}

# -----------------------------------------------
# TOOL 1 — Apply Leave
# -----------------------------------------------
@mcp.tool()
def apply_leave(emp_id: str, days: int, reason: str) -> str:
    """Apply for leave for a given employee"""
    if emp_id not in employees:
        return f"❌ Employee ID {emp_id} not found."

    employee = employees[emp_id]
    if days > employee["leave_balance"]:
        return f"❌ Not enough leave balance! Available: {employee['leave_balance']} days."

    # Deduct balance and store leave record
    employee["leave_balance"] -= days
    employee["leaves_taken"].append({"days": days, "reason": reason})
    return f"✅ {employee['name']} applied for {days} day(s) leave. Reason: {reason}. Remaining balance: {employee['leave_balance']} days."


# -----------------------------------------------
# TOOL 2 — Check Leave Balance
# -----------------------------------------------
@mcp.tool()
def check_balance(emp_id: str) -> str:
    """Check remaining leave balance"""
    if emp_id not in employees:
        return f"❌ Employee ID {emp_id} not found."

    employee = employees[emp_id]
    return f"🧾 {employee['name']} has {employee['leave_balance']} day(s) of leave remaining."


# -----------------------------------------------
# TOOL 3 — View Leave History
# -----------------------------------------------
@mcp.tool()
def leave_history(emp_id: str) -> str:
    """View all past leaves of an employee"""
    if emp_id not in employees:
        return f"❌ Employee ID {emp_id} not found."

    history = employees[emp_id]["leaves_taken"]
    if not history:
        return f"📘 No leave records found for {employees[emp_id]['name']}."

    lines = [f"📅 {len(history)} leave(s) taken by {employees[emp_id]['name']}:"] + [
        f" - {leave['days']} days for '{leave['reason']}'" for leave in history
    ]
    return "\n".join(lines)


# -----------------------------------------------
# RESOURCE — Employee Profile
# -----------------------------------------------
@mcp.resource("employee://{emp_id}")
def get_employee_profile(emp_id: str) -> str:
    """Get basic employee profile"""
    if emp_id not in employees:
        return f"❌ Employee ID {emp_id} not found."

    e = employees[emp_id]
    return f"👤 {e['name']} | Leave Balance: {e['leave_balance']} | Total Leaves Taken: {len(e['leaves_taken'])}"


# -----------------------------------------------
# PROMPT — Leave Approval Template
# -----------------------------------------------
@mcp.prompt()
def leave_approval_prompt(emp_name: str, days: int, reason: str) -> str:
    """Generate a leave approval message"""
    return (
        f"Dear {emp_name},\n\n"
        f"Your request for {days} day(s) leave for '{reason}' has been approved.\n"
        "Please ensure task handover before proceeding.\n\n"
        "Regards,\nHR Department"
    )

# -----------------------------------------------
# End of Script
# -----------------------------------------------
