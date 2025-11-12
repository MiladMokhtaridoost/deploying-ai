from datetime import datetime, date
from models.schema import ToolResult

def c_to_f(c: float) -> ToolResult:
    f = (c * 9/5) + 32
    return ToolResult(tool="c_to_f", result=f"{c:.2f} °C = {f:.2f} °F")

def f_to_c(f: float) -> ToolResult:
    c = (f - 32) * 5/9
    return ToolResult(tool="f_to_c", result=f"{f:.2f} °F = {c:.2f} °C")

def days_until(iso_date: str) -> ToolResult:
    try:
        target = datetime.fromisoformat(iso_date).date()
    except Exception:
        return ToolResult(tool="days_until", result="Invalid date format. Use YYYY-MM-DD.")
    today = date.today()
    delta = (target - today).days
    return ToolResult(tool="days_until", result=f"{delta} days until {iso_date}.")

