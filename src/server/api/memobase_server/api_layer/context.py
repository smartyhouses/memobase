import json

from .. import controllers

from ..models.response import CODE
from ..models.utils import Promise
from ..models import response as res
from fastapi import Request
from fastapi import Path, Query


async def get_user_context(
    request: Request,
    user_id: str = Path(..., description="The ID of the user"),
    max_token_size: int = Query(
        1000,
        description="Max token size of returned Context",
    ),
    prefer_topics: list[str] = Query(
        None,
        description="Rank prefer topics at first to try to keep them in filtering, default order is by updated time",
    ),
    only_topics: list[str] = Query(
        None,
        description="Only return profiles with these topics, default is all",
    ),
    max_subtopic_size: int = Query(
        None,
        description="Max subtopic size of the same topic in returned Context",
    ),
    topic_limits_json: str = Query(
        None,
        description='Set specific subtopic limits for topics in JSON, for example {"topic1": 3, "topic2": 5}. The limits in this param will override `max_subtopic_size`.',
    ),
    profile_event_ratio: float = Query(
        0.6,
        description="Profile event ratio of returned Context",
    ),
    require_event_summary: bool = Query(
        False,
        description="Whether to require event summary in returned Context",
    ),
) -> res.UserContextDataResponse:
    project_id = request.state.memobase_project_id
    topic_limits_json = topic_limits_json or "{}"
    try:
        topic_limits = res.StrIntData(data=json.loads(topic_limits_json)).data
    except Exception as e:
        return Promise.reject(
            CODE.BAD_REQUEST, f"Invalid topic_limits JSON: {e}"
        ).to_response(res.UserContextDataResponse)
    p = await controllers.context.get_user_context(
        user_id,
        project_id,
        max_token_size,
        prefer_topics,
        only_topics,
        max_subtopic_size,
        topic_limits,
        profile_event_ratio,
        require_event_summary,
    )
    return p.to_response(res.UserContextDataResponse)
