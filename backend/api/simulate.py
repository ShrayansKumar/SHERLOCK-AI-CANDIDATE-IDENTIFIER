from fastapi import APIRouter
from meeting_simulator.simulator import run_simulation

router = APIRouter(
    prefix="/api/v1/simulate",
    tags=["Simulator"],
)


@router.post("")
@router.post("/")
@router.get("")
@router.get("/")
async def trigger_simulation(meeting_id: int = 1):
    """
    Trigger the synthetic meeting simulator.
    Runs the full pipeline (Event -> Fusion -> Postgres -> WebSocket) and returns a summary of generated events.
    """
    results = await run_simulation(meeting_id=meeting_id)
    return {
        "status": "success",
        "message": f"Simulation completed for meeting_id={meeting_id}",
        "events_processed": len(results),
        "summary": results,
    }
