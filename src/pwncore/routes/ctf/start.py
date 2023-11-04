from __future__ import annotations

from pwncore.routes.ctf import router


@router.get("/start/{ctf_id}")
async def start_the_docker_container(ctf_id: int):       # The function name is inferred for the summary
    # This is a regular single-line comment.
    # Will not be displayed in the documentation.
    '''
    This is a multi-line comment, and will be displayed
    in the documentation when the route is expanded.

    The cool thing is that Markdown works here!
    # See, Markdown works!
    _Pretty_ **cool** right?
    '''
    return {"status": "CTF started"}
